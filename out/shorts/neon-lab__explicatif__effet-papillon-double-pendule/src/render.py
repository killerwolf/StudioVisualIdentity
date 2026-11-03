#!/usr/bin/env python3
"""
render.py — Labo Néon / LABO/03 : « L'effet papillon : deux pendules presque identiques » rendu avec Matplotlib (Agg).

  .venv/bin/python render.py --out raw.mp4                 # vidéo muette 1080×1920 30 fps (crf 14), 15 s
  .venv/bin/python render.py --stills 0.5,5,9.5,13.5 --dir stills/

- Physique : pendulum.py (RK4 pas fixe 1/1800 s, m=1 kg, L=1 m, g=9,81). Pendule A : θ1=θ2=1,8 rad ;
  pendule B : θ1 = 1,8 + 0,001 rad. Sans aléa ; graine 3 = seulement le bruit du champ de fond.
- Une seule figure 10,8×19,2 in à 100 dpi ; les artistes sont mis à jour à chaque frame (set_data / set_segments /
  set_position / set_alpha), jamais recréés. fig.canvas.buffer_rgba() -> numpy -> pipe rawvideo ffmpeg.
- Polices : Matplotlib/FreeType ne lit pas le WOFF2 (pas de brotli) -> conversion des .woff @fontsource en .ttf
  avec fontTools (dépendance de Matplotlib), puis font_manager.fontManager.addfont. Le sous-ensemble grec de
  JetBrains Mono est renommé « JetBrains Mono Greek » et sert de repli (Δ, θ).
- Beats (80 bpm, noire 0,75 s) : A 0 · B 4,5 · C 8,25 · D 12,0 · fin 15,0. Impulsion (pulse) 0,35 s à chaque beat.
"""
import argparse, os, subprocess, sys, time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import pendulum as P

W, H, FPS, DUR, SEED = 1080, 1920, 30, 15.0, 3
TB, TC, TD = 4.5, 8.25, 12.0
BG, SURF, CY, MG, LI, TX, MU = '#05060B', '#11142A', '#38F9FF', '#FF3DCB', '#B6FF3B', '#F2F6FF', '#9FB7FF'
PX = 72 / 100  # px -> points à 100 dpi


# ---------- polices ----------
def install_fonts(tmp):
    tmp.mkdir(parents=True, exist_ok=True)
    spec = [('space-grotesk', 'latin', 700, None), ('space-grotesk', 'latin', 500, None),
            ('jetbrains-mono', 'latin', 500, None), ('jetbrains-mono', 'greek', 500, 'JetBrains Mono Greek')]
    for pkg, sub, w, rename in spec:
        src = ROOT / 'node_modules' / '@fontsource' / pkg / 'files' / f'{pkg}-{sub}-{w}-normal.woff'
        dst = tmp / f'{pkg}-{sub}-{w}.ttf'
        if not dst.exists():
            f = TTFont(str(src)); f.flavor = None
            if rename:
                for rec in f['name'].names:
                    if rec.nameID in (1, 4, 16):
                        rec.string = rename
            f.save(str(dst))
        fm.fontManager.addfont(str(dst))


# ---------- champ de force (portage numpy du GLSL field.glsl.js, image fixe) ----------
def fract(x):
    return x - np.floor(x)


def nl_h(px, py):
    px, py = fract(px * 123.34), fract(py * 456.21)
    d = px * (px + 45.32) + py * (py + 45.32)
    px, py = px + d, py + d
    return fract(px * py)


def nl_vn(x, y):
    ix, iy = np.floor(x), np.floor(y); fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = nl_h(ix, iy), nl_h(ix + 1, iy); c, d = nl_h(ix, iy + 1), nl_h(ix + 1, iy + 1)
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy


def nl_fbm(x, y):
    return .6 * nl_vn(x, y) + .3 * nl_vn(x * 2.03 + 7.1, y * 2.03 + 7.1) + .1 * nl_vn(x * 4.01 + 3.3, y * 4.01 + 3.3)


