#!/usr/bin/env python3
"""
Chrome Liquide — « Quatre peintures tombent et se mélangent » (famille abstrait).

Simulation : Taichi MLS-MPM 2D (fluide faiblement compressible façon mpm88 : seul J est suivi),
grille 90×196 (dx = 1/160, 12 px), 4 × 8 000 particules, dt = 1e-4, 100 sous-pas par frame.
Les couleurs des particules diffusent légèrement via la grille (P2G/G2P de la couleur) -> vrai mélange.
Rendu : accumulation de points (Taichi) -> flou gaussien OpenCV -> masque liquide -> normales (Sobel)
-> ombrage « peinture chrome » OpenCV/numpy (diffus, spéculaire Blinn, reflet d'environnement néon,
liseré de Fresnel) -> pipe rawvideo vers ffmpeg (libx264 crf 14 yuv420p). Muet ; le texte et le son
sont ajoutés par assemble.py.

USAGE
  out/tools/slot.sh .venv/bin/python out/shorts/<dossier>/src/mpm_paint.py --out /tmp/svi/liquid-a/video.mp4 \
      [--duration 14] [--until 6] [--stills 0.5,4,9,13 --stills-dir /tmp/x]
Déterministe : graine fixe (SEED), positions initiales tirées par numpy RandomState(SEED).
"""
import argparse, json, math, subprocess, sys, time
import numpy as np
import cv2
import taichi as ti

SEED = 11
ap = argparse.ArgumentParser()
ap.add_argument('--out', default='')
ap.add_argument('--duration', type=float, default=14.0)
ap.add_argument('--until', type=float, default=None)
ap.add_argument('--stills', default='')
ap.add_argument('--stills-dir', default='')
ap.add_argument('--threads', type=int, default=1)
a = ap.parse_args()

ti.init(arch=ti.cpu, random_seed=SEED, cpu_max_num_threads=a.threads, offline_cache=True)
cv2.setNumThreads(1)

FPS = 30
W, H = 1080, 1920               # sortie
HW, HH = 540, 960               # tampon d'accumulation (demi-résolution)
NX, NY = 90, 196                # grille : 90×160 visibles + 36 rangées au-dessus du cadre
DX = 1.0 / 160.0
INV_DX = 160.0
DT = 1e-4
SUBSTEPS = 80
P_VOL = (DX * 0.5) ** 2
P_MASS = P_VOL * 1.0
E = 600.0
MU = 0.05                       # viscosité (contrainte déviatorique mu(C+C^T)) : peinture, pas de l'eau
GRAV = 20.0

# géométrie du verre (en pixels de sortie) -> unités de simulation (1 unité = 1920 px)
WALL_L_PX, WALL_R_PX, FLOOR_PX = 96, 940, 1584
WL, WR = WALL_L_PX / 1920.0, WALL_R_PX / 1920.0
FLOOR = (1920 - FLOOR_PX) / 1920.0

