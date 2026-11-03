#!/usr/bin/env python3
"""
textures.py — textures gravées de l'identité « Atlas Gravé » (pycairo + numpy), 100 % générées par code.

USAGE  .venv/bin/python textures.py <dossier_sortie> [--seed 7]
Produit (PNG) :
  paper.png     1080×1920 RGB   papier vergé : fond crème, nuages de pâte, grain, vergeures + pontuseaux, rousseurs
  vignette.png  1080×1920 RGBA  vignettage sépia (posé au-dessus de tout)
  frame.png     1080×1920 RGBA  cadre de planche : double filet + bordure graduée noir/blanc + écoinçons
  cartouche.png 920×300   RGBA  cartouche guilloché (lignes trochoïdales entrelacées) pour légendes/dates
  compass.png   420×420   RGBA  rose des vents 16 pointes, demi-pointes hachurées, nord rouge
  sea.png       1080×1920 RGBA  mer gravée : lignes horizontales ondulées (taille-douce)
  ship.png      220×220   RGBA  caravelle gravée (coque hachurée, 3 mâts)
Déterministe : même graine -> mêmes PNG.
"""
import sys, math
from pathlib import Path
import numpy as np
import cairo

W, H = 1080, 1920
INK = (0x2A / 255, 0x1F / 255, 0x14 / 255)
RED = (0x8C / 255, 0x2F / 255, 0x1B / 255)
BLUE = (0x2D / 255, 0x4A / 255, 0x5A / 255)
GOLD = (0xB8 / 255, 0x86 / 255, 0x2B / 255)
BG = (0xEF, 0xE3, 0xC8)


def smooth_noise(rng, h, w, cell):
    """bruit de valeur basse fréquence (bilinéaire sur une grille grossière)."""
    gh, gw = h // cell + 2, w // cell + 2
    g = rng.random((gh, gw))
    ys = np.linspace(0, gh - 1.001, h); xs = np.linspace(0, gw - 1.001, w)
    y0 = ys.astype(int); x0 = xs.astype(int); fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def surface_from_rgb(arr):
    h, w, _ = arr.shape
    buf = np.zeros((h, w, 4), np.uint8)
    buf[..., 0] = arr[..., 2]; buf[..., 1] = arr[..., 1]; buf[..., 2] = arr[..., 0]; buf[..., 3] = 255
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride() // 4, 4)[:, :w] = buf
    s.mark_dirty()
    return s


def paper(out, rng):
    n = 0.55 * smooth_noise(rng, H, W, 240) + 0.3 * smooth_noise(rng, H, W, 90) + 0.15 * smooth_noise(rng, H, W, 30)
    grain = rng.normal(0, 1, (H, W))
    base = np.array(BG, float)[None, None, :]
    shade = (n - 0.5) * 26 + grain * 3.2
    tint = np.array([1.0, 0.86, 0.62])[None, None, :]       # les nuages tirent vers le brun
    arr = np.clip(base + shade[..., None] * tint, 0, 255)
    # rousseurs (foxing) : quelques taches douces
    yy, xx = np.mgrid[0:H, 0:W]
    for _ in range(9):
        cx, cy, r = rng.random() * W, rng.random() * H, 6 + rng.random() * 26
        m = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
        arr -= m[..., None] * np.array([18, 26, 34])[None, None, :] * (0.4 + rng.random() * 0.6)
    s = surface_from_rgb(np.clip(arr, 0, 255).astype(np.uint8))
    c = cairo.Context(s)
    # vergeures (fines, serrées) + pontuseaux (espacés)
    c.set_source_rgba(*INK, 0.05); c.set_line_width(0.8)
    for y in range(0, H, 9):
        c.move_to(0, y + 0.5)
        for x in range(0, W + 40, 40):
            c.line_to(x, y + 0.5 + math.sin(x * 0.01 + y * 0.3) * 0.6)
        c.stroke()
    c.set_source_rgba(*INK, 0.07); c.set_line_width(1.6)
    for x in range(40, W, 150):
        c.move_to(x, 0); c.line_to(x + 2, H); c.stroke()
    s.write_to_png(str(out / 'paper.png'))


def vignette(out):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    g = cairo.RadialGradient(W / 2, H * 0.48, H * 0.30, W / 2, H * 0.48, H * 0.78)
    g.add_color_stop_rgba(0, 0.35, 0.22, 0.10, 0.0)
    g.add_color_stop_rgba(1, 0.35, 0.22, 0.10, 0.42)
    c.set_source(g); c.paint()
    s.write_to_png(str(out / 'vignette.png'))