def field_image(center=(540, 960), loop=(0.7071, 0.7071)):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    px, py = (xx - center[0]) / H, ((H - yy) - (H - center[1])) / H
    r = np.hypot(px, py)
    f = nl_fbm(px * 3 + loop[0] * .32 + SEED * 0.0, py * 3 + loop[1] * .32) * .9 + .42 / (r * 5.5 + 1)
    k = f * 11
    gy, gx = np.gradient(k); w = np.abs(gx) + np.abs(gy) + 1e-6
    dl = .5 - np.abs(fract(k) - .5)
    iso = 1 - np.clip(dl / (w * 1.6), 0, 1); iso = iso * iso * (3 - 2 * iso)
    side = nl_fbm(px * 1.4 - loop[0] * .2 + 5, py * 1.4 - loop[1] * .2 + 5)
    side = np.clip((side - .25) / .5, 0, 1)[..., None]
    cyan, mag = np.array([.2196, .9765, 1.]), np.array([1., .2392, .796])
    bg, surf = np.array([.0196, .0235, .0431]), np.array([.0667, .0784, .1647])
    glow = np.exp(-r * r * 5)[..., None]
    vign = np.clip((1.05 - r) / .8, 0, 1)[..., None]
    base = bg + (surf - bg) * glow * .85
    rgba = np.dstack([cyan + (mag - cyan) * side, iso[..., None] * vign])   # couleur de ligne + masque iso
    return np.clip(base, 0, 1), np.clip(rgba, 0, 1)


# ---------- easings / helpers ----------
def clamp(x, a=0., b=1.):
    return min(b, max(a, x))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def out_expo(x):
    return 1. if x >= 1 else 1 - 2 ** (-10 * x)


def in_expo(x):
    return 0. if x <= 0 else 2 ** (10 * x - 10)


def pulse_at(t):
    p = 0.
    for tb in (0., TB, TC, TD):
        if t >= tb:
            p = max(p, np.exp(-(t - tb) / 0.35))
    return p


def glide(t, t0, t1=None):
    """(alpha, dy_px) : entrée outExpo 0,6 s, sortie inExpo 0,3 s (tokens Labo Néon)."""
    a = out_expo(seg(t, t0, t0 + .6)); b = 0. if t1 is None else in_expo(seg(t, t1 - .3, t1))
    return a * (1 - b), (1 - a) * 46 - b * 28


def fy(px_top):  # coordonnée figure (0 en bas) depuis un y en px depuis le haut
    return 1 - px_top / H


def fmt_m(d):
    return (f'{d:.4f}' if d < 0.1 else f'{d:.2f}').replace('.', ',') + ' m'