# matières (palette de l'identité) : lilas chrome, rose, menthe, or
PAL = ['#C8D3FF', '#FF9AE8', '#7CF7E4', '#FFE29A']
def hx(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
COLS = [hx(c) for c in PAL]
NPER = 6000
N = NPER * 4
# chutes : (instant d'apparition s, centre x px, centre y px (négatif = au-dessus du cadre), rayon px, vx, vy)
DROPS = [(0.00, 380, 830, 168, 0.20, -0.5),
         (1.55, 700, -190, 160, -0.35, -0.6),
         (3.10, 420, -190, 160, 0.40, -0.6),
         (4.65, 610, -190, 168, -0.20, -0.6)]
STIR = (7.2, 10.6)              # fenêtre de touillage (vortex doux)
MIX = (6.8, 14.0)               # fenêtre de diffusion de couleur

x = ti.Vector.field(2, float, N)
v = ti.Vector.field(2, float, N)
C = ti.Matrix.field(2, 2, float, N)
J = ti.field(float, N)
col = ti.Vector.field(3, float, N)
act = ti.field(int, N)
gv = ti.Vector.field(2, float, (NX, NY))
gm = ti.field(float, (NX, NY))
gc = ti.Vector.field(3, float, (NX, NY))
acc = ti.field(float, (HH, HW))
accc = ti.Vector.field(3, float, (HH, HW))
stir = ti.field(float, ())
mixr = ti.field(float, ())
stir_c = ti.Vector.field(2, float, ())


@ti.kernel
def substep():
    for i, j in gm:
        gv[i, j] = [0.0, 0.0]; gm[i, j] = 0.0; gc[i, j] = [0.0, 0.0, 0.0]
    for p in x:
        if act[p] == 1:
            Xp = x[p] * INV_DX
            base = int(Xp - 0.5)
            fx = Xp - base
            w = [0.5 * (1.5 - fx) ** 2, 0.75 - (fx - 1) ** 2, 0.5 * (fx - 0.5) ** 2]
            stress = -DT * 4 * E * P_VOL * (J[p] - 1) * INV_DX * INV_DX
            visc = -DT * 4 * P_VOL * INV_DX * INV_DX * MU * (C[p] + C[p].transpose())
            affine = ti.Matrix([[stress, 0], [0, stress]]) + P_MASS * C[p] + visc
            for i, j in ti.static(ti.ndrange(3, 3)):
                off = ti.Vector([i, j])
                dpos = (off - fx) * DX
                wt = w[i].x * w[j].y
                I = base + off
                if 0 <= I.x < NX and 0 <= I.y < NY:
                    gv[I] += wt * (P_MASS * v[p] + affine @ dpos)
                    gm[I] += wt * P_MASS
                    gc[I] += wt * P_MASS * col[p]
    for i, j in gm:
        if gm[i, j] > 0:
            gc[i, j] /= gm[i, j]
            vv = gv[i, j] / gm[i, j]
            vv.y -= DT * GRAV
            pos = ti.Vector([i, j]) * DX
            r = pos - stir_c[None]
            d = r.norm() + 1e-4
            fall = ti.exp(-(d / 0.16) ** 2)
            vv += DT * stir[None] * fall * ti.Vector([-r.y, r.x]) / d
            vv *= 1.0 - DT * 0.6                      # légère viscosité apparente (peinture)
            if pos.x < WL + DX and vv.x < 0: vv.x = 0
            if pos.x > WR - DX and vv.x > 0: vv.x = 0
            if pos.y < FLOOR + DX and vv.y < 0: vv.y = 0
            if j > NY - 3 and vv.y > 0: vv.y = 0
            gv[i, j] = vv
    for p in x:
        if act[p] == 1:
            Xp = x[p] * INV_DX
            base = int(Xp - 0.5)
            fx = Xp - base
            w = [0.5 * (1.5 - fx) ** 2, 0.75 - (fx - 1) ** 2, 0.5 * (fx - 0.5) ** 2]
            new_v = ti.Vector.zero(float, 2)
            new_C = ti.Matrix.zero(float, 2, 2)
            new_c = ti.Vector.zero(float, 3)
            for i, j in ti.static(ti.ndrange(3, 3)):
                off = ti.Vector([i, j])
                dpos = (off - fx) * DX
                wt = w[i].x * w[j].y
                I = base + off
                if 0 <= I.x < NX and 0 <= I.y < NY:
                    g = gv[I]
                    new_v += wt * g
                    new_C += 4 * INV_DX * INV_DX * wt * g.outer_product(dpos)
                    new_c += wt * gc[I]
            v[p] = new_v
            x[p] += DT * new_v
            x[p].x = ti.min(ti.max(x[p].x, WL + 0.5 * DX), WR - 0.5 * DX)
            x[p].y = ti.min(ti.max(x[p].y, FLOOR + 0.5 * DX), (NY - 2) * DX)
            J[p] *= 1 + DT * new_C.trace()
            C[p] = new_C
            col[p] += mixr[None] * (new_c - col[p])


@ti.kernel
def splat():
    for i, j in acc:
        acc[i, j] = 0.0; accc[i, j] = [0.0, 0.0, 0.0]
    for p in x:
        if act[p] == 1:
            px = x[p].x * 960.0
            py = (1.0 - x[p].y) * 960.0
            ix, iy = int(px), int(py)
            if 0 <= ix < HW - 1 and 0 <= iy < HH - 1:
                fx, fy = px - ix, py - iy    # splat bilinéaire : moins de scintillement
                for a_, b_ in ti.static(ti.ndrange(2, 2)):
                    wt = (fx if a_ == 1 else 1 - fx) * (fy if b_ == 1 else 1 - fy)
                    acc[iy + b_, ix + a_] += wt
                    accc[iy + b_, ix + a_] += wt * col[p]


rs = np.random.RandomState(SEED)
X0 = np.zeros((N, 2), np.float32); V0 = np.zeros((N, 2), np.float32); C0 = np.zeros((N, 3), np.float32)
for k, (t0, cx, cy, r, vx, vy) in enumerate(DROPS):
    # disque légèrement en goutte (bas plus lourd), échantillonné uniformément
    ang = rs.rand(NPER) * 2 * np.pi; rr = np.sqrt(rs.rand(NPER)) * r
    px = cx + rr * np.cos(ang); py = cy + rr * np.sin(ang) * 1.06
    X0[k * NPER:(k + 1) * NPER, 0] = px / 1920.0
    X0[k * NPER:(k + 1) * NPER, 1] = (1920 - py) / 1920.0
    V0[k * NPER:(k + 1) * NPER] = [vx, vy]
    C0[k * NPER:(k + 1) * NPER] = COLS[k]
x.from_numpy(X0); v.from_numpy(V0); col.from_numpy(C0)
J.from_numpy(np.ones(N, np.float32))
act.from_numpy(np.zeros(N, np.int32))
stir_c[None] = [(WL + WR) / 2, FLOOR + 0.12]


def activate(k):
    a_ = act.to_numpy(); a_[k * NPER:(k + 1) * NPER] = 1; act.from_numpy(a_)


# ---------- ombrage OpenCV ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def halo(cx, cy, r, c, k):
    d = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)))
    return d[..., None] * np.array(c, np.float32)[None, None] * k
