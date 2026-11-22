#!/usr/bin/env python3
"""
planche.py — planche de comparaison source / maquette : 5 instants, vue entière et crop à 100 % de chacun.

La vidéo source reste hors dépôt ; ses images ne servent que dans cette planche.
  ../.venv/bin/python planche.py /chemin/source_1080.mp4
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ICI = Path(__file__).resolve().parent
# (instant source, coin du crop source, instant maquette, coin du crop maquette) ; crops de 480×480 à 100 %
PAIRES = [(3.5, (330, 520), 0.5, (0, 520)), (5.0, (60, 560), 1.5, (120, 560)), (0.5, (120, 60), 2.5, (300, 1000)),
          (11.0, (0, 0), 3.5, (160, 900)), (2.0, (120, 30), 4.5, (300, 700))]
C, H, G, TOP = 480, 480, 12, 34


def main(src):
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for ts, cs, tm, cm in PAIRES:
            f = Path(tmp) / f's_{ts}.png'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ts), '-i', src, '-frames:v', '1', str(f)], check=True)
            s = Image.open(f).convert('RGB')
            m = Image.open(ICI / 'sortie' / f'still_{tm:.2f}s.png').convert('RGB')
            sw = round(s.width * H / s.height)
            mw = round(m.width * H / m.height)
            row = Image.new('RGB', (sw + C + mw + C + 5 * G, H + TOP), '#1b1b1f')
            d = ImageDraw.Draw(row)
            x = G
            for im, label in ((s.resize((sw, H), Image.LANCZOS), f'source {ts:.1f} s'),
                              (s.crop((cs[0], cs[1], cs[0] + C, cs[1] + C)), 'source, crop 100 %'),
                              (m.resize((mw, H), Image.NEAREST), f'maquette {tm:.1f} s'),
                              (m.crop((cm[0], cm[1], cm[0] + C, cm[1] + C)), 'maquette, crop 100 %')):
                row.paste(im, (x, TOP))
                d.text((x, 10), label, fill='#f2f2f2')
                x += im.width + G
            rows.append(row)
    out = Image.new('RGB', (rows[0].width, sum(r.height for r in rows) + G), '#1b1b1f')
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    out.save(ICI / 'planche-source-maquette.jpg', quality=90)
    print(ICI / 'planche-source-maquette.jpg', out.size)


if __name__ == '__main__':
    main(sys.argv[1])
