#!/usr/bin/env python3
"""
build_audio.py — son, assemblage, aperçu et vignette de la démo « Caméléon » (appelé par build.py).

Quatre couches, mixées ici :
- VOIX OFF : out/demo/voice_fr/NN.mp3, découpées par `split_voice()` dans le fichier unique voice_fr_raw/demo.mp3
  (Gemini « Puck »). Aucun appel réseau : on ne fait que découper. La voix cale le montage (build.VOICE).
- SON DES SHORTS : quand de vrais shorts sont à l'écran (carte qui change de style, carrousel, mur, épisodes, panneaux),
  on entend leur propre bande son (voix + musique de leur short.mp4), avec fondus, baissée sous la voix off.
- MUSIQUE : synthétisée par code (numpy/scipy, 120 BPM, la mineur), calée sur le montage.
- BRUITAGES : sons CC0 de out/demo/sfx/ (crédits : sfx/credits.json) + synthèse de out/tools/sound.py.
"""
import json, math, shutil, subprocess, sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

import __main__ as _m
B = _m if hasattr(_m, 'VOICE') else __import__('build')
sys.path.insert(0, str(B.ROOT / 'out' / 'tools'))
import sound as SND  # noqa: E402

SR = 48000
HERE = Path(__file__).resolve().parent
SFX = HERE / 'sfx'
BEAT = 0.5


# ------------------------------------------------------------------ outils
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'high')
    return signal.lfilter(b, a, x, axis=0)


def tax(d):
    return np.arange(int(d * SR)) / SR


def st(y):
    return y if y.ndim == 2 else np.stack([y, y], 1)


class Track:
    def __init__(self, dur):
        self.x = np.zeros((int(dur * SR) + 2 * SR, 2))

    def add(self, y, t, g=1.0, pan=0.0):
        i = int(round(t * SR))
        if i < 0:
            y = y[-i:]
            i = 0
        n = min(len(y), len(self.x) - i)
        if n <= 0:
            return
        l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
        if y.ndim == 1:
            self.x[i:i + n, 0] += y[:n] * g * l
            self.x[i:i + n, 1] += y[:n] * g * r
        else:
            self.x[i:i + n, 0] += y[:n, 0] * g * l
            self.x[i:i + n, 1] += y[:n, 1] * g * r


def kick():
    t = tax(0.34)
    f = 46 + 150 * np.exp(-t * 34)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    click = hp(np.random.default_rng(1).uniform(-1, 1, len(t)), 3000) * np.exp(-t * 300) * 0.25
    return np.tanh((y + click) * 1.6)


def subdrop(d=1.1):
    """Chute de basse : le « boum » sous les gros impacts."""
    t = tax(d)
    f = 34 + 70 * np.exp(-t * 5)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.5) * np.exp(-t * 3.2) * np.minimum(1, t * 200)


def hat(d=0.05, seed=2, dec=70):
    t = tax(d)
    return hp(np.random.default_rng(seed).uniform(-1, 1, len(t)), 7500) * np.exp(-t * dec)


def crash(d=1.6):
    t = tax(d)
    n = np.random.default_rng(8).uniform(-1, 1, len(t))
    return hp(n, 4500) * np.exp(-t * 3.2) * np.minimum(1, t * 400)


def clap():
    t = tax(0.22)
    n = np.random.default_rng(5).uniform(-1, 1, len(t))
    b, a = signal.butter(2, [900 / (SR / 2), 4200 / (SR / 2)], 'band')
    env = sum(np.exp(-np.clip(t - d, 0, None) * 38) * (t >= d) for d in (0, 0.011, 0.023)) / 2
    return signal.lfilter(b, a, n) * env


def bass(m, d):
    t = tax(d)
    f = hz(m)
    y = signal.sawtooth(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * f * t)
    y = lp(y, 520)
    return y * np.minimum(1, t * 300) * np.exp(-t * 3.5) * np.minimum(1, (d - t) * 60)


def pluck(m, d=0.3, bright=2600):
    t = tax(d)
    f = hz(m)
    y = signal.sawtooth(2 * np.pi * f * t, 0.5) * 0.5 + signal.square(2 * np.pi * f * t) * 0.25 + np.sin(2 * np.pi * 2 * f * t) * 0.2
    y = lp(y, bright)
    return y * np.minimum(1, t * 500) * np.exp(-t * 11)


def pad(notes, d, cut=1500):
    t = tax(d)
    y = sum(signal.sawtooth(2 * np.pi * hz(m) * (1 + dt) * t) for m in notes for dt in (-0.004, 0.003, 0.0)) / (3 * len(notes))
    y = lp(y, cut)
    return y * np.minimum(1, t * 6) * np.minimum(1, (d - t) * 4)


def stab(notes, d=0.22):
    t = tax(d)
    y = sum(signal.sawtooth(2 * np.pi * hz(m) * (1 + dt) * t) for m in notes for dt in (-0.005, 0.005)) / (2 * len(notes))
    return lp(y, 3200) * np.minimum(1, t * 400) * np.exp(-t * 13)


