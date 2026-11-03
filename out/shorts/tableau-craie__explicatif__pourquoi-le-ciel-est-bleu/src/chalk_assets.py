"""chalk_assets.py — fond ardoise, grain de craie et overlays texte (identité « Tableau Craie »).

Tout est généré par code (numpy + PIL + polices @fontsource via out/tools/textpng.py). Graine fixe.
Usage : .venv/bin/python chalk_assets.py <outdir>   -> board.png, grain.png, txt_*.png, overlays.txt
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'out' / 'tools'))
from textpng import text_layer  # noqa: E402

W, H = 1080, 1920
SEED = 5
TOK = json.loads((HERE / 'tokens.json').read_text())
P = TOK['color']


def hex3(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def board(path):
    """Ardoise verte : vignette radiale + essuyages de chiffon + bruit + rebord bois (bas, décoratif)."""
    r = np.random.default_rng(SEED)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - 540) ** 2 + (yy - 900) ** 2) / 1300
    c0, c1 = hex3('#24443A'), hex3('#16291F')
    img = c0[None, None] * (1 - d[..., None].clip(0, 1)) + c1[None, None] * d[..., None].clip(0, 1)
    for _ in range(26):  # traces de chiffon
        x, y, rx, ry, a = r.random() * W, r.random() * H, 140 + r.random() * 320, 30 + r.random() * 70, (r.random() - .5) * .6
        u = ((xx - x) * np.cos(a) + (yy - y) * np.sin(a)) / rx
        v = (-(xx - x) * np.sin(a) + (yy - y) * np.cos(a)) / ry
        k = np.clip(1 - np.sqrt(u * u + v * v), 0, 1) * 0.05
        img = img * (1 - k[..., None]) + hex3('#F0F0DC')[None, None] * k[..., None]
    img += (r.random((H, W, 1)) - .5) * 14
    # rebord bois + 3 craies (zone basse décorative, hors contenu)
    wood = np.linspace(0, 1, 70)[:, None, None]
    img[1770:1840] = hex3('#9A6A3E') * (1 - wood) + hex3('#5E3D22') * wood
    img[1765:1771] *= 0.65
    for x0, col, ln in [(160, P['accent'][0], 120), (330, P['accent'][1], 90), (470, P['accent'][2], 70)]:
        img[1752:1770, x0:x0 + ln] = hex3(col)
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(path)


def grain_mask(seed=77):
    """Masque de grain : 1 = craie conservée, 0 = trou (le grain du tableau traverse la craie)."""
    r = np.random.default_rng(seed)
    v = r.random((H, W))
    m = np.where(v < 0.26, 0.0, np.where(v < 0.38, 0.5, 1.0))
    return m.astype(np.float32)


def grain_overlay(path, board_path):
    """Overlay plein cadre = pixels de l'ardoise elle-même, posé SUR la vidéo Manim : il « troue » les traits
    de craie et reste invisible sur le fond (même image)."""
    m = 1 - grain_mask(77)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = np.asarray(Image.open(board_path).convert('RGB'))
    rgba[..., 3] = (m * 235).astype(np.uint8)
    # sur le fond, le grain est presque invisible (même teinte) ; sur la craie il crée la texture
    Image.fromarray(rgba, 'RGBA').save(path)


def chalk_text(path, text, font, weight, size, color, y, x=None, maxw=840, align='center', seed=3, rot=0.0):
    img = text_layer(text, font=font, weight=weight, size=size, color=color, y=y, x=x, maxw=maxw, align=align)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, center=(x or 540, y + size / 2))
    a = np.asarray(img).astype(np.float32)
    a[..., 3] *= grain_mask(seed)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    halo = out.filter(ImageFilter.GaussianBlur(1.2))  # poussière de craie
    Image.alpha_composite(halo, out).save(path)


if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    board(out / 'board.png')
    grain_overlay(out / 'grain.png', out / 'board.png')
    T = json.loads((HERE / 'timeline.json').read_text())
    lines = []
    tp = TOK['typography']
    for i, o in enumerate(T['texts']):
        f = tp[o['role']]
        p = out / f'txt_{i:02d}.png'
        chalk_text(p, o['text'], f['pkg'], f['weight'], o.get('size', f['size']), o.get('color', P['text']),
                   o['y'], o.get('x'), o.get('maxw', 840), o.get('align', 'center'), seed=11 + i, rot=o.get('rot', 0))
        lines.append(f"{p}:{o['t0']}:{o['t1']}:{o.get('fade', 0.25)}")
    lines.insert(0, f"{out / 'grain.png'}:0:{T['duration']}:0.01")
    (out / 'overlays.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
