#!/usr/bin/env python3
"""Prototype d'images fixes « Lyrics punchy » (validation de la direction, PAS le moteur de rendu).

Dessine 5 images 1080×1920 avec Pillow pour vérifier : la colonne justifiée par l'axe de largeur d'Anybody,
le mur en camaïeu, le carton d'illustration, le mode plaque sur un fond plein cadre et les zones sûres.
Les textes sont du REMPLISSAGE écrit par nous (en français), pas les paroles d'une chanson.

    uv run --python 3.11 --with pillow python proto_frames.py /chemin/vers/Anybody[wdth,wght].ttf [dossier_sortie]

Police : Anybody (SIL OFL 1.1), fichier variable de github.com/google/fonts (ofl/anybody). Non versionnée ici :
le moteur final la prend dans @fontsource-variable/anybody.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = sys.argv[1]
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent)
K = 2                                  # suréchantillonnage
W, H = 1080, 1920
X0, X1 = 64, 940                       # colonne de texte (876 px)
COL = X1 - X0

CAMAIEUX = {
    'nuit':   dict(bg='#2A1160', mur=['#B9A4F5', '#8468DB', '#5F45B8'], accent='#E6FF4F', encre='#140A33'),
    'lagon':  dict(bg='#063F4A', mur=['#8FD9DC', '#4FA9B0', '#2F8791'], accent='#FF8A5C', encre='#04252C'),
    'braise': dict(bg='#5E0F2C', mur=['#F2A5B5', '#D0708A', '#A64A66'], accent='#FFD166', encre='#33061A'),
}
CREME = '#FFF6E5'


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    c = [v / 255 for v in rgb(h)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


_cache = {}


def police(size, wdth, wght):
    key = (round(size), round(wdth), wght)
    if key not in _cache:
        f = ImageFont.truetype(FONT, round(size * K))
        f.set_variation_by_axes([wdth, wght])      # ordre des axes du fichier : wdth, wght
        _cache[key] = f
    return _cache[key]


def largeur(txt, size, wdth, wght):
    return police(size, wdth, wght).getlength(txt) / K


def ajuster(txt, wght, smin, smax, cible=COL):
    """Taille puis axe de largeur pour remplir exactement la colonne. Retourne (taille, wdth, largeur)."""
    size = max(smin, min(smax, smax * cible / largeur(txt, smax, 100, wght)))
    lo, hi = 50, 150
    for _ in range(12):
        mid = (lo + hi) / 2
        if largeur(txt, size, mid, wght) > cible:
            hi = mid
        else:
            lo = mid
    wd = round(lo)
    while largeur(txt, size, wd, wght) > cible and size > smin:   # encore trop large à wdth 50 : on réduit
        size -= 2
    return size, wd, largeur(txt, size, wd, wght)


class Toile:
    def __init__(self, bg):
        self.im = Image.new('RGB', (W * K, H * K), bg)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x0, y0, x1, y1, fill, r=0):
        self.d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], radius=r * K, fill=fill)

    def rond(self, cx, cy, r, fill):
        self.d.ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], fill=fill)

    def texte(self, x, y, txt, size, wdth, wght, fill):
        """y = haut des capitales."""
        f = police(size, wdth, wght)
        top = f.getbbox('H')[1]
        self.d.text((x * K, y * K - top), txt, font=f, fill=fill)

    def hauteur_cap(self, size, wdth, wght):
        b = police(size, wdth, wght).getbbox('H')
        return (b[3] - b[1]) / K

    def coller(self, calque, angle, cx, cy):
        r = calque.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.im.paste(r, (round(cx * K - r.width / 2), round(cy * K - r.height / 2)), r)

    def sauver(self, nom):
        self.im.resize((W, H), Image.LANCZOS).save(OUT / nom, quality=92)
        print('écrit', OUT / nom)


def compteur(t, cam, temps_actif):
    """4 points en haut à gauche : le temps de la mesure en cours."""
    for i in range(4):
        t.rond(64 + 13 + i * 40, 262, 13, cam['accent'] if i == temps_actif else cam['mur'][2])


def mur(t, cam, lignes, bas=800, estompe=False):
    """Lignes passées, la plus récente en bas, justifiées, de plus en plus proches du fond."""
    y = bas
    for i, txt in enumerate(lignes[:4]):
        size, wd, _ = ajuster(txt, 800, 56, 118)
        hc = t.hauteur_cap(size, wd, 800)
        y -= hc
        ton = cam['mur'][min(2, i + (1 if estompe else 0))] if i < 3 else cam['mur'][2]
        t.texte(X0, y, txt, size, wd, 800, ton)
        y -= 26


def bloc_vivant(t, cam, rangs, accent_rang, haut=850, plaque=False, smax=250):
    """Ligne en cours : 1 à 3 rangs justifiés ; l'unité qui vient de tomber est en couleur d'accent."""
    y = haut
    for i, txt in enumerate(rangs):
        size, wd, lw = ajuster(txt, 900, 120, smax)
        hc = t.hauteur_cap(size, wd, 900)
        if plaque:
            t.rect(X0 - 18, y - 20, X0 + lw + 18, y + hc + 20, cam['encre'], r=14)
        t.texte(X0, y, txt, size, wd, 900, cam['accent'] if i == accent_rang else CREME)
        y += hc + (48 if plaque else 34)
    return y


def carton(cam, dessin, taille=440):
    """Carton d'illustration : carré couleur d'accent, pictogramme encre + crème + une seule couleur vraie."""
    c = Image.new('RGBA', (taille * K, taille * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, taille * K - 1, taille * K - 1], radius=36 * K, fill=cam['accent'])
    g = Image.new("RGBA", (500 * K, 500 * K), (0, 0, 0, 0)); dessin(ImageDraw.Draw(g), cam, 500); g = g.resize((taille * K, taille * K), Image.LANCZOS); c.alpha_composite(g)
    return c


def picto_plan_mode(d, cam, T):
    R = lambda x0, y0, x1, y1, f, r=0: d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], radius=r * K, fill=f)
    R(50, 54, 450, 150, cam['encre'], 48)                       # pastille « PLAN MODE »
    f = police(58, 78, 900)
    d.text((84 * K, 76 * K - f.getbbox('H')[1] + 6 * K), 'PLAN MODE', font=f, fill=CREME)
    for i in range(3):                                           # liste à cocher, 2 lignes cochées
        y = 200 + i * 86
        R(50, y, 106, y + 56, cam['encre'], 10)
        if i < 2:
            d.line([(62 * K, (y + 30) * K), (76 * K, (y + 44) * K), (96 * K, (y + 14) * K)], fill=CREME, width=9 * K, joint='curve')
        R(134, y + 10, 134 + (300, 230, 270)[i], y + 46, cam['encre'], 8)


def picto_serveur(d, cam, T):
    R = lambda x0, y0, x1, y1, f, r=0: d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], radius=r * K, fill=f)
    for i in range(3):                                           # 3 tiroirs de baie
        y = 70 + i * 104
        R(60, y, 440, y + 84, cam['encre'], 14)
        for j in range(3):
            R(250 + j * 56, y + 30, 290 + j * 56, y + 54, '#5B3A46' if i == 1 else CREME, 6)
        col = '#FF3B3B' if i == 1 else CREME                     # une seule couleur vraie : la diode rouge
        d.ellipse([92 * K, (y + 24) * K, 128 * K, (y + 60) * K], fill=col)
    f = police(74, 78, 900)                                      # « 503 » sous la baie
    d.text((60 * K, 396 * K - f.getbbox('H')[1]), '503', font=f, fill=cam['encre'])
    d.line([(300 * K, 400 * K), (360 * K, 450 * K)], fill='#FF3B3B', width=16 * K)
    d.line([(360 * K, 400 * K), (300 * K, 450 * K)], fill='#FF3B3B', width=16 * K)


def zones(t):
    """Calque de contrôle : zones de l'interface TikTok (rouge) et colonne utile (trait blanc)."""
    o = Image.new('RGBA', t.im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    for box in ([0, 0, W, 220], [0, H - 360, W, H], [W - 140, 0, W, H]):
        d.rectangle([v * K for v in box], fill=(255, 40, 40, 70))
    d.rectangle([X0 * K, 240 * K, X1 * K, 1560 * K], outline=(255, 255, 255, 230), width=3 * K)
    d.line([(X0 * K, 820 * K), (X1 * K, 820 * K)], fill=(255, 255, 255, 230), width=2 * K)
    t.im = Image.alpha_composite(t.im.convert('RGBA'), o).convert('RGB')
    t.d = ImageDraw.Draw(t.im)


def main():
    for nom, c in CAMAIEUX.items():
        print(nom, 'crème', contraste(CREME, c['bg']), 'accent', contraste(c['accent'], c['bg']),
              'mur', [contraste(m, c['bg']) for m in c['mur']], 'crème/encre', contraste(CREME, c['encre']),
              'encre/accent', contraste(c['encre'], c['accent']))

    # 1 — refrain, camaïeu « nuit » : le mur est encore vide, la ligne se construit rang par rang
    cam = CAMAIEUX['nuit']
    t = Toile(cam['bg'])
    compteur(t, cam, 2)
    bloc_vivant(t, cam, ['TOUT EST', 'DANS', 'LE PLAN'], 2)
    t.sauver('frame-1-refrain-nuit.jpg')

    # 2 — couplet, camaïeu « lagon » : mur de 3 lignes passées + carton « plan mode »
    cam = CAMAIEUX['lagon']
    t = Toile(cam['bg'])
    compteur(t, cam, 0)
    mur(t, cam, ['TOUT EST DANS LE PLAN', 'ENCORE UN REFRAIN', 'TEXTE DE REMPLISSAGE', 'PAS LES VRAIES PAROLES'], estompe=True)
    t.coller(carton(cam, picto_plan_mode), -4, 712, 476)
    bloc_vivant(t, cam, ['LE MATIN', 'EN PLAN', 'MODE'], 2)
    t.sauver('frame-2-plan-mode-lagon.jpg')
    zones(t)
    t.sauver('frame-2b-zones-sures.jpg')

    # 3 — camaïeu « braise » : carton « serveur en panne »
    cam = CAMAIEUX['braise']
    t = Toile(cam['bg'])
    compteur(t, cam, 3)
    mur(t, cam, ['LÀ DEPUIS LA 2.0', 'DES LIGNES, PAS DU CODE', 'LE MATIN EN PLAN MODE'], estompe=True)
    t.coller(carton(cam, picto_serveur), 3, 712, 476)
    bloc_vivant(t, cam, ['SERVEUR', 'EN PANNE'], 1)
    t.sauver('frame-3-serveur-braise.jpg')

    # 4 — exemple générique de la bibliothèque : « France » = fond tricolore plein cadre, texte en mode plaque
    cam = CAMAIEUX['nuit']
    t = Toile('#1F3FBF')
    t.rect(360, 0, 720, H, '#F4F1EA')
    t.rect(720, 0, W, H, '#E1262D')
    bloc_vivant(t, cam, ['TOUTE LA', 'FRANCE', 'CHANTE'], 1, haut=820, plaque=True, smax=230)
    t.sauver('frame-4-fond-france-plaque.jpg')


main()
