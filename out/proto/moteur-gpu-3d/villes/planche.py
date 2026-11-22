#!/usr/bin/env python3
"""planche.py — planche des trois villes : 2 images par ville, le nom sous chaque paire.
    ../.venv/bin/python planche.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICI = Path(__file__).resolve().parent
VILLES = [('paris', 'Paris'), ('newyork', 'New York'), ('tokyo', 'Tokyo')]
W, H, G, LAB = 405, 720, 14, 64

font = ImageFont.load_default(size=38)
out = Image.new('RGB', (3 * (2 * W + G) + 4 * 2 * G, H + LAB + 2 * G), '#1b1b1f')
d = ImageDraw.Draw(out)
x = 2 * G
for cid, nom in VILLES:
    for k, t in enumerate(('1.00', '3.80')):
        im = Image.open(ICI / 'sortie' / f'{cid}_{t}s.png').convert('RGB').resize((W, H), Image.LANCZOS)
        out.paste(im, (x + k * (W + G), G))
    tw = d.textlength(nom, font=font)
    d.text((x + (2 * W + G - tw) / 2, H + G + 10), nom, fill='#f2f2f2', font=font)
    x += 2 * W + G + 2 * G
out.save(ICI / 'planche-villes.jpg', quality=90)
print(ICI / 'planche-villes.jpg', out.size)
