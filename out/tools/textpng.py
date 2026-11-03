#!/usr/bin/env python3
"""
textpng.py — génère des overlays texte PNG RGBA plein cadre 1080×1920 avec les polices @fontsource
(PIL lit directement les .woff2). Sert aux pipelines Python (Manim sans Pango, Taichi, OpenCV, Matplotlib).

USAGE CLI
  python out/tools/textpng.py --text "Pourquoi le ciel est bleu ?" --font space-grotesk --weight 700 \
      --size 96 --color "#ffffff" --y 760 --maxw 840 --out title.png [--stroke 0 --stroke-color "#000"] \
      [--bg "#00000088" --pad 28 --radius 24] [--align center] [--tracking -2] [--x 540]

USAGE PYTHON
  from textpng import text_layer
  img = text_layer("Texte", font="inter", weight=800, size=90, color="#fff", y=800)   # PIL.Image RGBA 1080×1920

Règles : corps ≥ 54 px, titres ≥ 90 px ; garder le texte entre y=220 et y=1600, x ≤ 960 (zones sûres TikTok).
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H = 1080, 1920


def font_path(pkg, weight=400, style='normal', subset='latin'):
    p = ROOT / 'node_modules' / '@fontsource' / pkg / 'files' / f'{pkg}-{subset}-{weight}-{style}.woff2'
    if not p.exists():
        raise FileNotFoundError(p)
    return str(p)


def hex_rgba(h):
    h = h.lstrip('#')
    if len(h) == 6:
        h += 'ff'
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def wrap(draw, text, font, maxw, tracking=0):
    lines = []
    for para in text.split('\n'):
        words, cur = para.split(' '), ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if measure(draw, test, font, tracking) <= maxw or not cur:
                cur = test
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


def measure(draw, s, font, tracking=0):
    return draw.textlength(s, font=font) + tracking * max(0, len(s) - 1)


def draw_line(draw, x, y, s, font, fill, tracking=0, stroke=0, stroke_fill=None):
    if tracking == 0:
        draw.text((x, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        return
    for ch in s:
        draw.text((x, y), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += draw.textlength(ch, font=font) + tracking


def text_layer(text, font='inter', weight=700, size=90, color='#ffffff', y=800, x=None, maxw=840,
               align='center', stroke=0, stroke_color='#000000', bg=None, pad=24, radius=20,
               tracking=0, line_height=1.15, style='normal', canvas=None):
    img = canvas if canvas is not None else Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(font_path(font, weight, style), size)
    lines = wrap(d, text, f, maxw, tracking)
    lh = int(size * line_height)
    widths = [measure(d, l, f, tracking) for l in lines]
    block_w, block_h = max(widths), lh * len(lines)
    cx = x if x is not None else (W - 120) / 2 + 30  # centre de la zone sûre horizontale (60..960)
    if bg:
        bx0 = cx - block_w / 2 - pad if align == 'center' else cx - pad
        d.rounded_rectangle([bx0, y - pad, bx0 + block_w + 2 * pad, y + block_h + pad * 0.6], radius=radius, fill=hex_rgba(bg))
    for i, (l, w) in enumerate(zip(lines, widths)):
        lx = cx - w / 2 if align == 'center' else (cx if align == 'left' else cx - w)
        draw_line(d, lx, y + i * lh, l, f, hex_rgba(color), tracking, stroke, hex_rgba(stroke_color))
    return img


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--text', required=True); p.add_argument('--font', default='inter')
    p.add_argument('--weight', type=int, default=700); p.add_argument('--size', type=int, default=90)
    p.add_argument('--color', default='#ffffff'); p.add_argument('--y', type=int, default=800)
    p.add_argument('--x', type=float); p.add_argument('--maxw', type=int, default=840)
    p.add_argument('--align', default='center'); p.add_argument('--stroke', type=int, default=0)
    p.add_argument('--stroke-color', default='#000000'); p.add_argument('--bg'); p.add_argument('--pad', type=int, default=24)
    p.add_argument('--radius', type=int, default=20); p.add_argument('--tracking', type=float, default=0)
    p.add_argument('--style', default='normal'); p.add_argument('--out', required=True)
    a = p.parse_args()
    text_layer(a.text, a.font, a.weight, a.size, a.color, a.y, a.x, a.maxw, a.align, a.stroke, a.stroke_color,
               a.bg, a.pad, a.radius, a.tracking, style=a.style).save(a.out)
    print(a.out)


if __name__ == '__main__':
    main()