BG = np.zeros((H, W, 3), np.float32) + np.array(hx('#0B0B10'), np.float32)
BG += halo(330, 980, 560, hx('#FF9AE8'), 0.16) + halo(780, 1100, 520, hx('#7CF7E4'), 0.12) + halo(540, 1400, 420, hx('#C8D3FF'), 0.10)
BG += halo(540, 1640, 300, hx('#1A1A24'), 1.0)   # « table » sous le verre : jamais de frame noire
BG = np.clip(BG, 0, 1)

def env(rx, ry):
    """environnement studio néon (comme le poster) en fonction du vecteur réfléchi (repère image, y vers le bas)."""
    top = np.clip((-ry - 0.25) / 0.5, 0, 1) ** 1.5                   # softbox blanche en haut
    left = np.clip((-rx - 0.35) / 0.4, 0, 1) * np.clip(1 - np.abs(ry) * 1.2, 0, 1)
    right = np.clip((rx - 0.35) / 0.4, 0, 1) * np.clip(1 - np.abs(ry) * 1.2, 0, 1)
    bot = np.clip((ry - 0.55) / 0.4, 0, 1)
    e = (top[..., None] * np.array([0.97, 0.97, 1.0], np.float32) + left[..., None] * np.array(hx('#FF9AE8'), np.float32) * 0.9
         + right[..., None] * np.array(hx('#7CF7E4'), np.float32) * 0.9 + bot[..., None] * np.array(hx('#FFE29A'), np.float32) * 0.5)
    return e

L = np.array([-0.45, -0.75, 0.55], np.float32); L /= np.linalg.norm(L)
Hh = L + np.array([0, 0, 1], np.float32); Hh /= np.linalg.norm(Hh)
DENS = None

# verre : contour chrome fin (dessiné une fois) + reflets verticaux
GLASS = np.zeros((H, W, 3), np.float32); GA = np.zeros((H, W), np.float32)
def glass_layer():
    m = np.zeros((H, W), np.uint8)
    rr = 70
    x0, x1, y0, y1 = WALL_L_PX - 8, WALL_R_PX + 8, 640, FLOOR_PX + 10
    pts = []
    cv2.line(m, (x0, y0), (x0, y1 - rr), 255, 3, cv2.LINE_AA)
    cv2.line(m, (x1, y0), (x1, y1 - rr), 255, 3, cv2.LINE_AA)
    cv2.ellipse(m, (x0 + rr, y1 - rr), (rr, rr), 0, 90, 180, 255, 3, cv2.LINE_AA)
    cv2.ellipse(m, (x1 - rr, y1 - rr), (rr, rr), 0, 0, 90, 255, 3, cv2.LINE_AA)
    cv2.line(m, (x0 + rr, y1), (x1 - rr, y1), 255, 3, cv2.LINE_AA)
    a_ = m.astype(np.float32) / 255.0
    fade = np.clip((yy - y0) / 260.0, 0, 1)            # le verre s'efface vers le haut (pas de bord dur)
    a_ = a_ * fade
    glow = cv2.GaussianBlur(a_, (0, 0), 6) * 0.6
    # deux reflets verticaux doux sur la paroi
    s = np.zeros((H, W), np.float32)
    cv2.line(s, (x0 + 26, y0 + 200), (x0 + 26, y1 - 140), 1.0, 10, cv2.LINE_AA)
    cv2.line(s, (x1 - 30, y0 + 260), (x1 - 30, y1 - 160), 1.0, 5, cv2.LINE_AA)
    s = cv2.GaussianBlur(s, (0, 0), 7) * fade * 0.22
    alpha = np.clip(a_ * 0.85 + glow + s, 0, 1)
    colr = np.ones((H, W, 3), np.float32) * np.array([0.86, 0.89, 1.0], np.float32)
    return colr, alpha
GLASS, GA = glass_layer()
BGG = (np.clip(BG * (1 - GA[..., None]) + GLASS * GA[..., None], 0, 1) * 255).astype(np.uint8)[..., ::-1].copy()  # fond + verre, BGR