# ---------- scène ----------
class Scene:
    def __init__(self):
        install_fonts(Path('/tmp/svi/neon-lab-pend/fonts'))
        self.fig = fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
        # fond : base + lignes de champ (alpha pulsé)
        base, lines = field_image(center=(520, 900))
        axb = fig.add_axes([0, 0, 1, 1]); axb.axis('off')
        axb.imshow(base, extent=(0, 1, 0, 1), aspect='auto', interpolation='nearest')
        self.lines_img = axb.imshow(lines,
                                    extent=(0, 1, 0, 1), aspect='auto', interpolation='nearest', alpha=.1)
        axb.set_xlim(0, 1); axb.set_ylim(0, 1)
        # simulation (enregistrement à 10 échantillons par frame pour des traînes lisses)
        self.sim_a, self.sim_b, self.sub_a, self.sub_b = self.simulate()
        self.d = np.hypot(self.sim_a[:, 2] - self.sim_b[:, 2], self.sim_a[:, 3] - self.sim_b[:, 3])
        self.t1000 = np.argmax(self.d >= 1.0) / FPS
        # axes pendule : pivot à (520, 820) px, 215 px/m (extension simulée : y -2,0..+0,83 m, x ±2 m -> 640–1250 px)
        cx, cy, half, SC = 520, 820, 470, 215
        self.axp = axp = fig.add_axes([(cx - half) / W, fy(cy + half), 2 * half / W, 2 * half / H])
        axp.set_xlim(-half / SC, half / SC); axp.set_ylim(-half / SC, half / SC); axp.axis('off')
        axp.patch.set_alpha(0)
        self.trails = {}
        # B (magenta) dessous et plus large, A (cyan) dessus et fin : superposés, on voit un cœur cyan bordé de magenta
        for key, col, zb, lwk, bobstyle in (('b', MG, 1, 2.2, 'ring'), ('a', CY, 3, 1.0, 'fill')):
            glow = LineCollection([], colors=col, linewidths=16, capstyle='round', zorder=zb)
            core = LineCollection([], colors=col, linewidths=4.5, capstyle='round', zorder=zb + .5)
            axp.add_collection(glow); axp.add_collection(core)
            rod, = axp.plot([], [], '-', color=TX if key == 'a' else MG, lw=4 if key == 'a' else 9, alpha=.85 if key == 'a' else .55,
                            solid_capstyle='round', zorder=5 + zb)
            halo, = axp.plot([], [], 'o', ms=46, color=col, alpha=.22, zorder=6 + zb, mec='none')
            if bobstyle == 'ring':
                bob, = axp.plot([], [], 'o', ms=34, mfc='none', mec=col, mew=5, zorder=7 + zb)
            else:
                bob, = axp.plot([], [], 'o', ms=20, color=col, zorder=7 + zb, mec=TX, mew=2.5)
            self.trails[key] = (glow, core, rod, halo, bob, col, lwk)
        axp.plot([0], [0], 'o', ms=12, color=TX, zorder=8)
        # graphe de l'écart (log)
        self.axs = axs = fig.add_axes([230 / W, fy(1590), (940 - 230) / W, (1590 - 1410) / H])
        axs.set_yscale('log'); axs.set_xlim(0, DUR); axs.set_ylim(5e-4, 6)
        axs.patch.set_alpha(0)
        for s in ('top', 'right'):
            axs.spines[s].set_visible(False)
        for s in ('left', 'bottom'):
            axs.spines[s].set_color(MU); axs.spines[s].set_alpha(.5); axs.spines[s].set_linewidth(2)
        axs.set_xticks([]); axs.set_yticks([]); axs.minorticks_off()
        for yv in (1e-3, 1e-2, 1e-1, 1):
            axs.axhline(yv, color=MU, lw=1.2, alpha=.18)
        self.sep_glow, = axs.plot([], [], color=LI, lw=12, alpha=.18, solid_capstyle='round')
        self.sep, = axs.plot([], [], color=LI, lw=4, solid_capstyle='round')
        self.sep_dot, = axs.plot([], [], 'o', ms=16, color=LI, mec=TX, mew=2)
        mono = dict(family=['JetBrains Mono', 'JetBrains Mono Greek'], weight=500, size=54 * PX)
        ly = lambda v: 1590 - (np.log(v) - np.log(5e-4)) / (np.log(6) - np.log(5e-4)) * 180   # px du graphe log
        self.t_mm = fig.text(72 / W, fy(ly(1e-3)), '1 mm', color=MU, va='center', **mono)
        self.t_1m = fig.text(72 / W, fy(ly(1.0)), '1 m', color=MU, va='center', **mono)
        self.t_cap = fig.text(72 / W, fy(1372), 'ÉCART', color=TX, va='center', **mono)
        self.t_val = fig.text(960 / W, fy(1372), '', color=LI, va='center', ha='right', **mono)
        # textes (tag, titres de beat, donnée)
        self.tag = fig.text(108 / W, fy(262), 'LABO/03 · CHAOS', color=CY, va='center', **mono)
        self.dot, = fig.add_axes([0, 0, 1, 1], facecolor='none').plot([86 / W], [fy(262)], 'o', ms=16, color=MG)
        fig.axes[-1].set_xlim(0, 1); fig.axes[-1].set_ylim(0, 1); fig.axes[-1].axis('off')
        title = dict(family='Space Grotesk', weight=700, size=104 * PX, va='top')
        self.titles = [
            (fig.text(72 / W, fy(316), 'Effet papillon', color=TX, **title), 0.05, TB),
            (fig.text(72 / W, fy(316), 'Presque jumeaux', color=TX, **title), TB + .1, TC),
            (fig.text(72 / W, fy(316), 'Puis… le chaos', color=MG, **title), TC + .1, TD),
            (fig.text(72 / W, fy(316), 'Imprévisible', color=LI, **title), TD + .1, None)]
        self.data = fig.text(72 / W, fy(470), 'Δθ = 0,001 rad', color=LI, va='center', **mono)
        self.data2 = fig.text(72 / W, fy(470), f'×1 000 en {self.t1000:.1f} s'.replace('.', ','), color=LI, va='center', **mono)

    def simulate(self):
        a = np.array([1.8, 1.8, 0., 0.]); b = np.array([1.8 + 0.001, 1.8, 0., 0.])
        n = int(round(DUR * FPS)) + 1
        SA, SB = np.zeros((n, 4)), np.zeros((n, 4))
        sub_a, sub_b = [P.tips(a)[2:]], [P.tips(b)[2:]]
        SA[0], SB[0] = P.tips(a), P.tips(b)
        self.state_a, self.state_b = [a.copy()], [b.copy()]
        for f in range(1, n):
            for s in range(P.SUB):
                a = P.rk4(a); b = P.rk4(b)
                if (s + 1) % 6 == 0:
                    sub_a.append(P.tips(a)[2:]); sub_b.append(P.tips(b)[2:])
            SA[f], SB[f] = P.tips(a), P.tips(b)
            self.state_a.append(a.copy()); self.state_b.append(b.copy())
        e0, e1 = P.energy(self.state_a[0]), P.energy(self.state_a[-1])
        print(f'énergie A : {e0:.6f} -> {e1:.6f} J (dérive {e1 - e0:.2e})', file=sys.stderr)
        return SA, SB, np.array(sub_a), np.array(sub_b)

    def draw(self, t):
        f = min(int(round(t * FPS)), len(self.sim_a) - 1)
        p = pulse_at(t)
        self.lines_img.set_alpha(.10 + .14 * p)
        for key, S, SUBS in (('a', self.sim_a, self.sub_a), ('b', self.sim_b, self.sub_b)):
            glow, core, rod, halo, bob, col, lwk = self.trails[key]
            x1, y1, x2, y2 = S[f]
            rod.set_data([0, x1, x2], [0, y1, y2])
            bob.set_data([x1, x2], [y1, y2]); halo.set_data([x2], [y2])
            halo.set_markersize(46 * (1 + .5 * p))
            i1 = f * 10; i0 = max(0, i1 - 14 * 10)          # traîne = 1,4 s
            pts = SUBS[i0:i1 + 1]
            if len(pts) > 1:
                segs = np.stack([pts[:-1], pts[1:]], axis=1)
                k = np.linspace(0, 1, len(segs)) ** 1.6
                glow.set_segments(segs); core.set_segments(segs)
                glow.set_alpha(None); core.set_alpha(None)
                rgb = matplotlib.colors.to_rgb(col)
                glow.set_color([(*rgb, .14 * kk * (1 + .8 * p)) for kk in k])
                core.set_color([(*rgb, .95 * kk) for kk in k])
                glow.set_linewidths(16 * (1 + .6 * p) * (.4 + .6 * k)); core.set_linewidths(4.5 * lwk * (.3 + .7 * k))
            else:
                glow.set_segments([]); core.set_segments([])
        # graphe
        ts = np.arange(f + 1) / FPS; dd = np.maximum(self.d[:f + 1], 1e-4)
        self.sep.set_data(ts, dd); self.sep_glow.set_data(ts, dd); self.sep_dot.set_data([ts[-1]], [dd[-1]])
        self.sep_glow.set_linewidth(12 * (1 + .8 * p))
        self.t_val.set_text(fmt_m(self.d[f]))
        # textes
        for art, t0, t1 in self.titles:
            a, dy = glide(t, t0, t1)
            art.set_alpha(a); art.set_y(fy(316 + dy)); art.set_visible(a > 0.003)
        a, dy = glide(t, 0.0)
        self.tag.set_alpha(a); self.tag.set_y(fy(262 + dy * .4)); self.dot.set_alpha(a)
        a, dy = glide(t, 0.3, TD + .3); self.data.set_alpha(a); self.data.set_y(fy(470 + dy))
        a, dy = glide(t, TD + .5); self.data2.set_alpha(a); self.data2.set_y(fy(470 + dy))
        a, _ = glide(t, 0.6)
        for art in (self.t_mm, self.t_1m, self.t_cap, self.t_val):
            art.set_alpha(a)
        self.fig.canvas.draw()
        return np.asarray(self.fig.canvas.buffer_rgba())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out'); ap.add_argument('--stills'); ap.add_argument('--dir', default='.')
    a = ap.parse_args()
    t0 = time.time()
    sc = Scene()
    print(f'setup {time.time() - t0:.1f}s, ×1000 à {sc.t1000:.2f}s', file=sys.stderr)
    if a.stills:
        from PIL import Image
        os.makedirs(a.dir, exist_ok=True)
        for s in a.stills.split(','):
            img = sc.draw(float(s))
            Image.fromarray(img[..., :3]).save(f'{a.dir}/still_{float(s):05.2f}s.jpg', quality=92)
        print(f'{{"mode":"stills","seconds":{time.time() - t0:.1f}}}')
        return
    n = int(round(DUR * FPS))
    part = a.out + '.part.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14',
                           '-pix_fmt', 'yuv420p', '-r', str(FPS), part], stdin=subprocess.PIPE)
    t1 = time.time()
    for i in range(n):
        ff.stdin.write(sc.draw(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); os.replace(part, a.out)
    dt = time.time() - t1
    print(f'{{"mode":"video","frames":{n},"seconds":{time.time() - t0:.1f},"drawSeconds":{dt:.1f},"secPer100Frames":{dt / n * 100:.1f}}}')


if __name__ == '__main__':
    main()