def noise_riser(d):
    """Montée de bruit filtré (balayage passe-haut), pour amener une révélation."""
    t = tax(d)
    n = np.random.default_rng(21).uniform(-1, 1, len(t))
    out = np.zeros_like(n)
    blk = 1024
    for i in range(0, len(n), blk):
        x = i / len(n)
        b, a = signal.butter(2, [(300 + 5000 * x ** 2) / (SR / 2), min(0.98, (1500 + 14000 * x ** 1.5) / (SR / 2))], 'band')
        out[i:i + blk] = signal.lfilter(b, a, n[i:i + blk])
    return out * (t / d) ** 2.2


def load(name):
    sr, y = wavfile.read(SFX / f'{name}.wav')
    y = y.astype(np.float64) / (32768.0 if y.dtype == np.int16 else (np.abs(y).max() or 1))
    y = st(y)
    pk = np.abs(y).max()
    return y / pk if pk else y


def pitch(y, ratio):
    n = int(len(y) / ratio)
    idx = np.linspace(0, len(y) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(y)), y[:, c]) for c in range(y.shape[1])], 1)


def decode(path, ss=None, dur=None, ch=1):
    cmd = ['ffmpeg', '-loglevel', 'error']
    if ss is not None:
        cmd += ['-ss', f'{max(0, ss):.3f}', '-t', f'{dur:.3f}']
    cmd += ['-i', str(path), '-vn', '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-']
    y = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).astype(np.float64)
    return y.reshape(-1, 2) if ch == 2 else y


def smooth_env(x, attack=0.05, release=0.25):
    """Enveloppe 0..1 lissée (montée rapide, descente lente) à partir d'un signal de présence."""
    k = int(release * SR)
    e = signal.fftconvolve(x, np.ones(k) / k, 'same')
    e = np.clip(e * 3, 0, 1)
    b, a = signal.butter(1, 1 / (attack * 2 * np.pi) / (SR / 2))
    return np.clip(signal.filtfilt(b, a, e), 0, 1)


CH = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]  # Am F C G (basse, accord)


# ------------------------------------------------------------------ voix off
def split_voice():
    """Découpe voice_fr_raw/demo.mp3 en une ligne par fichier (voice_fr/NN.mp3), pauses internes recalées sur le montage."""
    raw = HERE / 'voice_fr_raw' / 'demo.mp3'
    y = decode(raw)
    g = 0.9 / np.abs(y).max()
    out = HERE / 'voice_fr'
    out.mkdir(exist_ok=True)
    f = int(0.008 * SR)
    for k, (txt, chunks) in enumerate(B.VOICE):
        t0 = chunks[0][2]
        end = chunks[-1][2] + (chunks[-1][1] - chunks[-1][0]) + 0.12
        buf = np.zeros(int((end - t0) * SR))
        for a, b, tv in chunks:
            seg = y[int((a - 0.03) * SR):int((b + 0.07) * SR)].copy() * g
            seg[:f] *= np.linspace(0, 1, f)
            seg[-f:] *= np.linspace(1, 0, f)
            i = max(0, int((tv - 0.03 - t0) * SR))
            n = min(len(seg), len(buf) - i)
            buf[i:i + n] += seg[:n]
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '128k',
                        str(out / f'{k:02d}.mp3')], input=buf.astype(np.float32).tobytes(), check=True)
        print(f'{k:02d}.mp3  {t0:5.2f} -> {end - 0.12:5.2f} s  {txt}')


def voice_files():
    d = HERE / 'voice_fr'
    fs = [d / f'{k:02d}.mp3' for k in range(len(B.NARRATION))]
    return fs if all(f.exists() for f in fs) else None


def voice_track(n):
    vf = voice_files()
    if not vf:
        return None
    v = np.zeros(n)
    for (t0, t1, _), f in zip(B.NARRATION, vf):
        y = decode(f)
        i = int(t0 * SR)
        m = min(len(y), n - i)
        v[i:i + m] += y[:m]
    v = hp(v, 85)
    v = np.tanh(v * 1.5) / np.tanh(1.5)        # un peu de compression : voix de bande-annonce, bien devant
    return v


# ------------------------------------------------------------------ le son des shorts à l'écran
_gain = {}


def short_gain(short):
    """Gain qui ramène chaque short au même niveau moyen (mesuré sur 8 s)."""
    if short not in _gain:
        y = decode(B.SHORTS / short / 'short.mp4', 1.0, 8.0)
        _gain[short] = 0.09 / (np.sqrt((y ** 2).mean()) + 1e-6)
    return _gain[short]


