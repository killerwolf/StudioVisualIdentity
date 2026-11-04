"""Moteur de rendu de la chaîne : un seul moteur pour les Shorts (1080×1920) et les vidéos longues (1920×1080).

Une vidéo = un fichier `episodes/<slug>/video.py` qui décrit les répliques et les scènes :

    from episode import Episode
    import elements as E

    ep = Episode("xx-1-exemple", format="short", serie="SÉRIE · 01")
    r1 = ep.replique("voix/01.mp3", "Everyone says AI agents. But what is an agent, really? ...")
    s = ep.scene("accroche", r1.debut())
    s.pose(E.bandes([("What is", "papier"), ("an AI agent?", "bleu")]), 520, 590, 0, effet="aucun")
    s.pose(E.carte("Act", "use a tool", couleur="jaune"), 540, 900, r1.phrase(3))
    ep.lancer()

Commandes (dans le dossier de la vidéo) :
    ../../.venv/bin/python video.py images 0 3.5 12   images fixes de contrôle (out/images/)
    ../../.venv/bin/python video.py son                 le mixage seul
    ../../.venv/bin/python video.py video               la vidéo complète (JOBS=n tranches en parallèle)
    ../../.venv/bin/python video.py miniature           la miniature
Le moteur ajoute seul : générique (Long), logo en coin (Short), suivi des chapitres (Long), sous-titres
(incrustés pour un Short, fichier .srt pour un Long), fin, bruitages de base, mixage aux NIVEAUX validés.
"""
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image

import chaine as C
import elements as E
import papier as P
import son

FORMATS = {"short": (1080, 1920), "long": (1920, 1080)}
FPS = 30
ECART_PAPIER = 2.5               # secondes au moins entre deux bruits de papier (« swoosh fatigue », 2026-10-25)
TRANS = 0.25                     # la scène qui se termine glisse vers la gauche (en pas)
SFX = {"papier": "sfx/papier_pose.wav", "glisse": "sfx/glissement.wav", "ticket": "sfx/ticket.mp3",
       "bouton": "sfx/bouton.mp3"}
Y_SOUS_TITRE, X_SOUS_TITRE = 1330, 490      # Short : au-dessus de la zone YouTube, à gauche des boutons
INTRO_LONG = 5.0                             # générique d'une vidéo longue
CHAPITRES = ["1 · Problem", "2 · Plan", "3 · What broke", "4 · Cost", "5 · Result"]


