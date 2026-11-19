#!/usr/bin/env python3
"""
test_jersey_grid.py — test de non-régression de la grille des polices Jersey (correctif C8 du challenge).

Pour Jersey 10 / 15 / 20 (@fontsource 5.3.0, sous-ensemble latin) rendues par PIL sans anticrénelage (fontmode "1")
aux tailles natives du moteur (56/3, 27, 34 px/em) sur une origine entière :
  1. pour chaque glyphe, le nombre de pixels encrés = aire du contour (fontTools AreaPen sur le .woff) / pas² ;
  2. pour une ligne entière, l'encre totale = somme des encres de ses glyphes (aucun crénage ne déplace un pixel).
Sortie non nulle en cas d'écart. Usage : .venv/bin/python <src>/test_jersey_grid.py
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'node_modules' / '@fontsource'
SIZES = {10: 56 / 3, 15: 27, 20: 34}
GLYPHS = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
          'éèêëàâîïôûùüçÉÈÊÀÂÎÏÔÛÙÇœŒ«»’.,:;!?\'-')
LINES = ["UN ANNEAU EN PLEINE MER ?", "LES INCAS BÂTISSENT", "marches : convention de dessin", "RÉVÉLÉE AU MONDE"]


def ink(font, s):
    w = int(font.getlength(s)) + 8
    im = Image.new('1', (w, 60), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((2, 2), s, font=font, fill=1)
    return int(np.array(im, bool).sum())


def main():
    bad = 0
    for n, size in SIZES.items():
        stem = f'jersey-{n}-latin-400-normal'
        tt = TTFont(str(BASE / f'jersey-{n}' / 'files' / f'{stem}.woff'))
        upm = tt['head'].unitsPerEm
        step = upm / size                     # unités de police par pixel natif (75, 50, 38)
        gs = tt.getGlyphSet()
        cmap = tt.getBestCmap()
        font = ImageFont.truetype(str(BASE / f'jersey-{n}' / 'files' / f'{stem}.woff2'), size)
        ok = 0
        for ch in GLYPHS:
            g = cmap.get(ord(ch))
            if g is None:
                print(f'Jersey {n}: glyphe absent {ch!r}'); bad += 1; continue
            pen = AreaPen(gs)
            gs[g].draw(pen)
            expect = abs(pen.value) / step ** 2
            got = ink(font, ch)
            if abs(got - expect) > 0.5:
                print(f'Jersey {n}: {ch!r} encre {got} ≠ contour {expect:.2f}'); bad += 1
            else:
                ok += 1
        for line in LINES:
            tot = ink(font, line)
            parts = sum(ink(font, c) for c in line if c != ' ')
            if tot != parts:
                print(f'Jersey {n}: ligne « {line} » {tot} ≠ somme des glyphes {parts}'); bad += 1
        print(f'Jersey {n} (size {size:.3f}, pas {step:.1f} unités) : {ok}/{len(GLYPHS)} glyphes exacts')
    print('OK' if bad == 0 else f'ÉCHEC : {bad} écart(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