def shorts_layer():
    D = B.DUR
    tr = Track(D)
    log = []

    def seg(short, src, t0, t1, g=1.0, pan=0.0, fi=0.08, fo=0.08, what=''):
        d = t1 - t0
        if d <= 0.02:
            return
        y = decode(B.SHORTS / short / 'short.mp4', src, d, ch=2) * short_gain(short)
        n = len(y)
        if n < 10:
            return
        e = np.minimum(1, np.arange(n) / max(1, fi * SR)) * np.minimum(1, (n - np.arange(n)) / max(1, fo * SR))
        tr.add(y * e[:, None], t0, g, pan)
        log.append({'t0': round(t0, 2), 't1': round(t1, 2), 'short': short, 'from': round(src, 2), 'gain': g, 'what': what})

    ids = B.IDS
    # 1. la carte qui change de style : un zapping d'un quart de seconde par style
    for k, name in enumerate(B.MUTANTS):
        r = ids[B.IDX[name]]
        t0 = B.T_MUT + 0.25 * k
        seg(r[2], r[3] + 2.0 + 0.25 * k, t0, t0 + 0.25, 0.55, 0, 0.02, 0.03, 'zapping')
    # 2. carrousel : on entend le short de la carte du centre (même horloge que l'image)
    t_first = B.T_MUT + 0.25 * len(B.MUTANTS)
    seg(ids[0][2], ids[0][3], t_first, B.COV_T[1] + 0.05, 0.75, 0, 0.03, 0.08, 'carrousel')
    for k in range(1, B.N):
        t0 = B.COV_T[k]
        t1 = (B.COV_T[k + 1] if k + 1 < B.N else B.T_SPIN + 0.3) + 0.05
        seg(ids[k][2], ids[k][3] + 2.0, t0, t1, 0.75, 0.25 * (-1) ** k, 0.05, 0.08 if k + 1 < B.N else 0.4, 'carrousel')
    # 3. le mur : six shorts à la fois, étalés dans la stéréo
    wall = ['gazette-1900__evenements__9-novembre-1989-mur-de-berlin', 'pixel-arcade__engagement__quelle-bille-gagne-la-course',
            'tableau-craie__explicatif__pourquoi-le-ciel-est-bleu', 'cosmos-doc__evenements__voyager-1-a-un-jour-lumiere',
            'pastel-diorama__enfants__d-ou-vient-la-pluie', 'riso-zine__geographie__5-plus-grands-deserts']
    for k, sname in enumerate(wall):
        seg(sname, 1.0, B.T_WALL + 0.1 + 0.12 * k, B.T_JUDGE + 0.15, 0.36, -0.9 + 1.8 * k / 5, 0.5, 0.6, 'mur')
    # 4. les épisodes 1, 2, 3 : le son du short qui passe dans le téléphone
    for k, (sname, st0) in enumerate(B.EPISODES):
        t1 = B.T_EP[k + 1] if k < 2 else B.T_SLAM + 0.1
        seg(sname, st0, B.T_EP[k], t1 + 0.1, 0.95, 0, 0.12, 0.2, 'épisode')
    # 5. les quatre panneaux : chaque short entre avec son panneau
    for k, (name, _, _) in enumerate(B.PANELS):
        r = ids[B.IDX[name]]
        seg(r[2], r[3] + 1.0, B.T_SLAM + k + 0.05, B.T_END + 0.35, 0.42, -0.75 + 0.5 * k, 0.25, 0.5, 'panneau')
    return tr.x, log