def frame(out):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    x0, y0, x1, y1 = 46, 196, 946, 1636
    c.set_source_rgb(*INK)
    c.set_line_width(3.2); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.stroke()
    # bordure graduée (alternance noir / blanc, comme les cartes gravées)
    b = 12
    c.set_line_width(1.1); c.rectangle(x0 + 8, y0 + 8, x1 - x0 - 16, y1 - y0 - 16); c.stroke()
    c.rectangle(x0 + 8 + b, y0 + 8 + b, x1 - x0 - 16 - 2 * b, y1 - y0 - 16 - 2 * b); c.stroke()
    step = 36
    xa, xb = x0 + 8 + b, x1 - 8 - b
    k = 0
    x = xa
    while x < xb:
        if k % 2 == 0:
            w = min(step, xb - x)
            c.rectangle(x, y0 + 8, w, b); c.rectangle(x, y1 - 8 - b, w, b)
        x += step; k += 1
    ya, yb = y0 + 8 + b, y1 - 8 - b
    k = 0; y = ya
    while y < yb:
        if k % 2 == 0:
            h = min(step, yb - y)
            c.rectangle(x0 + 8, y, b, h); c.rectangle(x1 - 8 - b, y, b, h)
        y += step; k += 1
    c.fill()
    # écoinçons : petits carrés avec croix gravée
    for (cx, cy) in [(x0 + 8, y0 + 8), (x1 - 8 - b, y0 + 8), (x0 + 8, y1 - 8 - b), (x1 - 8 - b, y1 - 8 - b)]:
        c.set_source_rgb(*BG_F); c.rectangle(cx, cy, b, b); c.fill()
        c.set_source_rgb(*INK); c.set_line_width(1); c.rectangle(cx, cy, b, b); c.stroke()
        c.move_to(cx, cy); c.line_to(cx + b, cy + b); c.move_to(cx + b, cy); c.line_to(cx, cy + b); c.stroke()
    s.write_to_png(str(out / 'frame.png'))


BG_F = tuple(v / 255 for v in BG)


def rrect_pt(t, a, b, n=5.0):
    """point d'une superellipse |x/a|^n+|y/b|^n=1 (angle t)."""
    ct, st = math.cos(t), math.sin(t)
    x = a * math.copysign(abs(ct) ** (2 / n), ct)
    y = b * math.copysign(abs(st) ** (2 / n), st)
    return x, y


def cartouche(out):
    w, h = 920, 300
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.translate(w / 2, h / 2)
    A, B = w / 2 - 14, h / 2 - 14
    # fond papier du cartouche
    c.set_source_rgba(*BG_F, 0.96)
    N = 720
    for i in range(N + 1):
        x, y = rrect_pt(i / N * 2 * math.pi, A, B)
        (c.move_to if i == 0 else c.line_to)(x, y)
    c.close_path(); c.fill()
    # guilloché : 14 lignes trochoïdales déphasées entre deux superellipses
    band = 22
    for k in range(14):
        ph = k * 2 * math.pi / 14
        c.set_source_rgba(*INK, 0.78); c.set_line_width(0.9)
        for i in range(N + 1):
            t = i / N * 2 * math.pi
            off = band * (0.5 + 0.5 * math.sin(t * 46 + ph))
            x, y = rrect_pt(t, A - 4 - off, B - 4 - off)
            (c.move_to if i == 0 else c.line_to)(x, y)
        c.close_path(); c.stroke()
    # filets
    for (d, lw, col) in [(0, 3.0, INK), (band + 10, 1.4, INK), (band + 18, 2.2, GOLD)]:
        c.set_source_rgb(*col); c.set_line_width(lw)
        for i in range(N + 1):
            x, y = rrect_pt(i / N * 2 * math.pi, A - d, B - d)
            (c.move_to if i == 0 else c.line_to)(x, y)
        c.close_path(); c.stroke()
    s.write_to_png(str(out / 'cartouche.png'))


