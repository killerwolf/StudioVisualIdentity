"""Briques du design system (papier découpé, à adapter : STYLE_GUIDE.md § 2) : couleurs, polices, pièces de papier, pose, mouvement.

Tout est déterministe (graines fixes) pour que deux rendus donnent la même image.
Une « pièce » est un couple (image RGBA, marge) : l'image contient l'ombre, la marge sert au calage.
"""
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = Path(__file__).resolve().parent.parent
STOP = 12                      # stop-motion : 12 images de mouvement par seconde

# ---------- couleurs (reprises du design system d'origine ; à remplacer par celles de {{DESIGN_SYSTEM}}) ----------
MAT, MAT_DEEP = (31, 90, 74), (23, 73, 59)
PAPER, WHITE, INK, INK_SOFT = (247, 244, 236), (255, 255, 255), (16, 35, 29), (61, 79, 73)
BLUE, RED, YELLOW = (47, 92, 245), (228, 67, 45), (255, 210, 63)
PINK, CYAN, KRAFT, MUTED = (255, 158, 199), (127, 227, 214), (201, 154, 91), (185, 205, 196)

# ---------- polices ----------
_POLICES = {"display": "DelaGothicOne-Regular.woff2", "hand": "Kalam-Bold.woff2",
            "hand-r": "Kalam-Regular.woff2", "mono": "DMMono-Medium.woff2", "mono-r": "DMMono-Regular.woff2"}
_cache_polices = {}

# ---------- thème d'essai (phase 1 : planches de design) ----------
# THEME_ESSAI=<fichier.json> remplace couleurs, polices et style de tapis, sans toucher au design validé.
TAPIS = "grille"                 # grille (tapis de découpe) | kraft (papier brun) | nuit (fond sombre uni)
if __import__("os").environ.get("THEME_ESSAI"):
    import json as _json
    _t = _json.loads(Path(__import__("os").environ["THEME_ESSAI"]).read_text(encoding="utf-8"))
    for _k, _v in _t.get("couleurs", {}).items():
        globals()[_k] = tuple(_v)
    _POLICES.update(_t.get("polices", {}))   # chemin relatif à assets/fonts, ou absolu
    TAPIS = _t.get("tapis", TAPIS)


def police(nom, taille):
    k = (nom, taille)
    if k not in _cache_polices:
        _cache_polices[k] = ImageFont.truetype(str(RACINE / "assets/fonts" / _POLICES[nom]), taille)
    return _cache_polices[k]