# ------------------------------------------------------------------ musique
def music():
    D = B.DUR
    drums, tonal, fx = Track(D), Track(D), Track(D)
    K, HH, CL, CR = kick(), hat(), clap(), crash()
    OH = hat(0.16, 3, 22)
    T0 = B.T_COV

    # 0 -> T_MUT : la « musique de template » (ukulélé joyeux, filtré comme un haut-parleur de téléphone), puis elle déraille
    muz = Track(3.0)
    cmaj = [(60, 64, 67), (60, 64, 67), (65, 69, 72), (67, 71, 74)]
    for i in range(int((B.T_MUT + 0.4) / 0.25)):
        ch = cmaj[(i // 4) % 4]
        muz.add(pluck(ch[(0, 2, 1, 2)[i % 4]] + 12, 0.3, 4000), i * 0.25, 0.5)
        if i % 4 == 0:
            muz.add(pluck(ch[0] - 12, 0.5, 1200), i * 0.25, 0.6)
    m = hp(lp(muz.x, 3400), 380)
    n0, n1 = int((B.T_MUT - 0.05) * SR), int((B.T_MUT + 0.45) * SR)      # arrêt de bande
    sp = np.ones(n1)
    sp[n0:] = np.linspace(1, 0.05, n1 - n0) ** 1.5
    pos = np.cumsum(sp)
    pos = pos[pos < len(m) - 1]
    m2 = np.stack([np.interp(pos, np.arange(len(m)), m[:, c]) for c in range(2)], 1)
    m2[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))[:, None]
    fx.add(m2, 0, 1.1)
    for t in (0.03, 0.50, 0.95):
        drums.add(K, t, 0.9)

    def chord_at(t):
        return CH[int((t - T0) // 2.0) % 4]

    def groove(t0, t1, full=True, hats=True, kicks=True, claps=True, arp=True, bassg=1.0, stabs=True):
        nb = int(round((t1 - t0) / BEAT))
        for b in range(nb):
            t = t0 + b * BEAT
            gb = int(round((t - T0) / BEAT))          # numéro de temps global : la mesure ne se décale pas entre sections
            root, chord = chord_at(t + 0.01)
            if kicks and (full or gb % 2 == 0):
                drums.add(K, t, 0.95)
            if hats:
                drums.add(HH, t + 0.25, 0.30, 0.2)
                if full:
                    drums.add(HH, t + 0.125, 0.12, -0.3)
                    drums.add(HH, t + 0.375, 0.12, 0.3)
                    if gb % 4 == 3:
                        drums.add(OH, t + 0.25, 0.22, 0.1)
            if claps and full and gb % 2 == 1:
                drums.add(CL, t, 0.55)
            if bassg:
                tonal.add(bass(root - 12, 0.24), t, 0.55 * bassg)
                tonal.add(bass(root - 12, 0.22), t + 0.25, 0.42 * bassg)
                if full and gb % 4 == 3:
                    tonal.add(bass(root, 0.12), t + 0.375, 0.3 * bassg)
            if arp:
                pat = [0, 1, 2, 1, 0, 2, 1, 2]
                for s in range(4):
                    q = (gb * 4 + s) % 8
                    nt = chord[pat[q]] + (12 if q in (2, 5) else 0)
                    tonal.add(pluck(nt + 12, 0.26, 3200 if full else 1800), t + s * 0.125, 0.16 if full else 0.11, 0.5 * math.sin(gb + s))
                    tonal.add(pluck(nt + 12, 0.26, 1500), t + s * 0.125 + 0.1875, 0.06, -0.5 * math.sin(gb + s))  # écho
            if stabs and full and gb % 4 in (0, 3):
                tonal.add(stab([c + 12 for c in chord]), t + (0 if gb % 4 == 0 else 0.25), 0.22)

    def pads(t0, t1, g=0.16, cut=1500):
        t = t0
        while t < t1 - 0.01:
            nxt = T0 + (math.floor((t - T0) / 2.0 + 1e-6) + 1) * 2.0
            d = min(nxt, t1) - t
            tonal.add(pad(chord_at(t + 0.01)[1], d + 0.3, cut), t, g)
            t += d

    def roll(t0, t1, g0=0.15, g1=0.6, step=0.125):
        n = int(round((t1 - t0) / step))
        for i in range(n):
            drums.add(CL, t0 + i * step, g0 + (g1 - g0) * i / max(1, n - 1))

    # carrousel : entrée à mi-régime, plein régime, puis sans arpège pendant que les shorts « parlent » (7,5 -> 11)
    groove(T0, T0 + 1.0, full=False, claps=False)
    groove(T0 + 1.0, 7.5)
    groove(7.5, 11.0, arp=False, stabs=False)
    groove(11.0, B.T_SPIN, claps=True)
    groove(B.T_SPIN, B.T_WALL - 0.5, full=False, kicks=True, hats=True, arp=True)      # le tour : on retient, roulement
    roll(B.T_SPIN + 0.2, B.T_WALL - 0.1)
    pads(T0, B.T_WALL)
    # mur : plein régime + cymbale
    drums.add(CR, B.T_WALL, 0.5)
    groove(B.T_WALL, B.T_JUDGE)
    pads(B.T_WALL, B.T_JUDGE)
    # juge : on retire la grosse caisse, on garde le fil, puis un battement monte vers 18/18
    groove(B.T_JUDGE, B.T_JUDGE + 2.0, full=False, kicks=False, hats=True, bassg=0.5)
    groove(B.T_JUDGE + 2.0, B.T_TERM, full=False, kicks=True, hats=True, bassg=0.7)
    pads(B.T_JUDGE, B.T_TERM, 0.3, 1900)
    # le prompt : presque rien (basse + nappe), la frappe s'entend
    groove(B.T_TERM, B.T_CHK[0], full=False, kicks=False, hats=False, arp=False, bassg=0.7, stabs=False)
    groove(B.T_CHK[0], B.T_EP[0] - 1.0, full=False, kicks=True, hats=True, bassg=0.8)
    groove(B.T_EP[0] - 1.0, B.T_EP[0] - 0.5, full=False, kicks=True, hats=True, bassg=0.8)
    pads(B.T_TERM, B.T_EP[0] - 0.2, 0.3, 1100)
    roll(B.T_EP[0] - 1.0, B.T_EP[0] - 0.14, 0.2, 0.75)
    # LE DROP : les épisodes défilent (batterie + basse devant, pas d'arpège : on écoute les shorts)
    drums.add(CR, B.T_EP[0], 0.7)
    groove(B.T_EP[0], B.T_SLAM, arp=False)
    pads(B.T_EP[0], B.T_SLAM, 0.12)
    for t in B.T_EP[1:]:
        drums.add(CR, t, 0.35)
    # panneaux : tout le monde
    drums.add(CR, B.T_SLAM, 0.6)
    groove(B.T_SLAM, B.T_END)
    pads(B.T_SLAM, B.T_END)
    roll(B.T_END - 0.5, B.T_END - 0.05, 0.3, 0.7)
    # fin : accord tenu + arpège de cloche, puis un dernier coup sur « À vous de jouer »
    tonal.add(pad([45, 57, 60, 64, 71], 4.4, 2200), B.T_END, 0.34)
    tonal.add(stab([57, 60, 64, 69, 72], 0.6), B.T_END, 0.5)
    for k, mnote in enumerate((69, 72, 76, 81, 84)):
        tonal.add(pluck(mnote, 1.2, 3000), B.T_END + k * 0.125, 0.22, 0.6 * (-1) ** k)
    drums.add(K, B.T_END, 1.0)
    drums.add(CR, B.T_END, 0.7)
    t_last = B.VOICE[-1][1][-1][2]
    drums.add(K, t_last + 0.02, 0.9)
    tonal.add(stab([45, 57, 64, 69], 0.5), t_last + 0.02, 0.4)

    # pompage (sidechain) de la partie tonale sur les grosses caisses
    env = np.ones(len(tonal.x))
    for t0, t1, step in ((T0, T0 + 1.0, 1.0), (T0 + 1.0, B.T_SPIN, 0.5), (B.T_WALL, B.T_JUDGE, 0.5), (B.T_EP[0], B.T_END, 0.5)):
        t = t0
        while t < t1 - 0.01:
            i = int(t * SR)
            n = int(0.3 * SR)
            env[i:i + n] = np.minimum(env[i:i + n], 1 - 0.55 * np.exp(-np.arange(n) / (0.09 * SR)))
            t += step
    tonal.x *= env[:, None]
    mix = drums.x * 0.8 + tonal.x * 1.0 + fx.x
    # le silence d'une double croche juste avant le drop
    i0, i1 = int((B.T_EP[0] - 0.13) * SR), int(B.T_EP[0] * SR)
    mix[i0:i1] *= np.linspace(1, 0, i1 - i0)[:, None] ** 0.3 * 0.15
    n = int(1.4 * SR)
    e = int(D * SR)
    mix[e - n:e] *= np.linspace(1, 0, n)[:, None] ** 2
    mix[e:] = 0
    return mix


# ------------------------------------------------------------------ bruitages
def sfx_track():
    D = B.DUR
    tr = Track(D)
    S = {n: load(n) for n in ('click', 'ding', 'glitch', 'impact', 'impact_light', 'key1', 'key2', 'key3', 'pop', 'riser', 'whoosh_fast', 'whoosh_soft')}
    ev = []

    def put(name, t, g=0.6, ratio=1.0, pan=0.0, rev=False):
        y = S[name] if ratio == 1.0 else pitch(S[name], ratio)
        if rev:
            y = y[::-1]
            t = t - len(y) / SR
        tr.add(y, t, g, pan)
        ev.append({'t': round(t, 3), 'sfx': name + ('(inversé)' if rev else ''), 'gain': round(g, 2)})

    def syn(kind, t, g=0.5, pan=0.0, **kw):
        y = SND.sfx(kind, **kw)
        y = y / (np.abs(y).max() or 1)
        tr.add(y, t, g, pan)
        ev.append({'t': round(t, 3), 'sfx': 'synthèse:' + kind, 'gain': round(g, 2)})

    def raw(y, t, g, name, pan=0.0):
        tr.add(y / (np.abs(y).max() or 1), t, g, pan)
        ev.append({'t': round(t, 3), 'sfx': 'synthèse:' + name, 'gain': round(g, 2)})

    def reveal(t, d=1.6, g=0.5, big=True):
        """Montée vers une révélation, puis l'impact : aspiration + riser + bruit, coup, chute de basse."""
        put('riser', t - 1.76 * (d / 1.76), g, 1.76 / d)
        raw(noise_riser(d), t - d, g * 0.55, 'montée de bruit')
        put('whoosh_soft', t - 0.02, 0.45, rev=True)
        put('impact', t, 1.0)
        if big:
            raw(subdrop(), t, 0.8, 'chute de basse')
            put('whoosh_soft', t + 0.02, 0.4, 0.8)

    # --- accroche : trois mots qui claquent
    for k, t in enumerate((0.03, 0.50, 0.95)):
        put('whoosh_fast', t - 0.12, 0.3, 1.1)
        put('impact_light' if k < 2 else 'impact', t, 0.85 + 0.1 * k)
        syn('thud', t, 0.5)
    # --- la carte change de style : arrêt de bande, zapping, montée
    put('glitch', B.T_MUT - 0.04, 0.7)
    put('glitch', B.T_MUT + 0.1, 0.35, 1.5)
    for k in range(6):
        put('pop', B.T_MUT + 0.25 * k, 0.5, 0.9 + 0.09 * k, pan=0.4 * (-1) ** k)
        put('click', B.T_MUT + 0.25 * k, 0.4, 1.0 + 0.1 * k)
    reveal(B.T_COV, 1.5, 0.55)
    # --- carrousel : un souffle + un tic à chaque glissement, plus marqués sur les quatre que la voix nomme
    for k in range(1, B.N):
        t = B.COV_T[k]
        named = k >= B.N - 4
        put('whoosh_fast', t - 0.10, 0.42 if named else 0.26, 0.9 + 0.03 * (k % 5), pan=0.5 * (-1) ** k)
        put('click', t + 0.02, 0.4, 0.85 + 0.02 * k, pan=0.3 * (-1) ** k)
        if named:
            put('impact_light', t + 0.03, 0.6)
            syn('thud', t + 0.03, 0.35)
    put('ding', 5.42, 0.3, 1.2)                                   # « 18 identités visuelles » s'affiche
    # le tour complet : souffle qui accélère, montée, puis le mur tombe
    for k in range(9):
        x = (k / 9) ** 0.45
        put('whoosh_fast', B.T_SPIN + x * (B.T_WALL - B.T_SPIN - 0.15), 0.22 + 0.03 * k, 0.9 + 0.07 * k, pan=0.7 * (-1) ** k)
    reveal(B.T_WALL, 1.2, 0.6)
    # --- mur des 45 shorts
    for k in range(6):                                            # les cartes se posent
        put('pop', B.T_WALL + 0.04 + 0.045 * k, 0.22, 1.2 + 0.08 * k, pan=-0.8 + 0.32 * k)
    put('impact', B.T_WALL + 0.3, 0.9, 0.9)                       # « 45 shorts »
    raw(subdrop(0.8), B.T_WALL + 0.3, 0.55, 'chute de basse')
    put('whoosh_fast', B.T_WALL + 1.72, 0.35)
    put('impact_light', B.T_WALL + 1.8, 0.6)                      # « tous rendus par du code »
    # --- juge à l'aveugle
    put('whoosh_soft', B.T_JUDGE - 0.25, 0.6)
    put('impact_light', B.T_JUDGE + 0.05, 0.5)
    for k in range(12):                                           # 72 images qui tombent en vrac
        put('click', B.T_JUDGE + 0.03 + 0.022 * k, 0.2, 0.7 + 0.05 * (k % 5), pan=-0.8 + 1.6 * (k % 6) / 5)
    put('whoosh_soft', B.T_JUDGE + 0.95, 0.6, 1.15)               # elles se rangent
    put('whoosh_fast', B.T_JUDGE + 1.35, 0.35, 0.8)
    put('riser', B.T_JUDGE + 2.3 - 0.25, 0.4, 1.76 / 1.25)         # montée pendant les coches
    for k in range(B.N):
        put('click', B.T_JUDGE + 2.3 + k * 0.055, 0.42, 0.9 + 0.045 * k, pan=-0.8 + 1.6 * k / 17)
        syn('blip', B.T_JUDGE + 2.3 + k * 0.055, 0.16, note=hz(72 + k), pan=-0.8 + 1.6 * k / 17)
    t18 = B.T_JUDGE + 2.3 + B.N * 0.055
    put('impact', t18, 1.0)                                       # 18/18
    raw(subdrop(0.9), t18, 0.7, 'chute de basse')
    put('ding', t18, 0.8)
    put('ding', t18 + 0.12, 0.45, 1.5)
    syn('chime', t18, 0.3, note='A5', dur=1.6)
    # --- le prompt : glissement, frappe, entrée
    put('whoosh_fast', B.T_TERM - 0.12, 0.55, 0.85)
    put('impact_light', B.T_TERM + 0.12, 0.5)
    total = sum(len(l) for l in B.PROMPT)
    rng = np.random.default_rng(11)
    for c in range(0, total, 2):
        ch = ''.join(B.PROMPT)[c]
        t = B.TYPE0 + (B.TYPE1 - B.TYPE0) * c / total
        put(f'key{1 + int(rng.integers(0, 3))}', t + float(rng.uniform(-0.012, 0.012)), 0.42 if ch != ' ' else 0.3,
            float(rng.uniform(0.9, 1.1)), pan=float(rng.uniform(-0.35, 0.05)))
    put('key1', B.TYPE1 + 0.12, 0.7, 0.7)                         # touche Entrée
    put('click', B.TYPE1 + 0.12, 0.5, 0.6)
    for hi in range(int((B.T_CHK[0] - (B.T_TERM + 1.3)) / 0.25)):  # l'agent compare les styles
        put('click', B.T_TERM + 1.3 + 0.25 * hi, 0.2, 1.3 + 0.03 * hi, pan=0.55)
        syn('tick', B.T_TERM + 1.3 + 0.25 * hi, 0.14, pan=0.55)
    for k, t in enumerate(B.T_CHECKS):                            # les ✓
        put('ding', t, 0.6 if k < 3 else 0.32, 1.0 + 0.08 * k, pan=-0.3)
        put('pop', t, 0.35 if k < 3 else 0.2, 1.3, pan=-0.3)
    put('impact_light', B.T_CHK[0], 0.55)                         # le style est choisi
    put('whoosh_soft', B.T_CHK[1] - 0.02, 0.55, pan=0.4)           # la carte devient le téléphone
    for k in range(8):                                            # rendu image par image
        syn('tick', B.T_CHK[1] + 0.7 + 0.15 * k, 0.16 + 0.02 * k, pan=0.5)
    # --- LE DROP : épisode 1
    reveal(B.T_EP[0], 1.7, 0.7)
    put('ding', B.T_EP[0] + 0.02, 0.5, 0.8)
    for t in B.T_EP[1:]:                                          # épisodes 2 et 3 : balayage du fil
        put('whoosh_soft', t, 0.4, rev=True)
        put('whoosh_fast', t - 0.06, 0.55)
        put('impact', t, 0.8, 1.05)
        syn('thud', t, 0.5)
    # --- les quatre panneaux
    put('riser', B.T_SLAM - 1.2, 0.45, 1.76 / 1.2)
    for k in range(4):
        t = B.T_SLAM + k
        put('whoosh_fast', t - 0.10, 0.5, 0.9, pan=-0.7 + 0.45 * k)
        put('impact', t + 0.04, 0.7, 1.0 - 0.05 * k, pan=-0.6 + 0.4 * k)
        put('impact_light', t + 0.14, 0.75, pan=-0.6 + 0.4 * k)   # le chiffre claque
        raw(subdrop(0.7), t + 0.04, 0.5, 'chute de basse')
    # --- fin : le coup final
    reveal(B.T_END, 1.3, 0.7)
    syn('chime', B.T_END, 0.3, note='A5', dur=2.4)
    syn('chime', B.T_END + 0.12, 0.2, note='E6', dur=2.0)
    for k in range(1, 6):                                         # le nom change de police sur chaque temps
        put('click', B.T_END + 0.3 + 0.5 * k, 0.4, 1.0 + 0.06 * k)
        put('pop', B.T_END + 0.3 + 0.5 * k, 0.22, 1.1 + 0.06 * k)
    put('ding', B.T_END + 1.1, 0.45, 1.12)                        # l'adresse
    t_last = B.VOICE[-1][1][-1][2]
    put('whoosh_soft', t_last + 0.02, 0.45, rev=True)
    put('impact', t_last + 0.02, 0.9)                             # « À vous de jouer »
    raw(subdrop(1.3), t_last + 0.02, 0.7, 'chute de basse')
    put('ding', t_last + 0.04, 0.6, 0.75)
    x = tr.x
    wet = np.stack([SND.simple_reverb(x[:, c], 0.14) for c in range(2)], 1)   # un peu d'air autour des bruitages
    return wet, ev


def limit(x, peak=0.84, drive=1.1):
    x = np.tanh(x * drive) / np.tanh(drive)
    pk = np.abs(x).max()
    return x * (peak / pk) if pk > 0 else x


def write_wav(path, x):
    wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))


def audio():
    B.TMP.mkdir(parents=True, exist_ok=True)
    n = int(B.DUR * SR)
    mus = music()[:n]
    sfx, ev = sfx_track()
    sfx = sfx[:n]
    sh, slog = shorts_layer()
    sh = sh[:n]
    voice = voice_track(n)
    # sans voix : musique + bruitages + son des shorts
    novo = limit(mus * 0.55 + sfx * 0.85 + sh * 0.8)
    write_wav(B.TMP / 'bed.wav', novo)
    print(B.TMP / 'bed.wav')
    info = {'duration': B.DUR, 'bpm': 120,
            'layers': 'voix off (voice_fr/) · son propre des shorts à l’écran · musique synthétisée · bruitages',
            'ducking': 'sous la voix off : son des shorts −13 dB, musique −7 dB, bruitages −2 dB',
            'sfx': ev, 'shortsAudio': slog}
    json.dump(info, open(HERE / 'sound_fr.json', 'w'), ensure_ascii=False, indent=1)
    if voice is not None:
        pres = (np.abs(voice) > 0.015).astype(np.float64)
        env = smooth_env(pres, 0.04, 0.22)
        d_sh = 1 - 0.78 * env          # son des shorts : −13 dB sous la voix, plein niveau dans les silences
        d_mu = 1 - 0.55 * env          # musique : −7 dB
        d_fx = 1 - 0.20 * env          # bruitages : −2 dB
        mixv = mus * 0.55 * d_mu[:, None] + sfx * 0.85 * d_fx[:, None] + sh * 0.8 * d_sh[:, None] + np.stack([voice, voice], 1) * 1.15
        write_wav(B.TMP / 'mix_voice.wav', limit(mixv, 0.89, 1.0))
        print(B.TMP / 'mix_voice.wav')
    elif (B.TMP / 'mix_voice.wav').exists():
        (B.TMP / 'mix_voice.wav').unlink()


def final(fmt):
    v = B.TMP / f'video_{fmt}.mp4'

    def mux(wav, out):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(v), '-i', str(wav), '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-pix_fmt', 'yuv420p', '-r', '30',   # ~12 Mo par fichier
                        '-af', 'loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.79:level=false', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-t', str(B.DUR),
                        '-movflags', '+faststart', str(out)], check=True)
        print(out)
    novo = HERE / f'demo_{fmt}_novo.mp4'
    mux(B.TMP / 'bed.wav', novo)
    if (B.TMP / 'mix_voice.wav').exists() and voice_files():
        mux(B.TMP / 'mix_voice.wav', HERE / f'demo_{fmt}.mp4')
    else:
        shutil.copyfile(novo, HERE / f'demo_{fmt}.mp4')
        print(HERE / f'demo_{fmt}.mp4', '(sans voix : voice_fr/ absent)')


