#!/usr/bin/env python3
"""
thumb.py — bannière du haut du README : out/demo/thumb/hero_fr.jpg (2560×1280) et hero_fr_1280.jpg (1280×640).

USAGE (depuis la racine du dépôt) : .venv/bin/python out/demo/thumb.py

Un mur incliné, en perspective, de 18 vraies images : une par identité, tirée de son short (aucun cache nécessaire, les images
sont lues directement dans out/shorts/*/short.mp4). À gauche, la promesse en trois lignes. Fond sombre, bord sombre : la
bannière tient sur les deux thèmes de GitHub. Mêmes polices et mêmes outils de dessin que la vidéo (build.py).
"""
import math, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa: E402

W, H = 2560, 1280
TITLE = [('Un prompt.', '#FFFFFF'), ('18 styles.', B.YEL), ('Votre chaîne.', '#FFFFFF')]
# ordre du mur (6 colonnes × 3 rangées) : clairs et sombres alternés, les plus parlants près du titre
WALL = ['gazette-1900', 'pixel-arcade', 'pastel-diorama', 'brut-meme', 'carte-meteo', 'cosmos-doc',
        'neon-lab', 'trait-continu', 'survol-pixel', 'swiss-data', 'tableau-craie', 'aquarelle-conte',
        'bauhaus-kinetic', 'topo-relief', 'riso-zine', 'liquid-chrome', 'atlas-grave', 'papier-decoupe']
# instant choisi dans chaque short (s) : une image lisible et typique
AT = {'gazette-1900': 6.5, 'pixel-arcade': 6.0, 'pastel-diorama': 12.5, 'brut-meme': 2.4, 'carte-meteo': 9.0, 'cosmos-doc': 12.6,
      'neon-lab': 9.0, 'trait-continu': 8.0, 'survol-pixel': 5.0, 'swiss-data': 3.0, 'tableau-craie': 12.0, 'aquarelle-conte': 8.0,
      'bauhaus-kinetic': 1.0, 'topo-relief': 4.0, 'riso-zine': 1.5, 'liquid-chrome': 8.0, 'atlas-grave': 12.0, 'papier-decoupe': 9.0}


def frame(ident):
    short = B.IDS[B.IDX[ident]][2]
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(AT[ident]), '-i', str(B.SHORTS / short / 'short.mp4'), '-frames:v', '1',
                          '-vf', 'scale=540:960:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(960, 540, 3)


def hero():
    assert len(WALL) == 18 and set(WALL) == set(r[0] for r in B.IDS)
    B.W, B.H = W, H
    cols, rows, pw, ph, tw, th = 6, 3, 470, 800, 430, 764
    cw, chh = cols * pw, rows * ph
    can = np.empty((chh, cw, 3), np.uint8)
    can[:] = B.rgb(B.DARK)
    for j, ident in enumerate(WALL):
        c, r = j % cols, j // cols
        img = cv2.resize(frame(ident), (tw, th), interpolation=cv2.INTER_AREA)
        x, y = c * pw + (pw - tw) // 2, r * ph + (ph - th) // 2
        B.blit(can, B.shadow(tw, th, 34, 22, 190), x - 66, y - 66 + 26)
        B.blit(can, B.card_rgba(img, 34), x, y)
    big = np.tile(can, (3, 3, 1))
    ang = math.radians(-9)
    c_, s_ = math.cos(ang), math.sin(ang)
    z = 0.66
    A = np.array([[c_ * z, -s_ * z, 0], [s_ * z, c_ * z, 0], [0, 0, 1]], np.float64)
    Tc = np.array([[1, 0, -cw * 1.5 - 120], [0, 1, -chh * 1.5 + 60], [0, 0, 1]], np.float64)
    Pm = np.array([[1, 0, 0], [0, 1, 0], [-0.00012, -0.00012, 1]], np.float64)
    Tb = np.array([[1, 0, W * 0.765], [0, 1, H * 0.50], [0, 0, 1]], np.float64)
    fr = cv2.warpPerspective(big, Tb @ Pm @ A @ Tc, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=B.rgb(B.DARK))
    # voile sombre à gauche (le titre) et léger assombrissement des bords
    x = np.linspace(0, 1, W)[None, :, None]
    al = np.clip(1.86 - x * 2.9, 0, 1) ** 1.3 * 0.98
    fr = (fr * (1 - al) + np.array(B.rgb('#07080F'), np.float32) * al).astype(np.uint8)
    B.blitc(fr, B.glow(1800, '#2B3BFF'), 380, 200, 0.22)
    B.blitc(fr, B.glow(1500, '#FF3DCB'), 300, 1250, 0.12)
    # le titre
    size = 150
    y = 300
    for txt, col in TITLE:
        s = B.Tt(txt, ('unbounded', 900), size, col)
        B.blit(fr, B.Tt(txt, ('unbounded', 900), size, '#05060B'), 130 + 8, y + 10)
        B.blit(fr, s, 130, y)
        y += 250
    fr = cv2.multiply(fr, B.vignette(W, H), dtype=cv2.CV_8U)
    out = B.HERE / 'thumb'
    out.mkdir(exist_ok=True)
    im = Image.fromarray(fr)
    im.save(out / 'hero_fr.jpg', quality=86, optimize=True, progressive=True)
    im.resize((1280, 640), Image.LANCZOS).save(out / 'hero_fr_1280.jpg', quality=90, optimize=True, progressive=True)
    for f in ('hero_fr.jpg', 'hero_fr_1280.jpg'):
        print(out / f, f'{(out / f).stat().st_size / 1024:.0f} Ko')


if __name__ == '__main__':
    hero()