def texte(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def lignes(s, f, largeur):
    """Coupe un texte en lignes qui tiennent dans `largeur` pixels."""
    mots, out, cur = s.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if f.getlength(essai) <= largeur or not cur:
            cur = essai
        else:
            out.append(cur)
            cur = m
    out.append(cur)
    return out


# ---------- papier ----------
_grain = None


def grain(w, h):
    global _grain
    if _grain is None or _grain.shape[0] < h or _grain.shape[1] < w:
        r = np.random.default_rng(7)
        g = r.normal(0, 1, (max(h, 1200), max(w, 1200))).astype(np.float32)
        _grain = cv2.GaussianBlur(g, (0, 0), 0.8)
    return _grain[:h, :w]


def coupe(w, h, seed):
    """Contour légèrement irrégulier (coup de ciseaux)."""
    r = np.random.default_rng(seed)
    j = lambda a: a * (0.4 + r.random())
    return [(j(3), j(4)), (w * 0.38, j(2)), (w - j(5), j(3)), (w - j(1), h * 0.52),
            (w - j(4), h - j(4)), (w * 0.61, h - j(1)), (j(5), h - j(3)), (j(1), h * 0.47)]


def papier(w, h, fill, seed=1, ombre=1.0, contenu=None):
    """Pièce de papier (RGBA, ombre portée comprise). Renvoie (image, marge)."""
    m = 40
    img = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    masque = Image.new("L", (w, h), 0)
    ImageDraw.Draw(masque).polygon(coupe(w, h, seed), fill=255)
    if ombre:
        sh = Image.new("L", img.size, 0)
        sh.paste(masque, (m + int(9 * ombre), m + int(14 * ombre)))
        sh = sh.filter(ImageFilter.GaussianBlur(9 * ombre)).point(lambda v: int(v * 0.42))
        img.putalpha(sh)
    face = np.empty((h, w, 3), np.float32)
    face[:] = fill
    face *= (1 + 0.035 * grain(w, h))[..., None]
    piece = Image.fromarray(np.clip(face, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    if contenu is not None:
        piece.alpha_composite(contenu)
    piece.putalpha(masque)
    img.alpha_composite(piece, (m, m))
    return img, m


def bande(s, nom="display", taille=78, fill=PAPER, ink=INK, pad=(36, 22), seed=1):
    """Bande de papier avec quelques mots (les titres en display sont en majuscules)."""
    f = police(nom, taille)
    if nom == "display":
        s = s.upper()
    x0, y0, x1, y1 = f.getbbox(s)
    w, h = (x1 - x0) + 2 * pad[0], (y1 - y0) + 2 * pad[1]
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    texte(ImageDraw.Draw(c), (w // 2, h // 2), s, f, ink, "mm")
    return papier(w, h, fill, seed, contenu=c)


def carte(titre, sous=None, w=440, h=200, fill=PAPER, ink=INK, seed=3, eyebrow=None, taille=46):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    y = 26
    if eyebrow:
        texte(d, (30, y), eyebrow, police("mono", 24), ink if fill != PAPER else INK_SOFT)
        y += 42
    texte(d, (30, y), titre.upper(), police("display", taille), ink)
    y += taille + 22
    if sous:
        for l in lignes(sous, police("hand", 34), w - 60):
            texte(d, (30, y), l, police("hand", 34), ink if fill != PAPER else INK_SOFT)
            y += 40
    return papier(w, h, fill, seed, contenu=c)


def sticky(s, fill=YELLOW, w=300, h=230, taille=44, seed=5):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, w, int(h * 0.16)), fill=(0, 0, 0, 20))
    f = police("hand", taille)
    ls = lignes(s, f, w - 40)
    y = h * 0.58 - len(ls) * taille * 0.62
    for l in ls:
        texte(d, (w // 2, y), l, f, INK, "ma")
        y += taille * 1.22
    return papier(w, h, fill, seed, contenu=c)


def cadre(img, bord=14, fill=PAPER):
    """Photo ou vidéo posée sur le tapis : bord papier, grande ombre."""
    w, h = img.size
    tot = Image.new("RGBA", (w + 2 * bord, h + 2 * bord), fill + (255,))
    tot.paste(img.convert("RGB"), (bord, bord))
    m = 60
    out = Image.new("RGBA", (tot.width + 2 * m, tot.height + 2 * m), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).rectangle((m, m + 30, m + tot.width, m + tot.height + 18), fill=130)
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(26)))
    out.alpha_composite(tot, (m, m))
    return out, m


# ---------- pose sur l'image ----------
_cache_rot = {}
CAMERA = None        # (zoom, centre x, centre y, largeur, hauteur, décalage x, décalage y) : posé par le moteur (vidéo de danse)


def poser(fond, piece, cx, cy, angle=0.0, echelle=1.0, cle=None):
    """Colle une pièce centrée en (cx, cy), tournée et mise à l'échelle (cache si `cle`)."""
    img, _ = piece
    if CAMERA is not None:               # caméra : on zoome la scène autour de son centre, les pièces restent nettes
        z, ccx, ccy, W, H, ddx, ddy = CAMERA
        cx, cy, echelle = W / 2 + (cx - ccx) * z + ddx, H / 2 + (cy - ccy) * z + ddy, echelle * z
    if echelle <= 0.01:
        return
    k = (cle, round(angle, 2), round(echelle, 3)) if cle is not None else None
    if k is not None and k in _cache_rot:
        im = _cache_rot[k]
    else:
        im = img
        if echelle != 1:
            im = im.resize((max(1, int(im.width * echelle)), max(1, int(im.height * echelle))), Image.LANCZOS)
        if angle:
            im = im.rotate(angle, Image.BICUBIC, expand=True)
        if k is not None:
            _cache_rot[k] = im
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(im.width, fond.width - x), min(im.height, fond.height - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) == (0, 0, im.width, im.height):
        fond.alpha_composite(im, (x, y))
    else:
        fond.alpha_composite(im.crop((x0, y0, x1, y1)), (x + x0, y + y0))


# ---------- mouvement en stop-motion ----------
def tq(t):
    """Temps arrondi au pas du stop-motion."""
    return math.floor(t * STOP) / STOP


def pop(t, t0):
    """0 → 1,15 → 0,96 → 1 en 4 pas."""
    if t < t0:
        return 0.0
    i = int((t - t0) * STOP)
    return [0.35, 1.15, 0.96, 1.0][i] if i < 4 else 1.0


def depose(t, t0):
    """Pièce simplement déposée (rythme calme) : (échelle, décalage vertical) en 3 pas, sans rebond."""
    if t < t0:
        return 0.0, 0.0
    i = int((t - t0) * STOP)
    return ([1.04, 1.015, 1.0][i], [-14.0, -4.0, 0.0][i]) if i < 3 else (1.0, 0.0)


def glisse(t, t0, de, a, n=5):
    """Interpolation de `de` à `a` en n pas (avec ralenti à l'arrivée)."""
    if t < t0:
        return de
    k = min(1.0, math.floor((t - t0) * STOP + 1) / n)
    return de + (a - de) * (1 - (1 - k) ** 2)


def frisson(t, seed):
    """Petit tremblement (personnage « vivant »), change à chaque pas du stop-motion."""
    r = np.random.default_rng(int(t * STOP) * 97 + seed)
    return int(r.integers(-2, 3)), int(r.integers(-2, 3)), float((r.random() - 0.5) * 0.5)


# ---------- fond : tapis de découpe ----------
def tapis(W, H):
    a = np.empty((H, W, 3), np.float32)
    a[:] = MAT
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.28 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2.2)[..., None]
    a *= (1 + 0.025 * np.random.default_rng(3).normal(0, 1, (H, W)).astype(np.float32))[..., None]
    if TAPIS == "kraft":                 # papier brun : fibres, sans grille
        f = cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 3)
        a *= (1 + 0.05 * f)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    if TAPIS != "grille":
        return img
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    p = 27
    for x in range(0, W, p):
        fort = x % (5 * p) == 0
        d.line([(x, 0), (x, H)], fill=(220, 255, 235, 51 if fort else 20), width=2 if fort else 1)
    for y in range(0, H, p):
        fort = y % (5 * p) == 0
        d.line([(0, y), (W, y)], fill=(220, 255, 235, 51 if fort else 20), width=2 if fort else 1)
    for i, x in enumerate(range(0, W, 5 * p)):
        texte(d, (x + 6, 8), str(i * 5), police("mono-r", 18), (220, 255, 235, 70))
    img.alpha_composite(calque)
    return img


# ---------- vidéos insérées ----------
class Lecteur:
    """Lit une vidéo vers l'avant, image par image, recadrée et redimensionnée."""

    def __init__(self, chemin, debut, taille, recadre=None):
        self.chemin, self.debut, self.taille, self.recadre = chemin, debut, taille, recadre
        self.cap = cv2.VideoCapture(str(chemin))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.cap.set(cv2.CAP_PROP_POS_MSEC, debut * 1000)
        self.idx = int(round(debut * self.fps)) - 1
        self.img = None

    def image(self, temps_source):
        cible = int(temps_source * self.fps)
        if cible < self.idx - 1:                         # retour en arrière : on rouvre
            self.__init__(self.chemin, max(0.0, temps_source), self.taille, self.recadre)
        while self.idx < cible or self.img is None:
            ok, fr = self.cap.read()
            if not ok:
                break
            self.idx += 1
            if self.recadre:
                x, y, w, h = self.recadre
                fr = fr[y:y + h, x:x + w]
            fr = cv2.resize(fr, self.taille, interpolation=cv2.INTER_AREA)
            self.img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        return self.img