def gif():
    src = HERE / 'demo_16x9.mp4'
    pal = B.TMP / 'palette.png'
    vf = 'fps=10,scale=480:-1:flags=lanczos'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-t', '12', '-i', str(src), '-vf', vf + ',palettegen=max_colors=128:stats_mode=diff', str(pal)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-t', '12', '-i', str(src), '-i', str(pal), '-lavfi', vf + '[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4',
                    str(HERE / 'demo_preview.gif')], check=True)
    print(HERE / 'demo_preview.gif')


def thumb():
    """Vignette 16:9 : le mur des vrais shorts + le titre."""
    from PIL import Image
    B.setfmt('16x9')
    fr = B.scene_wall(B.T_WALL + 2.6, 0, caption=False)
    W = B.W
    x = np.linspace(0, 1, W)[None, :, None]     # voile sombre à gauche
    al = np.clip(1.25 - x * 1.7, 0, 1) ** 1.2 * 0.93
    fr = (fr * (1 - al) + np.array(B.rgb('#07080F'), np.float32) * al).astype(np.uint8)
    y = 150
    for txt in ('18 identités', 'visuelles'):
        B.blit(fr, B.Tt(txt, ('unbounded', 900), 150, '#05060B'), 100 + 8, y + 10)
        B.blit(fr, B.Tt(txt, ('unbounded', 900), 150, B.YEL), 100, y)
        y += 190
    y += 40
    B.blit(fr, B.T('45 shorts pour le prouver.', B.GROT, 66, '#FFFFFF'), 100, y)
    B.blit(fr, B.T('Un prompt pour lancer la vôtre.', B.GROT, 66, '#FFFFFF'), 100, y + 88)
    lab = B.T('open source · rendu par du code', B.MONOB, 38, '#0B0D17')
    B.blit(fr, B.rr(lab.shape[1] + 48, lab.shape[0] + 24, 14, '#3CF2A0'), 100, y + 215)
    B.blit(fr, lab, 124, y + 227)
    fr = B.finish(fr, 0)
    d = HERE / 'thumb'
    d.mkdir(exist_ok=True)
    im = Image.fromarray(fr)
    im.save(d / 'thumbnail_fr_1920.jpg', quality=90)
    im.resize((1280, 720), Image.LANCZOS).save(d / 'thumbnail_fr_1280.jpg', quality=88)
    print(d / 'thumbnail_fr_1280.jpg')


