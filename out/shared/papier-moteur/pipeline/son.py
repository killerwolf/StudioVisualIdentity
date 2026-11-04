"""Son de la chaîne : niveaux et mixage (voix + fond + générique + bruitages).

Les NIVEAUX se règlent une fois avec Hamdi (phase 3), puis les agents n'y touchent plus.
Usage : .venv/bin/python pipeline/son.py apercu   → design/phase3/apercu_short.wav et apercu_long.wav
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
A = RACINE / "assets/audio"
SR = 48000

NIVEAUX = {                 # repris d'AI Reboot : à régler une fois avec Hamdi en phase 3, puis ne plus modifier sans son accord
    "voix_rms": 0.075,      # voix normalisée (≈ −20 LUFS avant le mastering)
    "fond_short": 0.020,    # fond des Shorts, hors voix (plus présent : rythme rapide)
    "fond_long": 0.013,     # fond des vidéos longues, hors voix (discret sur 7 min)
    "sous_voix": 0.40,      # facteur appliqué au fond pendant que le narrateur parle
    "rampe": 0.25,          # durée des montées / descentes du fond (s)
    "sfx": 0.030,           # bruitages
    "generique": 0.060,     # générique (bouton + motif)
    "final_lufs": -14.0,    # norme YouTube
    "final_crete": -1.0,
}


def lire(chemin, debut=0.0, duree=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(debut)] + (["-t", str(duree)] if duree else []) + \
          ["-i", str(chemin), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)) + 1e-9)


def poser(piste, x, t, gain=1.0):
    a = int(t * SR)
    b = min(len(piste), a + len(x))
    if b > a:
        piste[a:b] += x[:b - a] * gain


def mixer(voix, fond, duree, sfx=(), generique=None, sortie=None, niveau_fond="fond_short", extraits=()):
    """voix : [(fichier, t)] ; sfx : [(fichier, t)] ; generique : t ou None ;
    extraits : [(vidéo, début source, durée, t, gain dB)] — son d'origine, au niveau de la voix, fondus doux.
    Renvoie le fichier wav masterisé."""
    n = int(duree * SR)
    pv = np.zeros(n, np.float32)
    for f, t in voix:
        x = lire(f)
        poser(pv, x / rms(x) * NIVEAUX["voix_rms"], t)
    for f, deb, d, t, gain in extraits:
        x = lire(f, deb, d)
        a, b = int(0.3 * SR), int(0.35 * SR)
        x[:a] *= np.linspace(0, 1, a)
        x[-b:] *= np.linspace(1, 0, b)
        poser(pv, x / rms(x) * NIVEAUX["voix_rms"] * 10 ** (gain / 20), t)
    if fond is None:                     # pas de musique de fond (vidéo sans fond : la chanson est ajoutée dans l'appli YouTube)
        m = np.zeros(n, np.float32)
    else:
        m = lire(fond)
        m = m / rms(m) * NIVEAUX[niveau_fond]
        m = np.tile(m, n // len(m) + 2)[:n]
    parle = (np.abs(pv) > 0.002).astype(np.float32)
    k = int(NIVEAUX["rampe"] * SR)
    env = np.clip(np.convolve(parle, np.ones(k) / k, "same") * 4, 0, 1)
    m *= 1 - (1 - NIVEAUX["sous_voix"]) * env
    m[:int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))
    m[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))
    pe = np.zeros(n, np.float32)
    for f, t in sfx:
        x = clic(f[1]) if isinstance(f, tuple) and f[0] == "clic" else lire(f)
        poser(pe, x / rms(x) * NIVEAUX["sfx"], t)
    if generique is not None:
        x = lire(A / "music/generique.mp3")
        poser(pe, x / rms(x) * NIVEAUX["generique"], generique)
    tout = (pv + m + pe).astype(np.float32)
    if np.abs(tout).max() < 1e-6:        # vidéo muette : un silence, sans mastering
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        str(sortie)], input=tout.tobytes(), check=True)
        return sortie
    mix = tout.tobytes()
    # mastering en deux passes : mesure, puis correction exacte (une seule passe reste ≈ 2 à 3 dB sous la cible)
    cible = f"I={NIVEAUX['final_lufs']}:TP={NIVEAUX['final_crete']}:LRA=11"
    entree = ["ffmpeg", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-"]
    err = subprocess.run(entree + ["-af", f"loudnorm={cible}:print_format=json", "-f", "null", "-"],
                         input=mix, capture_output=True, check=True).stderr.decode()
    import json
    m1 = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    gain = NIVEAUX["final_lufs"] - float(m1["input_i"])           # écart à la cible
    plafond = 10 ** ((NIVEAUX["final_crete"] - 0.8) / 20)         # le limiteur ne rabote que les pointes (marge true peak)
    for _ in range(3):                                            # le limiteur retire un peu de volume : on corrige
        subprocess.run(entree[:1] + ["-v", "error", "-y"] + entree[2:] +
                       ["-af", f"volume={gain:.2f}dB,alimiter=limit={plafond:.3f}:attack=5:release=60:level=false",
                        "-ar", str(SR), str(sortie)], input=mix, check=True)
        e = subprocess.run(["ffmpeg", "-nostats", "-i", str(sortie), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        obtenu = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)[-1])
        if abs(obtenu - NIVEAUX["final_lufs"]) < 0.3:
            break
        gain += NIVEAUX["final_lufs"] - obtenu
    return sortie


def clic(accent=False):
    """Clic de métronome (aperçus sans la chanson) : un temps fort plus aigu tous les 4."""
    d = int(0.05 * SR)
    t = np.arange(d) / SR
    return (np.sin(2 * np.pi * (1500 if accent else 1000) * t) * np.exp(-t * 90)).astype(np.float32)