def glitch(c, t):
    """Éclair « glitch » d'un pas (vidéo de danse) : canaux rouge et bleu décalés, bandes déplacées, image un peu éclaircie."""
    import numpy as np
    a = np.asarray(c.convert("RGB")).astype(np.int16)
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], 14, axis=1)
    out[..., 2] = np.roll(a[..., 2], -14, axis=1)
    r = np.random.default_rng(int(t * 1000))
    for _ in range(5):
        y = int(r.integers(0, a.shape[0] - 60))
        hb = int(r.integers(20, 60))
        out[y:y + hb] = np.roll(out[y:y + hb], int(r.integers(-60, 60)), axis=1)
    out = np.clip(out * 0.85 + 255 * 0.15, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB").convert("RGBA")


def duree_audio(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)


def segments_parole(f, seuil=-40, mini=0.18):
    """Morceaux de parole d'un fichier (entre les silences)."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", f"silencedetect=n={seuil}dB:d={mini}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    debuts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", err)]
    fins = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    d = duree_audio(f)
    bornes, t = [], 0.0
    for a, b in zip(debuts, fins + [d] * (len(debuts) - len(fins))):
        if a - t > 0.05:
            bornes.append((t, a))
        t = b
    if d - t > 0.05:
        bornes.append((t, d))
    return bornes or [(0.0, d)]


def couper_phrases(texte):
    return [p for p in re.split(r"(?<=[.!?…])\s+", texte.strip()) if p]


def caler_sur_trous(cibles, trous, sans_trou=1.5):
    """Associe chaque début de phrase à un blanc de l'audio, dans l'ordre, au plus près des cibles
    (programmation dynamique ; une phrase peut rester sans blanc, avec une pénalité)."""
    from functools import lru_cache
    m, n = len(cibles), len(trous)

    @lru_cache(maxsize=None)
    def f(j, i):
        if j == m:
            return 0.0, ()
        best = (sans_trou + f(j + 1, i)[0], (None,) + f(j + 1, i)[1])
        for k in range(i, n):
            c = abs((trous[k][0] + trous[k][1]) / 2 - cibles[j]) + f(j + 1, k + 1)[0]
            if c < best[0]:
                best = (c, (k,) + f(j + 1, k + 1)[1])
        return best
    choix = f(0, 0)[1]
    out, prec = [], -1.0
    for j, k in enumerate(choix):
        t = trous[k][1] if k is not None else cibles[j]
        t = max(t, prec + 0.3)
        out.append(t)
        prec = t
    return out


class Ancre:
    """Un instant de la vidéo, résolu une fois les durées connues : réplique + phrase + décalage."""

    def __init__(self, rep=None, phrase=None, fin=False, plus=0.0, absolu=None):
        self.rep, self.phrase, self.fin, self.plus, self.absolu = rep, phrase, fin, plus, absolu

    def t(self):
        if self.absolu is not None:
            return self.absolu + self.plus
        if self.fin:
            return self.rep.t0 + self.rep.duree + self.plus
        if self.phrase is not None:
            return self.rep.t0 + self.rep.phrases[min(self.phrase, len(self.rep.phrases) - 1)][0] + self.plus
        return self.rep.t0 + self.plus


def instant(a):
    return a.t() if isinstance(a, Ancre) else float(a)


class Replique:
    def __init__(self, fichier, texte, pause_apres, gain, qui=None, parodie=False):
        self.fichier, self.texte, self.pause_apres, self.gain = fichier, texte, pause_apres, gain
        # une réplique inventée pour une vraie personne est toujours marquée « parody » (STYLE_GUIDE.md § 2.1)
        self.qui = f"{qui} · parody" if qui and parodie else qui
        self.t0 = self.duree = None
        self._niveaux = None
        self.phrases = []          # [(début relatif, texte)]

    def debut(self, plus=0.0):
        return Ancre(self, plus=plus)

    def phrase(self, i, plus=0.0):
        return Ancre(self, phrase=i, plus=plus)

    def fin(self, plus=0.0):
        return Ancre(self, fin=True, plus=plus)

    def caler(self):
        """Durée et début de chaque phrase, d'après les silences de l'audio."""
        self.duree = duree_audio(self.fichier)
        phrases = couper_phrases(self.texte)
        parole = segments_parole(self.fichier)
        debuts = [parole[0][0]]
        if len(phrases) > 1:
            # cible de chaque début de phrase : au prorata des caractères, entre la 1re et la dernière parole
            total, cumul, cibles = sum(len(p) for p in phrases), 0, []
            for p in phrases[:-1]:
                cumul += len(p)
                cibles.append(parole[0][0] + (parole[-1][1] - parole[0][0]) * cumul / total)
            trous = [(parole[i][1], parole[i + 1][0]) for i in range(len(parole) - 1)]
            debuts += caler_sur_trous(cibles, trous)
        self.phrases = list(zip(debuts, phrases))

    def niveau(self, t):
        """Force de la voix à l'instant t (0, 1, 2 ou 3), au pas du stop-motion : fait « parler » un portrait."""
        if self._niveaux is None:
            x = son.lire(self.fichier)
            n = int(son.SR / P.STOP)
            v = [float((x[i:i + n] ** 2).mean() ** 0.5) for i in range(0, len(x), n)]
            haut = sorted(v)[int(len(v) * 0.95)] or 1.0
            self._niveaux = [min(3, int(4 * a / haut)) if a > haut * 0.12 else 0 for a in v]
        i = int((t - self.t0) * P.STOP)
        return self._niveaux[i] if 0 <= i < len(self._niveaux) else 0


class Pose:
    def __init__(self, groupe, x, y, quand, effet, sortie, frisson, son_, echelle, plan=0, parle=()):
        self.plan, self.parle = plan, parle
        self.groupe, self.x, self.y, self.quand, self.effet = groupe, x, y, quand, effet
        self.sortie, self.frisson, self.son, self.echelle = sortie, frisson, son_, echelle
        self.jusqua, self.tj, self.bouches = None, None, None
        self.danse = None                       # (groupes, pas, départ) : une pose de marionnette par temps


class Video:
    def __init__(self, chemin, debut_source, x, y, largeur, hauteur, quand, angle, recadre):
        self.chemin, self.debut_source, self.x, self.y = chemin, debut_source, x, y
        self.taille, self.quand, self.angle, self.recadre = (largeur, hauteur), quand, angle, recadre
        self.lecteur = None


class Scene:
    def __init__(self, ep, nom, debut, chapitre):
        self.ep, self.nom, self.debut, self.chapitre = ep, nom, debut, chapitre
        self.poses, self.videos = [], []
        self.a = self.b = None

    def pose(self, groupe, x, y, quand=None, effet="auto", sortie=None, frisson=False, son="auto", echelle=1.0,
             dessous=False, parle=None, jusqua=None, bouches=None, danse=None):
        """Pose un élément en (x, y) à l'instant `quand` (Ancre ou secondes ; par défaut le début de la scène).
        effet : pop | depose | chute | glisse | aucun ; « auto » = pop (rythme vif) ou depose (rythme calme).
        son : papier | ticket | bouton | glisse | None ; « auto » = papier (rythme vif) ou rien (rythme calme).
        sortie : instant où il s'envole (facultatif). jusqua : instant où il disparaît, sans mouvement (rythme calme).
        dessous=True : dessiné sous les autres éléments de la scène (ex. les pointillés sous les cartes).
        parle=réplique (ou liste de répliques) : l'élément (un portrait) sautille au rythme de cette voix.
        danse=(groupes, pas, départ) : à chaque temps (pas en secondes, à partir de `départ`), le groupe suivant
        de la liste (le dernier reste) ; petit rebond sur chaque temps (vidéo de danse)."""
        parle = () if parle is None else (parle if isinstance(parle, (list, tuple)) else (parle,))
        calme = self.ep.rythme == "calme"
        if effet == "auto":
            effet = "depose" if calme else "pop"
        if son == "auto":
            son = None if calme else "papier"
        self.poses.append(Pose(groupe, x, y, quand, effet, sortie, frisson, son, echelle, -1 if dessous else 0, parle))
        self.poses[-1].jusqua = jusqua
        self.poses[-1].bouches = bouches         # E.avatars_parlants(...) : la bouche bouge avec la voix (parle=)
        self.poses[-1].danse = danse
        return self

    def video(self, chemin, debut_source, x, y, largeur, hauteur, quand=None, angle=0.0, recadre=None):
        """Insère une vidéo dans un cadre papier ; elle joue à partir de `debut_source` à l'instant `quand`."""
        self.videos.append(Video(chemin, debut_source, x, y, largeur, hauteur, quand, angle, recadre))
        return self


class Episode:
    def __init__(self, slug, format="short", serie="", fin_duree=None, dossier=None, rythme="vif", linkedin=False,
                 duree=None, fond="auto", bruitages=True, metronome=None):
        """rythme : « vif » (Shorts : une pièce qui saute et un bruit de papier à chaque idée) ou « calme »
        (vidéos longues : pièces simplement déposées, sans bruit ; glissement sonore seulement aux chapitres).
        linkedin=True : case « LinkedIn » cochée dans Notion → aussi une miniature 1080×1350 (<slug>_miniature_4x5.png).
        Vidéo sans voix (vidéo de danse) :
        duree = secondes avant l'écran de fin ; fond=None : pas de musique de fond ; bruitages=False : aucun bruitage ;
        metronome=(bpm, départ) : un clic par temps (accent tous les 4) pour vérifier la danse sans la chanson."""
        self.duree_libre, self.bruitages, self.metronome = duree, bruitages, metronome
        self.camera = None       # fonction t → dict(zoom, cx, cy, dx, dy, glitch) ; None = plan fixe (vidéo de danse)
        self._tapis_cam = {}
        self.fond = ("music/fond_short.mp3" if format == "short" else "music/fond_long.mp3") if fond == "auto" else fond
        assert format in FORMATS, format
        assert rythme in ("vif", "calme"), rythme
        self.rythme = rythme
        self.linkedin = linkedin
        self.slug, self.format, self.serie = slug, format, serie
        self.W, self.H = FORMATS[format]
        self.dossier = Path(dossier) if dossier else Path(sys.argv[0]).resolve().parent
        self.repliques, self.scenes, self.extraits = [], [], []
        self.fin_duree = fin_duree if fin_duree is not None else (3.2 if format == "short" else 20.0)
        self.miniature_mots = None
        self._calcule = False
        self._tapis = None

    # ---------- description ----------
    def replique(self, fichier, texte, pause_apres=0.35, gain=0.0, qui=None, parodie=False):
        """Une réplique (fichier relatif au dossier de la vidéo). `texte` sert aux sous-titres.
        qui : le nom de la personne qui parle (« Alan Turing ») ; None = le narrateur.
        parodie=True : réplique inventée pour une vraie personne → « NOM · PARODY » au-dessus du sous-titre."""
        r = Replique(self.dossier / fichier, texte, pause_apres, gain, qui, parodie)
        self.repliques.append(r)
        return r

    def scene(self, nom, debut, chapitre=None):
        """Nouvelle scène à l'instant `debut` ; elle dure jusqu'à la scène suivante. chapitre : 1 à 5 (Long)."""
        s = Scene(self, nom, debut, chapitre)
        self.scenes.append(s)
        return s

    def extrait_audio(self, chemin, debut_source, duree, quand, gain=0.0):
        """Le son d'origine d'une vidéo insérée (fondus doux de 0,3 s)."""
        self.extraits.append((chemin, debut_source, duree, quand, gain))

    def miniature_long(self, mots, groupe=None):
        """Miniature d'une vidéo longue : mots = [(texte, couleur)] (3 mots au plus en tout), groupe = l'objet du sujet."""
        self.miniature_mots = (mots, groupe)

    # ---------- calcul de la chronologie ----------
    def calculer(self):
        if self._calcule:
            return
        t = INTRO_LONG if self.format == "long" else 0.15
        for r in self.repliques:
            r.caler()
            r.t0 = t
            t += r.duree + r.pause_apres
        if self.duree_libre:
            t = max(t, self.duree_libre)
        self.fin_parole = t
        self.duree = round(t + self.fin_duree, 2)
        if self.format == "long":
            self.scenes.insert(0, Scene(self, "_intro", 0.0, None))
        self.scenes.append(Scene(self, "_fin", self.fin_parole, None))
        self.scenes.sort(key=lambda s: instant(s.debut))
        for i, s in enumerate(self.scenes):
            s.a = instant(s.debut)
            s.b = instant(self.scenes[i + 1].debut) if i + 1 < len(self.scenes) else self.duree + 1
            for p in s.poses:
                p.t = instant(p.quand) if p.quand is not None else s.a
                p.ts = instant(p.sortie) if p.sortie is not None else None
                p.tj = instant(p.jusqua) if p.jusqua is not None else None
            for v in s.videos:
                v.t = instant(v.quand) if v.quand is not None else s.a
            s.poses.sort(key=lambda p: p.plan)
        self._fabriquer_intro_fin()
        self.sous_titres = []
        for r in self.repliques:
            for k, (d, s) in enumerate(r.phrases):
                f = r.phrases[k + 1][0] if k + 1 < len(r.phrases) else r.duree + 0.25
                self.sous_titres.append((r.t0 + d, r.t0 + f, s, r.qui))
        self._calcule = True

    def _fabriquer_intro_fin(self):
        intro = next((s for s in self.scenes if s.nom == "_intro"), None)
        fin = next(s for s in self.scenes if s.nom == "_fin")
        a = fin.a
        if intro:
            for g, x, y, q in ((E.bouton(110), 960, 250, 0.4), (E.titre_chaine(150), 960, 470, 1.0),
                               (E.slogan(60), 1010, 660, 1.8), (E.etiquette(self.serie or C.NOM_COMPLET.upper()), 1010, 790, 2.4)):
                p = Pose(g, x, y, q, "pop", None, False, None, 1.0)
                p.t, p.ts = q, None
                intro.poses.append(p)
        if self.format == "short":
            elems = [(E.bouton(120), 540, 560, a + 0.1), (E.titre_chaine(110), 540, 820, a + 0.4),
                     (E.slogan(52), 540, 990, a + 0.8), (E.avatar(C.AVATAR_SALUT, 420), 300, 1260, a + 0.2),
                     (E.note(C.FIN_SHORT, "jaune", 300, 220, 44, 98), 780, 1200, a + 1.1)]
        else:
            elems = [(E.bande(C.FIN_LONG, "bleu", 90, seed=107), 520, 170, a + 0.2),
                     (E.emplacements_fin_long(), 960, 540, a + 0.5),
                     (E.avatar(C.AVATAR_SALUT, 360), 1560, 860, a + 0.8),
                     (E.slogan(56), 700, 820, a + 1.1), (E.logo_coin(30), 160, 980, a + 1.4)]
        for g, x, y, q in elems:
            p = Pose(g, x, y, q, "pop", None, False, None, 1.0)
            p.t, p.ts = q, None
            fin.poses.append(p)

    # ---------- image ----------
    def tapis(self):
        if self._tapis is None:
            self._tapis = P.tapis(self.W, self.H)
        return self._tapis

    def _poser_scene(self, c, s, t):
        for v in s.videos:
            if t >= v.t - 0.5 or v.t <= s.a:
                if v.lecteur is None:
                    v.lecteur = P.Lecteur(v.chemin, max(0.0, v.debut_source + max(t, s.a) - v.t), v.taille, v.recadre)
                img = v.lecteur.image(max(0.0, v.debut_source + t - v.t))
                if img is not None:
                    P.poser(c, P.cadre(img, 14), v.x, v.y, v.angle, P.pop(t, max(s.a, v.t - 0.5)))
        for p in s.poses:
            if (t < p.t and p.effet != "aucun") or (p.tj is not None and t >= p.tj):
                continue
            dx, dy, da = P.frisson(t, id(p) % 997) if p.frisson else (0, 0, 0.0)
            ech, oy, ox = p.echelle, 0.0, 0.0
            groupe = p.groupe
            if p.danse:
                groupes, pas, depart = p.danse[:3]
                rebond = p.danse[3] if len(p.danse) > 3 else pas       # (vidéo de danse) la bouche rebondit avec le corps
                k = int(math.floor((t - instant(depart)) / pas)) if t >= instant(depart) else 0
                groupe = groupes[max(0, min(k, len(groupes) - 1))]
                if t >= instant(depart) and (t - instant(depart)) % rebond < 1 / P.STOP:
                    oy -= 12                     # rebond sur le temps
            for r in p.parle:                      # la personne parle : petits sauts au rythme de sa voix
                n = r.niveau(t)
                if p.bouches and n:
                    groupe = p.bouches[n]
                if n:
                    ech *= 1 + 0.025 * n
                    oy -= 7 * n
                    da += (0.8 if int(t * P.STOP) % 2 else -0.8) * n
            if p.effet == "pop":
                ech *= P.pop(t, p.t)
            elif p.effet == "depose":
                e, d = P.depose(t, p.t)
                ech *= e
                oy += d
            elif p.effet == "chute":
                oy = P.glisse(t, p.t, -self.H, 0.0, 5)
            elif p.effet == "glisse":
                ox = P.glisse(t, p.t, -self.W, 0.0, 5)
            if p.ts is not None and t >= p.ts:
                oy += P.glisse(t, p.ts, 0.0, -self.H, 4)
            for piece, gx, gy, ang in groupe:
                P.poser(c, piece, p.x + (gx * p.echelle) + ox + dx, p.y + (gy * p.echelle) + oy + dy, ang + da, ech,
                        cle=(id(piece[0]), p.echelle))

    def _regler_camera(self, t, fin):
        """Caméra (vidéo de danse) : zoom autour d'un point, tremblement ; pas de caméra sur l'écran de fin."""
        if self.camera is None or t >= fin.a:
            return None
        cam = self.camera(t)
        z = max(1.0, round(cam.get("zoom", 1.0) / 0.02) * 0.02)          # paliers : le cache des pièces reste petit
        cx = min(max(cam.get("cx", self.W / 2), self.W / (2 * z)), self.W - self.W / (2 * z))
        cy = min(max(cam.get("cy", self.H / 2), self.H / (2 * z)), self.H - self.H / (2 * z))
        dx, dy = cam.get("dx", 0), cam.get("dy", 0)
        return z, round(cx), round(cy), dx, dy, cam.get("glitch", False)

    def _tapis_camera(self, z, cx, cy, dx, dy):
        k = (z, cx, cy, dx, dy)
        if k not in self._tapis_cam:
            if len(self._tapis_cam) > 64:
                self._tapis_cam.clear()
            w, h = self.W / z, self.H / z
            x0, y0 = cx - w / 2 - dx / z, cy - h / 2 - dy / z
            self._tapis_cam[k] = self.tapis().transform((self.W, self.H), Image.EXTENT, (x0, y0, x0 + w, y0 + h),
                                                         Image.BILINEAR)
        return self._tapis_cam[k]

    def image(self, t, avec_sous_titres=True):
        self.calculer()
        fin = next(s for s in self.scenes if s.nom == "_fin")
        cam = self._regler_camera(t, fin)
        if cam and (cam[0] != 1 or cam[3] or cam[4]):
            c = self._tapis_camera(*cam[:5]).copy()
            P.CAMERA = (cam[0], cam[1], cam[2], self.W, self.H, cam[3], cam[4])
        else:
            c = self.tapis().copy()
        for s in self.scenes:
            if s.a <= t < s.b + TRANS:
                if t >= s.b:
                    couche = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
                    self._poser_scene(couche, s, t)
                    dec = -self.W * min(1, math.floor((t - s.b) * P.STOP + 1) / 3)
                    c.alpha_composite(couche.transform(couche.size, Image.AFFINE, (1, 0, -dec, 0, 1, 0)))
                else:
                    self._poser_scene(c, s, t)
        P.CAMERA = None
        if cam and cam[5]:
            c = glitch(c, t)
        en_cours = next((s for s in self.scenes if s.a <= t < s.b), None)
        if self.format == "short" and t < fin.a:
            for piece, gx, gy, ang in E.logo_coin():
                P.poser(c, piece, 110 + gx, 190 + gy, ang, 1.0, cle=(id(piece[0]), 1.0))
        if self.format == "long" and en_cours is not None and en_cours.chapitre:
            self._suivi_chapitres(c, en_cours.chapitre)
        if avec_sous_titres and self.format == "short" and t < fin.a:
            for a, b, s, qui in self.sous_titres:
                if a <= t < b:
                    for piece, gx, gy, ang in E.sous_titre(s, etiquette_haut=qui.upper() if qui else None):
                        P.poser(c, piece, X_SOUS_TITRE, Y_SOUS_TITRE, 0, 1.0, cle=("st", s, qui))
        return c.convert("RGB")

    _onglets = {}

    def _suivi_chapitres(self, c, actif):
        x = 260
        for i, n in enumerate(CHAPITRES):
            k = (i, i + 1 == actif)
            if k not in self._onglets:
                self._onglets[k] = P.bande(n.upper(), "mono", 24, P.BLUE if k[1] else P.PAPER,
                                           P.PAPER if k[1] else P.INK_SOFT, (18, 10), 100 + i)
            b = self._onglets[k]
            P.poser(c, b, x + b[0].width / 2 - 40, 70, 0.6 if i % 2 else -0.6, 1.0, cle=("onglet",) + k)
            x += b[0].width - 60

    # ---------- son ----------
    def mixage(self, sortie):
        self.calculer()
        evts = []
        chap = None
        papiers = []
        for s in self.scenes:
            # le glissement (« swoosh ») ne s'entend qu'aux changements de chapitre et à l'écran de fin, Shorts compris
            # (« swoosh fatigue » : pas de glissement sonore à chaque scène)
            tourne = s.nom == "_fin" or (s.chapitre and s.chapitre != chap)
            chap = s.chapitre or chap
            if s.nom not in ("_intro",) and s.a > 0.5 and tourne:
                evts.append((son.A / SFX["glisse"], s.a))
            for p in s.poses:
                if p.son == "papier":
                    papiers.append(p.t)
                elif p.son:
                    evts.append((son.A / SFX[p.son], p.t))
        dernier = -9.0
        for t in sorted(papiers):          # un bruit de papier toutes les ECART_PAPIER s au plus (même remarque)
            if t - dernier >= ECART_PAPIER:
                evts.append((son.A / SFX["papier"], t))
                dernier = t
        if self.format == "long":
            evts.append((son.A / SFX["bouton"], 0.3))
        fin = next(s for s in self.scenes if s.nom == "_fin")
        if self.format == "short":
            evts.append((son.A / SFX["bouton"], fin.a + 0.1))
        if not self.bruitages:
            evts = []
        if self.metronome:
            bpm, depart = self.metronome
            k, tc = 0, instant(depart)
            while tc < self.fin_parole:
                evts.append((("clic", k % 4 == 0), tc))
                k += 1
                tc = instant(depart) + k * 60 / bpm
        return son.mixer([(r.fichier, r.t0) for r in self.repliques],
                         son.A / self.fond if self.fond else None,
                         self.duree, sfx=evts, generique=0.6 if self.format == "long" else None, sortie=sortie,
                         niveau_fond="fond_short" if self.format == "short" else "fond_long",
                         extraits=self.extraits)

    # ---------- sorties ----------
    def garder_ancienne(self, f):
        """Range une version existante dans out/versions/vN_<date>_<heure>/ (rien n'est jamais supprimé) :
        la vidéo, ses sous-titres, sa miniature et une copie du video.py qui l'a produite (out/rendu_video.py).
        Pour revenir en arrière : reprendre les fichiers du dossier de la version voulue."""
        if not f.exists():
            return
        if getattr(self, "_version", None) is None:
            racine = self.dossier / "out/versions"
            racine.mkdir(parents=True, exist_ok=True)
            n = 1 + sum(1 for d in racine.iterdir() if d.is_dir() and d.name.startswith("v"))
            from datetime import datetime
            self._version = racine / f"v{n}_{datetime.now():%Y-%m-%d_%Hh%M}"
            self._version.mkdir()
            copie = self.dossier / "out/rendu_video.py"
            if copie.exists():
                shutil.move(str(copie), str(self._version / "video.py"))
        shutil.move(str(f), str(self._version / f.name))

    def copie_du_script(self):
        """Garde le video.py qui vient de produire la vidéo (rangé avec elle à la version suivante)."""
        shutil.copy2(Path(sys.argv[0]).resolve(), self.dossier / "out/rendu_video.py")

    def srt(self):
        def hms(x):
            h, r = divmod(x, 3600)
            m, s = divmod(r, 60)
            return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
        f = self.dossier / f"{self.slug}.srt"
        self.garder_ancienne(f)
        f.write_text("".join(f"{i + 1}\n{hms(a)} --> {hms(b)}\n{qui + ': ' if qui else ''}{s}\n\n"
                             for i, (a, b, s, qui) in enumerate(self.sous_titres)))
        return f

    def miniature(self):
        self.calculer()
        f = self.dossier / f"{self.slug}_miniature.png"
        self.garder_ancienne(f)
        if self.format == "short":
            premiere = next(s for s in self.scenes if not s.nom.startswith("_"))
            t_mini = getattr(self, "instant_miniature", None)       # vidéo de danse : une seule scène, couverture choisie
            self.image(t_mini if t_mini is not None else premiere.b - 0.05, avec_sous_titres=False).save(f)
        else:
            c = P.tapis(1280, 720)
            mots, groupe = self.miniature_mots or ([(self.slug, "jaune")], None)
            for i, (s, coul) in enumerate(mots):
                fond, encre = E.COULEURS[coul]
                b = P.bande(s, taille=104, fill=fond, ink=encre, pad=(30, 18), seed=108 + i)
                ech = min(1.0, 760 / (b[0].width - 80))          # jamais sur l'avatar (à droite de x = 800)
                P.poser(c, b, 40 + (b[0].width - 80) * ech / 2 + 20 * i, 190 + 170 * i, -2.3 if i % 2 == 0 else 1.4, ech)
            if groupe:
                for piece, gx, gy, ang in groupe:
                    P.poser(c, piece, 330 + gx, 580 + gy, ang)
            for piece, gx, gy, ang in E.avatar(C.AVATAR, 640):
                P.poser(c, piece, 1030, 400, 0)
            for piece, gx, gy, ang in E.bouton(46):
                P.poser(c, piece, 1210, 70, 0)
            c.convert("RGB").save(f)
        if self.linkedin:
            print("miniature LinkedIn :", self.miniature_linkedin(f))
        return f

    def miniature_linkedin(self, mini):
        """Miniature 4:5 (1080×1350) pour LinkedIn, tirée de la miniature YouTube `mini`.
        Short : la couverture recadrée au centre (la zone sûre y tient) ; Long : les mêmes pièces que la miniature
        YouTube, recomposées en hauteur (mots en haut, objet à gauche et avatar à droite en bas)."""
        f = self.dossier / f"{self.slug}_miniature_4x5.png"
        self.garder_ancienne(f)
        if self.format == "short":
            im = Image.open(mini).convert("RGB")
            haut = (im.height - 1350) // 2
            im.crop((0, haut, 1080, haut + 1350)).save(f)
            return f
        c = P.tapis(1080, 1350)
        mots, groupe = self.miniature_mots or ([(self.slug, "jaune")], None)
        for i, (s, coul) in enumerate(mots):
            fond, encre = E.COULEURS[coul]
            b = P.bande(s, taille=112, fill=fond, ink=encre, pad=(30, 18), seed=108 + i)
            ech = min(1.0, 940 / (b[0].width - 80))
            P.poser(c, b, 540 + 24 * (i % 2 * 2 - 1), 230 + 180 * i, -2.3 if i % 2 == 0 else 1.4, ech)
        if groupe:
            for piece, gx, gy, ang in groupe:
                P.poser(c, piece, 290 + gx, 1000 + gy, ang)
        for piece, gx, gy, ang in E.avatar(C.AVATAR, 640):
            P.poser(c, piece, 790, 1010, 0)
        for piece, gx, gy, ang in E.bouton(46):
            P.poser(c, piece, 1010, 70, 0)
        c.convert("RGB").save(f)
        return f

    def _tranche(self, k, n, sortie):
        self.calculer()
        total = int(self.duree * FPS)
        i0, i1 = total * k // n, total * (k + 1) // n
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{self.W}x{self.H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                              "-pix_fmt", "yuv420p", str(sortie)], stdin=subprocess.PIPE)
        for i in range(i0, i1):
            p.stdin.write(self.image(i / FPS).tobytes())
        p.stdin.close()
        if p.wait():
            raise SystemExit(f"tranche {k} : ffmpeg a échoué")

    def video(self):
        self.calculer()
        out = self.dossier / "out"
        out.mkdir(exist_ok=True)
        wav = self.mixage(out / f"{self.slug}_mix.wav")
        jobs = int(os.environ.get("JOBS", os.cpu_count() or 4))
        tmp = Path(tempfile.mkdtemp())
        procs = [subprocess.Popen([sys.executable, sys.argv[0], "tranche", str(k), str(jobs), str(tmp / f"p{k:02d}.mp4")])
                 for k in range(jobs)]
        if any(p.wait() for p in procs):
            raise SystemExit("une tranche a échoué")
        (tmp / "liste.txt").write_text("".join(f"file '{tmp / f'p{k:02d}.mp4'}'\n" for k in range(jobs)))
        final = self.dossier / f"{self.slug}.mp4"
        self.garder_ancienne(final)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "liste.txt"), "-i", str(wav),
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)],
                       check=True)
        shutil.rmtree(tmp, ignore_errors=True)
        if self.format == "long":
            print("sous-titres :", self.srt())
        self.copie_du_script()
        print("vidéo :", final, f"({self.duree:.1f} s)")
        return final

    def lancer(self):
        cmd = sys.argv[1] if len(sys.argv) > 1 else "video"
        if cmd == "tranche":
            self._tranche(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        elif cmd == "images":
            self.calculer()
            d = self.dossier / "out/images"
            d.mkdir(parents=True, exist_ok=True)
            for x in sys.argv[2:]:
                self.image(float(x)).save(d / f"t_{float(x):06.2f}.png")
            print("images dans", d, f"(durée totale {self.duree:.1f} s)")
        elif cmd == "son":
            out = self.dossier / "out"
            out.mkdir(exist_ok=True)
            print("mixage :", self.mixage(out / f"{self.slug}_mix.wav"))
        elif cmd == "miniature":
            print("miniature :", self.miniature())
        elif cmd == "chronologie":
            self.calculer()
            for r in self.repliques:
                print(f"{r.fichier.name:24s} {r.t0:6.2f} → {r.t0 + r.duree:6.2f}  " +
                      " | ".join(f"{r.t0 + d:.2f} {s[:28]}" for d, s in r.phrases))
            for s in self.scenes:
                print(f"scène {s.nom:16s} {s.a:6.2f} → {min(s.b, self.duree):6.2f}")
            print(f"durée totale : {self.duree:.2f} s")
        else:
            self.video()
            self.miniature()