def write_narration():
    def nwords(txt):
        return len([w for w in txt.replace(B.NB, ' ').replace('…', ' ').split() if any(c.isalnum() for c in w)])
    lines = []
    for k, (txt, chunks) in enumerate(B.VOICE):
        a = chunks[0][2]
        b = round(chunks[-1][2] + chunks[-1][1] - chunks[-1][0], 2)
        speech = sum(c[1] - c[0] for c in chunks)
        lines.append({'index': k, 'file': f'voice_fr/{k:02d}.mp3', 'start': a, 'end': b, 'text': txt,
                      'wordsPerSec': round(nwords(txt) / speech, 2),
                      'chunks': [{'rawStart': c[0], 'rawEnd': c[1], 'start': c[2], 'end': round(c[2] + c[1] - c[0], 2)} for c in chunks]})
    out = {'language': 'fr', 'voice': 'Gemini « Puck », style « voix off de bande-annonce, très punchy »',
           'source': 'voice_fr_raw/demo.mp3 (un seul appel, 39,84 s, les 12 lignes jointes par <long pause>)',
           'note': 'Découpe par build_audio.split_voice() : silences (ffmpeg silencedetect, −38 dB) + horodatage des mots faster-whisper small. '
                   'start/end = instants réels dans la vidéo ; rawStart/rawEnd = instants dans le fichier brut. '
                   'Les pauses internes sont resserrées ou étirées pour que chaque mot tombe sur son image. wordsPerSec = débit réel de la voix.',
           'duration': B.DUR, 'lines': lines}
    json.dump(out, open(HERE / 'narration_fr.json', 'w'), ensure_ascii=False, indent=1)
    print(HERE / 'narration_fr.json')
    for l in lines:
        print(f"  {l['start']:5.2f}–{l['end']:5.2f}  {l['wordsPerSec']:.2f} m/s  {l['text']}")
