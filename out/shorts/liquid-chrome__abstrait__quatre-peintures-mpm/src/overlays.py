#!/usr/bin/env python3
"""
Overlays texte de l'identité Chrome Liquide (PNG RGBA 1080×1920) pour le pipeline Python (Taichi/OpenCV).
Mêmes tokens que la scène three.js : légende Inter 500 54 px interlettrage 0.2em (#C8D3FF),
titre Syne 800 92 px interlignage 1.0, interlettrage -0.03em, x = 72, légende y = 232, titre y = 306,
mot-clé en dégradé chrome #C8D3FF -> #FF9AE8 (45 %) -> #7CF7E4 (80 %) -> #FFE29A.
USAGE : .venv/bin/python out/shorts/<dossier>/src/overlays.py <dossier_sortie>
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'out' / 'tools'))
from textpng import font_path  # noqa: E402

W, H = 1080, 1920
X0, CAP_Y, TITLE_Y = 72, 232, 306
GRAD = [(0.0, '#C8D3FF'), (0.45, '#FF9AE8'), (0.80, '#7CF7E4'), (1.0, '#FFE29A')]


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def gradient(w):
    xs = np.linspace(0, 1, max(w, 2)); out = np.zeros((len(xs), 3), np.float32)
    for (a, ca), (b, cb) in zip(GRAD[:-1], GRAD[1:]):
        m = (xs >= a) & (xs <= b); k = ((xs[m] - a) / (b - a))[:, None]; out[m] = rgb(ca) * (1 - k) + rgb(cb) * k
    return out


def draw_tracked(d, x, y, s, f, fill, tr):
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + tr
    return x


def card(caption, lines, out, cap_color='#C8D3FF'):
    """lines : liste de lignes ; chaque ligne = liste de (texte, dégradé?)"""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fc = ImageFont.truetype(font_path('inter', 500), 54)
    if caption:
        draw_tracked(d, X0, CAP_Y, caption, fc, tuple(rgb(cap_color).astype(int)) + (255,), 54 * 0.2)
    ft = ImageFont.truetype(font_path('syne', 800), 92)
    tr = -0.03 * 92
    for i, parts in enumerate(lines):
        x, y = X0, TITLE_Y + i * 92
        for text, grad in parts:
            if not grad:
                x = draw_tracked(d, x, y, text, ft, (255, 255, 255, 255), tr)
            else:
                m = Image.new('L', (W, H), 0); dm = ImageDraw.Draw(m)
                x1 = draw_tracked(dm, x, y, text, ft, 255, tr)
                g = gradient(int(x1 - x)); layer = np.zeros((H, W, 4), np.uint8)
                layer[:, int(x):int(x) + g.shape[0], :3] = g[None].astype(np.uint8)
                layer[..., 3] = np.array(m)
                img = Image.alpha_composite(img, Image.fromarray(layer)); d = ImageDraw.Draw(img)
                x = x1
    # ombre portée douce pour la lisibilité AA sur les reflets
    a = np.array(img)
    sh = Image.fromarray(a[..., 3]).filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(10))
    shadow = np.zeros_like(a); shadow[..., :3] = (11, 11, 16); shadow[..., 3] = (np.array(sh) * 0.55).astype(np.uint8)
    img = Image.alpha_composite(Image.fromarray(shadow), img)
    img.save(out); print(out)


if __name__ == '__main__':
    od = Path(sys.argv[1] if len(sys.argv) > 1 else '.'); od.mkdir(parents=True, exist_ok=True)
    card('MATIÈRE · FLUIDE', [[('Quatre', False)], [('peintures', True)], [('tombent…', False)]], od / 'o1.png')
    card('SIMULATION MPM', [[('…et se', False)], [('mélangent.', True)]], od / 'o2.png')
    card('24 000 PARTICULES', [[('Hypnotique.', True)]], od / 'o3.png')