def shade(D, Cs):
    global DENS
    Db = cv2.GaussianBlur(D, (0, 0), 2.0)
    Cb = cv2.GaussianBlur(Cs, (0, 0), 2.0)
    base = Cb / (Db[..., None] + 1e-6)
    if DENS is None:
        DENS = float(np.percentile(Db[Db > 0.05], 70)) if np.any(Db > 0.05) else 1.0
    # ombrage en demi-résolution (540×960), puis agrandissement cubique : ×4 moins cher qu'en pleine résolution
    dF = Db / DENS
    baseF = base
    alpha = np.clip((dF - 0.12) / 0.20, 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    # hauteur multi-échelle : biseau fin au bord + dôme large (reflets qui glissent sur toute la surface)
    h = cv2.GaussianBlur(alpha, (0, 0), 4.5) + 0.9 * cv2.GaussianBlur(alpha, (0, 0), 24.0)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3)
    k = 11.0
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(h)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz); nx *= inv; ny *= inv; nz *= inv
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    nh = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1)
    spec = nh ** 90 * 1.25 + nh ** 14 * 0.22          # point brillant + lustre large
    rx, ry = 2 * nz * nx, 2 * nz * ny                 # reflet de V=(0,0,1)
    fres = (1 - nz) ** 2
    e = env(rx, ry)
    c = baseF * (0.26 + 0.55 * diff[..., None]) + e * baseF * (0.42 + 0.9 * fres[..., None]) \
        + e * (0.6 * fres[..., None]) + spec[..., None]
    return np.clip(c, 0, 1), alpha


def frame_image():
    splat()
    D = acc.to_numpy(); Cs = accc.to_numpy()
    c, al = shade(D, Cs)
    out = BGG.copy()
    ys, xs = np.nonzero(al > 0.002)
    if len(ys):
        # composition pleine résolution limitée à la boîte englobante du liquide (×3 plus rapide)
        hy0, hy1 = max(0, ys.min() - 6), min(HH, ys.max() + 7); hx0, hx1 = max(0, xs.min() - 6), min(HW, xs.max() + 7)
        y0, y1, x0, x1 = hy0 * 2, hy1 * 2, hx0 * 2, hx1 * 2
        cc = cv2.resize(c[hy0:hy1, hx0:hx1], (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
        aa = np.clip(cv2.resize(al[hy0:hy1, hx0:hx1], (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC), 0, 1)[..., None]
        reg = BG[y0:y1, x0:x1] * (1 - aa) + np.clip(cc, 0, 1) * aa
        ga = GA[y0:y1, x0:x1, None]
        reg = reg * (1 - ga) + GLASS[y0:y1, x0:x1] * ga
        out[y0:y1, x0:x1] = (np.clip(reg, 0, 1) * 255).astype(np.uint8)[..., ::-1]
    return out


dur = a.until if a.until else a.duration
nframes = int(round(dur * FPS))
stills = {int(round(float(s) * FPS)): s for s in a.stills.split(',') if s}
proc = None
if a.out:
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p',
                             '-threads', '1', a.out + '.part.mp4'], stdin=subprocess.PIPE)
t_start = time.time(); t_sim = 0.0; t_shade = 0.0
spawned = [False] * 4
for f in range(nframes):
    t = f / FPS
    for k, d in enumerate(DROPS):
        if not spawned[k] and t >= d[0]:
            activate(k); spawned[k] = True
    s = 0.0
    if STIR[0] <= t <= STIR[1]:
        u = (t - STIR[0]) / (STIR[1] - STIR[0]); s = 34.0 * math.sin(math.pi * u) ** 2
    stir[None] = s
    mixr[None] = 0.0 if t < MIX[0] else 0.0016 * min(1.0, (t - MIX[0]) / 2.0)
    t0 = time.time()
    for _ in range(SUBSTEPS):
        substep()
    ti.sync(); t1 = time.time(); t_sim += t1 - t0
    img = frame_image(); t_shade += time.time() - t1
    if proc: proc.stdin.write(img.tobytes())
    if f in stills and a.stills_dir:
        cv2.imwrite(f'{a.stills_dir}/still_{stills[f]}s.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if f % 30 == 0:
        print(f'frame {f}/{nframes} t={t:.1f}s sim={t_sim:.1f}s shade={t_shade:.1f}s', file=sys.stderr, flush=True)
if proc:
    proc.stdin.close(); proc.wait()
    import os; os.replace(a.out + '.part.mp4', a.out)
el = time.time() - t_start
print(json.dumps({'frames': nframes, 'seconds': round(el, 1), 'secPer100Frames': round(el / nframes * 100, 1),
                  'simSec': round(t_sim, 1), 'shadeSec': round(t_shade, 1), 'particles': N, 'grid': [NX, NY], 'substeps': SUBSTEPS}))