def compass(out):
    S = 420
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S); c = cairo.Context(s)
    c.translate(S / 2, S / 2)
    R = 150
    c.set_source_rgb(*INK)
    for r, lw in [(R + 40, 2.4), (R + 30, 1.0), (R, 1.4), (58, 1.2)]:
        c.set_line_width(lw); c.arc(0, 0, r, 0, 2 * math.pi); c.stroke()
    for i in range(128):
        a = i / 128 * 2 * math.pi; l = 10 if i % 8 == 0 else 5
        c.set_line_width(1.6 if i % 8 == 0 else 0.8)
        c.move_to((R + 30) * math.cos(a), (R + 30) * math.sin(a)); c.line_to((R + 30 - l) * math.cos(a), (R + 30 - l) * math.sin(a)); c.stroke()
    # pointes : 4 cardinales longues, 4 intercardinales, 8 courtes
    def point(angle, length, width, north=False):
        a = angle - math.pi / 2
        tip = (length * math.cos(a), length * math.sin(a))
        l = (width * math.cos(a - math.pi / 2), width * math.sin(a - math.pi / 2))
        r = (width * math.cos(a + math.pi / 2), width * math.sin(a + math.pi / 2))
        # moitié pleine
        c.move_to(0, 0); c.line_to(*tip); c.line_to(*l); c.close_path()
        c.set_source_rgb(*(RED if north else INK)); c.fill()
        # moitié hachurée
        c.save(); c.move_to(0, 0); c.line_to(*tip); c.line_to(*r); c.close_path(); c.clip()
        c.set_source_rgb(*INK); c.set_line_width(0.9)
        for k in range(-int(length), int(length), 4):
            c.move_to(-length, k); c.line_to(length, k + 0.0); c.stroke()
        c.restore()
        c.move_to(0, 0); c.line_to(*tip); c.line_to(*r); c.close_path()
        c.set_source_rgb(*INK); c.set_line_width(1.2); c.stroke()
        c.move_to(0, 0); c.line_to(*tip); c.line_to(*l); c.close_path(); c.stroke()
    for i in range(16):
        ang = i * math.pi / 8
        if i % 4 == 0: continue
        point(ang, R * (0.62 if i % 2 == 0 else 0.45), 12 if i % 2 == 0 else 8)
    for i in range(4):
        point(i * math.pi / 2, R + 22, 20, north=(i == 0))
    c.set_source_rgb(*BG_F); c.arc(0, 0, 9, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(1.6); c.arc(0, 0, 9, 0, 2 * math.pi); c.stroke()
    s.write_to_png(str(out / 'compass.png'))


def sea(out, rng):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_line_width(1.0)
    ph = rng.random(400) * 6.28
    for j, y in enumerate(range(0, H, 7)):
        c.set_source_rgba(*BLUE, 0.30 + 0.12 * math.sin(j * 0.7))
        c.move_to(0, y)
        for x in range(0, W + 12, 12):
            c.line_to(x, y + 1.3 * math.sin(x * 0.018 + ph[j % 400]) + 0.6 * math.sin(x * 0.07 + j))
        c.stroke()
    s.write_to_png(str(out / 'sea.png'))


def ship(out):
    S = 220
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S); c = cairo.Context(s)
    c.translate(S / 2, S / 2 + 20)
    # coque
    c.move_to(-86, -18); c.curve_to(-70, 30, 60, 34, 84, -26); c.line_to(60, -18); c.line_to(-60, -14); c.close_path()
    c.set_source_rgb(*BG_F); c.fill_preserve(); c.save(); c.clip()
    c.set_source_rgb(*INK); c.set_line_width(1.6)
    for k in range(-120, 120, 6):
        c.move_to(k, -40); c.line_to(k + 40, 40); c.stroke()
    c.restore()
    c.move_to(-86, -18); c.curve_to(-70, 30, 60, 34, 84, -26); c.line_to(60, -18); c.line_to(-60, -14); c.close_path()
    c.set_source_rgb(*INK); c.set_line_width(3.6); c.stroke()
    c.set_line_width(2.4); c.move_to(-74, 2); c.curve_to(-40, 14, 40, 14, 72, -4); c.stroke()
    # mâts
    c.set_line_width(4)
    for x, top in [(-40, -100), (6, -130), (50, -92)]:
        c.move_to(x, -14); c.line_to(x, top); c.stroke()
    # voiles (carrées gonflées, hachurées)
    for x, y0, y1, w in [(-40, -92, -40, 26), (6, -122, -78, 32), (6, -72, -30, 36), (50, -86, -44, 24)]:
        c.move_to(x - w, y0); c.curve_to(x - w * 0.6, (y0 + y1) / 2, x - w * 0.6, (y0 + y1) / 2, x - w, y1)
        c.line_to(x + w, y1); c.curve_to(x + w * 1.3, (y0 + y1) / 2, x + w * 1.3, (y0 + y1) / 2, x + w, y0); c.close_path()
        c.set_source_rgb(*BG_F); c.fill_preserve()
        c.save(); c.clip(); c.set_source_rgba(*INK, 0.8); c.set_line_width(1.0)
        for k in range(int(y0), int(y1), 5):
            c.move_to(x - w * 1.4, k); c.line_to(x + w * 1.4, k + 3); c.stroke()
        c.restore(); c.set_source_rgb(*INK); c.set_line_width(2.6)
        c.move_to(x - w, y0); c.curve_to(x - w * 0.6, (y0 + y1) / 2, x - w * 0.6, (y0 + y1) / 2, x - w, y1)
        c.line_to(x + w, y1); c.curve_to(x + w * 1.3, (y0 + y1) / 2, x + w * 1.3, (y0 + y1) / 2, x + w, y0); c.close_path(); c.stroke()
    # croix rouge sur la grand-voile + flamme
    c.set_source_rgb(*RED); c.set_line_width(5)
    c.move_to(6, -64); c.line_to(6, -40); c.move_to(-6, -53); c.line_to(18, -53); c.stroke()
    c.move_to(6, -130); c.line_to(40, -136); c.line_to(6, -124); c.close_path(); c.fill()
    # vagues
    c.set_source_rgb(*BLUE); c.set_line_width(2.2)
    for k in range(3):
        c.move_to(-100, 26 + k * 10)
        for x in range(-100, 101, 10): c.line_to(x, 26 + k * 10 + 3 * math.sin(x * 0.12 + k))
        c.stroke()
    s.write_to_png(str(out / 'ship.png'))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    seed = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 7
    rng = np.random.default_rng(seed)
    paper(out, rng); vignette(out); frame(out); cartouche(out); compass(out); sea(out, rng); ship(out)
    print('textures ->', out)


if __name__ == '__main__':
    main()
