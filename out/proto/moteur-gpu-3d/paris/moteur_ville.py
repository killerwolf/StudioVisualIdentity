#!/usr/bin/env python3
"""
villes.py — trois survols de ville avec le moteur wgpu de la maquette (phase 0). Ce ne sont PAS des shorts de preuve.

Paris, New York, Tokyo : plans INVENTÉS, seulement évocateurs (forme urbaine et quelques repères en volumes stylisés).
Tout est généré par code à partir d'une graine : aucune carte, tuile, image ni donnée géographique.

Le moteur est celui de `../maquette-source/maquette.py` (importé tel quel : palette indexée, carte peinte à deux tons
tramés par une matrice de Bayer, vote majoritaire, nuages en tas, traits d'écume, brume en paliers). Ce fichier ajoute :
  - un générateur de ville partagé : la ville est une CARTE DE HAUTEURS par case de 1 unité (≈ 8 m). Les toits sont
    les dessus des cases, peints dans la carte ; les façades sont les contremarches, avec une trame de fenêtres ;
    les ombres portées des immeubles viennent du même balayage que celles du relief ;
  - un plan par ville (`paris`, `newyork`, `tokyo`) : eau, parcs, voies, parcelles, hauteurs, toits, repères, caméra.

USAGE (depuis ce dossier, avec le .venv du prototype)
  ../.venv/bin/python villes.py paris --out sortie/paris.mp4 --stills 1.0,3.5 --json sortie/mesures_paris.json
  options : --gpu radeon|intel  --frames 0,75,149 (images isolées)  --dump x.npy  --seed N
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'maquette-source'))
import maquette as mq  # noqa: E402

NW, NH, SCALE, FPS, DUR = mq.NW, mq.NH, mq.SCALE, mq.FPS, 5.0
WX, WY, K = 896, 1150, 2
NX, NY = WX * K, WY * K
SUN, SUN_TAN, KSH = mq.SUN, mq.SUN_TAN, mq.KSH
pk, F_MAP, F_CLOUD, F_FAR, F_STROKE, DT = mq.pk, mq.F_MAP, mq.F_CLOUD, mq.F_FAR, mq.F_STROKE, mq.DT

# trame de fenêtres sur les façades : mode 3 ajouté au shader de la maquette (un rang sur deux, une colonne sur deux)
_OLD = "        if (mode == 2u && (hashi(q) & 7u) == 0u) { idx = (v.mat >> 8u) & 255u; }"
assert _OLD in mq.GEOM_WGSL
F_WALL = 16      # façade basse de la carte de hauteurs : au loin, elle n'est plus dessinée (plus fine qu'un pixel, elle scintille)
mq.GEOM_WGSL = mq.GEOM_WGSL.replace(
    _OLD, "        if ((flags & 16u) != 0u && dd > u.fog.z * WALL_K) { discard; }\n" + _OLD + "\n        if (mode == 3u && ((q.z >> WIN_S) & 1) != 0 && (((q.x >> WIN_S) + (q.y >> WIN_S)) & 1) != 0) { idx = (v.mat >> 8u) & 255u; }")

# ------------------------------------------------------------------ palette
COMMON = {k: mq.COL[k] for k in ('G1', 'G2', 'G3', 'G4', 'G5', 'T0', 'T1', 'T2', 'T3', 'S1', 'S2', 'W1', 'W2', 'W3', 'W4',
                                 'FOAM', 'C1', 'C2', 'C3')}


class CityPal:
    """Palette d'une ville : couleurs de base, ombre calculée (plus sombre et plus bleue), tables de brume."""
    SHADE_MUL = (0.56, 0.62, 0.80)
    SHADE_ADD = (0.0, 0.0, 0.0)

    def __init__(self, cols):
        for q in (12, 16, 20, 24, 32):
            self.rgb, self.by_rgb, self.ix = [], {}, {}
            for n, h in cols.items():
                self.ix[n] = self.add(mq.hex2rgb(h))
            nb = len(self.rgb)
            self.luts = np.zeros((7, 256), np.int32)
            self.luts[0] = np.arange(256)
            for i in range(nb):
                c = np.array(self.rgb[i], float)
                sh = np.round((c * np.array(self.SHADE_MUL) + np.array(self.SHADE_ADD)) / 8.0) * 8.0
                self.luts[0, i] = self.add(np.clip(sh, 0, 255))
            for n in ('C1', 'C2', 'C3'):
                self.luts[0, self.ix[n]] = self.ix[n]
            nb = len(self.rgb)
            haze = np.array(mq.hex2rgb(mq.HAZE), float)
            self.luts[1, :nb] = np.arange(nb)
            for s in range(1, 6):
                for i in range(nb):
                    c = np.array(self.rgb[i], float)
                    m = c + (haze - c) * mq.FOG_MIX[s]
                    if s < 5:
                        m = np.round(m / q) * q
                    self.luts[1 + s, i] = self.add(np.clip(m, 0, 255))
            sky = [self.add(mq.hex2rgb(c)) for c in mq.SKYC]
            if len(self.rgb) < 250:
                break
        assert len(self.rgb) < 250, len(self.rgb)
        self.luts = self.luts.astype(np.uint8)
        self.sky = np.array(sky, np.uint8)
        self.table = np.zeros((256, 3), np.uint8)
        self.table[:len(self.rgb)] = self.rgb

    def add(self, rgb):
        rgb = tuple(int(round(float(c))) for c in rgb)
        if rgb not in self.by_rgb:
            self.by_rgb[rgb] = len(self.rgb)
            self.rgb.append(rgb)
        return self.by_rgb[rgb]


# ------------------------------------------------------------------ outils de plan (par texel de 0,5 unité)
X = ((np.arange(NX) + 0.5) / K)[:, None].astype(np.float32)
Y = ((np.arange(NY) + 0.5) / K)[None, :].astype(np.float32)
XX = np.ascontiguousarray(np.broadcast_to(X, (NX, NY)))
YY = np.ascontiguousarray(np.broadcast_to(Y, (NX, NY)))


def seg(p, q):
    """Distance de chaque texel au segment p-q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = np.clip(((X - p[0]) * dx + (Y - p[1]) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(X - p[0] - t * dx, Y - p[1] - t * dy)


def poly(pts):
    d = seg(pts[0], pts[1])
    for a, b in zip(pts[1:-1], pts[2:]):
        d = np.minimum(d, seg(a, b))
    return d


def hi(a, b, salt=0):
    """Hachage entier de deux tableaux d'entiers -> uint32."""
    a = (a.astype(np.int64) & 0xFFFFFFFF).astype(np.uint32)
    b = (b.astype(np.int64) & 0xFFFFFFFF).astype(np.uint32)
    h = a * np.uint32(374761393) + b * np.uint32(668265263) + np.uint32((salt * 2246822519) & 0xFFFFFFFF)
    h = (h ^ (h >> np.uint32(13))) * np.uint32(1274126177)
    return h ^ (h >> np.uint32(16))


def r01(h, shift=0):
    return ((h >> np.uint32(shift)) & np.uint32(0xFFF)).astype(np.float32) / 4096.0


def noise(sc, rng):
    return mq.vnoise(NX, NY, sc * K, rng)


def cells_all(b):
    """Texels -> cases : vrai si les 4 texels de la case le sont."""
    return b[0::2, 0::2] & b[1::2, 0::2] & b[0::2, 1::2] & b[1::2, 1::2]


def up(c):
    return np.repeat(np.repeat(c, K, 0), K, 1)


def erode(b, n):
    for _ in range(n):
        b = b & np.roll(b, 1, 0) & np.roll(b, -1, 0) & np.roll(b, 1, 1) & np.roll(b, -1, 1)
    return b


def dilate(b, n):
    for _ in range(n):
        b = b | np.roll(b, 1, 0) | np.roll(b, -1, 0) | np.roll(b, 1, 1) | np.roll(b, -1, 1)
    return b


def districts(rng, size, nang, base=0.0, spread=math.pi / 2):
    """Quartiers : un angle de trame par cellule grossière déformée. Renvoie (u, v) : coordonnées tournées par texel."""
    cx = np.floor((X + 45.0 * (noise(90, rng) - 0.5) * 2) / size)
    cy = np.floor((Y + 45.0 * (noise(90, rng) - 0.5) * 2) / size)
    did = hi(cx, cy, 3)
    th = base + (r01(did) * nang).astype(int) / nang * spread
    c, s = np.cos(th).astype(np.float32), np.sin(th).astype(np.float32)
    return X * c + Y * s, -X * s + Y * c, did


def along(pts, step, off):
    """Points le long d'une ligne brisée, tous les `step`, décalés de `off` sur le côté."""
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.array(a, float), np.array(b, float)
        L = np.linalg.norm(b - a)
        d = (b - a) / L
        nrm = np.array([-d[1], d[0]])
        for t in np.arange(0, L, step):
            out.append(a + d * t + nrm * off)
    return np.array(out)


class Boxes:
    def __init__(self):
        self.b, self.m = [], []

    def add(self, x0, x1, y0, y1, z0, z1, top, west, south, east, north):
        self.b.append((x0, x1, y0, y1, z0, z1))
        self.m.append((top, west, south, east, north))

    def col(self, cx, cy, hw, z0, z1, f, hwy=None):
        hwy = hw if hwy is None else hwy
        self.add(cx - hw, cx + hw, cy - hwy, cy + hwy, z0, z1, *f)

    def emit(self, me):
        if not self.b:
            return
        b = np.array(self.b, np.float32)
        m = np.array(self.m, np.uint32)
        x0, x1, y0, y1, z0, z1 = b.T
        c = lambda *v: np.stack(v, 1)                                   # noqa: E731
        me.quads(c(x0, y0, z1), c(x1, y0, z1), c(x1, y1, z1), c(x0, y1, z1), m[:, 0])
        me.quads(c(x0, y0, z0), c(x0, y1, z0), c(x0, y1, z1), c(x0, y0, z1), m[:, 1])
        me.quads(c(x0, y0, z0), c(x1, y0, z0), c(x1, y0, z1), c(x0, y0, z1), m[:, 2])
        me.quads(c(x1, y0, z0), c(x1, y1, z0), c(x1, y1, z1), c(x1, y0, z1), m[:, 3])
        me.quads(c(x0, y1, z0), c(x1, y1, z0), c(x1, y1, z1), c(x0, y1, z1), m[:, 4])


def sun_tone(nx_, ny_):
    d = nx_ * SUN[0] + ny_ * SUN[1]
    return 0 if d > 0.6 else (1 if d > 0.02 else 2)


def orient(lit, mid, dark):
    """Matières (ouest, sud, est, nord) selon la direction du soleil."""
    t = (lit, mid, dark)
    return (t[sun_tone(-1, 0)], t[sun_tone(0, -1)], t[sun_tone(1, 0)], t[sun_tone(0, 1)])


def faces(P, lit, mid, dark, top=None, alt=None, mode=0):
    """Matières d'un volume : dessus, ouest (éclairé), sud, est et nord (à l'ombre)."""
    a = (lambda n: pk(P[n], P[alt], mode)) if alt else (lambda n: pk(P[n]))
    return (pk(P[top or lit]), a(lit), a(mid), a(dark), a(dark))


def lattice_tower(bx, zs, P, cx, cy, H, base, colors, bands=None):
    """Tour en treillis stylisée : quatre pieds, deux plates-formes, un fût qui s'effile, une flèche.
    colors : (clair, moyen, sombre) ; bands : seconde série de couleurs pour des bandes alternées."""
    def f(i):
        c = bands if (bands and i % 2) else colors
        return (pk(P[c[0]]), pk(P[c[0]], P[c[1]], 1), pk(P[c[1]], P[c[2]], 1), pk(P[c[2]]), pk(P[c[2]]))
    w = lambda z: base * (1 - z / H) ** 2.1 + 0.32                      # noqa: E731
    z1p, z2p = 0.17 * H, 0.36 * H
    n = 0
    for z0 in np.arange(0, z1p, z1p / 4):                               # quatre pieds écartés
        ww = w(z0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                bx.col(cx + sx * (ww - 1.1), cy + sy * (ww - 1.1), 1.15, z0, z0 + z1p / 4, f(n))
        n += 1
    bx.col(cx, cy, w(z1p) + 0.5, z1p, z1p + 0.8, f(0))                  # première plate-forme
    for z0 in np.arange(z1p + 0.8, z2p, (z2p - z1p - 0.8) / 4):
        ww = w(z0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                bx.col(cx + sx * (ww - 0.8), cy + sy * (ww - 0.8), 0.85, z0, z0 + (z2p - z1p - 0.8) / 4, f(n))
        n += 1
    bx.col(cx, cy, w(z2p) + 0.4, z2p, z2p + 0.7, f(0))                  # seconde plate-forme
    zz = np.linspace(z2p + 0.7, 0.9 * H, 10)
    for a, b in zip(zz[:-1], zz[1:]):
        bx.col(cx, cy, w(a), a, b, f(n))
        n += 1
    bx.col(cx, cy, 0.55, 0.9 * H, 0.93 * H, f(0))
    bx.col(cx, cy, 0.22, 0.93 * H, H, f(n))
    # colonne d'ombre : hauteur selon la distance à l'axe
    ix, iy = np.meshgrid(np.arange(int(cx - base - 1), int(cx + base + 2)), np.arange(int(cy - base - 1), int(cy + base + 2)), indexing='ij')
    r = np.maximum(np.abs(ix + 0.5 - cx), np.abs(iy + 0.5 - cy))
    hh = H * (1 - np.clip((r - 0.32) / base, 0, 1) ** (1 / 2.1))
    zs[ix, iy] = np.maximum(zs[ix, iy], np.where(r < base, hh, 0))


# ------------------------------------------------------------------ assemblage commun
def assemble(spec, pal, seed):
    """spec (par texel) : water, park, paved, bld, H, kind, roof, ph + listes. Renvoie le monde du moteur."""
    P = pal.ix
    rng = np.random.default_rng(seed + 50)
    hs = mq.hash2(NX, NY, 1)
    hb = mq.hash2(NX // 2 + 1, NY // 2 + 1, 21).repeat(2, 0).repeat(2, 1)[:NX, :NY]
    hb2 = mq.hash2(NX // 2 + 1, NY // 2 + 1, 22).repeat(2, 0).repeat(2, 1)[:NX, :NY]
    bc = cells_all(spec['bld'])
    z = np.where(bc, np.maximum(spec['H'][::K, ::K], 0.6), 0.0).astype(np.float32)
    for (mask_c, zz) in spec.get('raised', []):                         # viaducs, ponts, quais : cases surélevées
        z = np.where(mask_c & ~bc, zz, z).astype(np.float32)
    bld = up(z > 0) & up(bc)
    zf = up(z)
    kind = spec['kind'][::K, ::K]
    # ombres portées : balayage vers le soleil, immeubles et repères
    zs = np.maximum(z, spec['zshadow'])
    shade_c = np.zeros(z.shape, bool)
    reach = int(max(8, min(70, zs.max() / SUN_TAN + 2)))
    for i in range(1, reach):
        ox, oy = int(round(SUN[0] * i)), int(round(SUN[1] * i))
        src = np.roll(np.roll(zs, -ox, 0), -oy, 1)
        shade_c |= src > z + math.hypot(ox, oy) * SUN_TAN + 0.35
    shadow = up(shade_c)

    m = np.zeros((NX, NY), np.uint8)
    mb = np.zeros((NX, NY), np.uint8)
    ma = np.zeros((NX, NY), np.uint8)
    tag = np.zeros((NX, NY), np.uint8)

    def flat(mask, name):
        m[mask] = P[name]
        ma[mask] = 0

    def blend(mask, a, b, f):
        m[mask] = P[a]
        mb[mask] = P[b]
        ma[mask] = np.round(np.clip(f, 0, 1) * 15)[mask] if isinstance(f, np.ndarray) else int(round(f * 15))

    n1, n2 = noise(7, rng), noise(30, rng)
    # sol : chaussée, trottoirs au pied des immeubles
    g = spec['ground']
    blend(np.ones((NX, NY), bool), g['street'][0], g['street'][1], 0.25 + 0.5 * n2)
    walk = dilate(bld, 1) & ~bld
    flat(walk, g['walk'])
    for mask, a, b in spec.get('paved', []):
        blend(mask & ~bld, a, b, 0.2 + 0.6 * n1)
    # parcs : pelouses tramées, allées
    park = spec['park'] & ~bld
    blend(park, 'G3', 'G2', n1 * 1.3 - 0.1)
    blend(park & (n2 > 0.62), 'G2', 'G1', n1)
    for mask, name in spec.get('lines', []):
        flat(mask & ~bld, name)
    # eau : deux bandes tramées et reflets
    water = spec['water'] & ~bld
    wd = spec['wdepth']
    blend(water, g['water'][0], g['water'][1], np.clip(1.0 - wd / g.get('wscale', 9.0), 0, 1))
    tag[water & (hb < 0.02)] = 1 + (mq.hash2(NX, NY, 7)[water & (hb < 0.02)] * 4).astype(np.uint8)
    for mask, name in spec.get('over', []):                             # ponts, voies, tracés par-dessus l'eau
        flat(mask & ~bld, name)
        tag[mask] = 0
    # toits : deux tons tramés par parcelle, acrotères clair et sombre, détails semés
    ph = spec['ph']
    roofs = spec['roofs']
    ri = spec['roof']
    rfar = spec['roof_far'] if 'roof_far' in spec else ri              # au loin : un ton par type, ou par îlot
    for k, (a, b) in enumerate(roofs):
        flat(bld & (rfar == k), a)
    zE, zN = np.roll(zf, -1, 0), np.roll(zf, -1, 1)
    zW, zS = np.roll(zf, 1, 0), np.roll(zf, 1, 1)
    dark_edge = bld & ((zf > zE + 0.3) | (zf > zN + 0.3))
    lit_edge = bld & ((zf > zW + 0.3) | (zf > zS + 0.3)) & ~dark_edge
    for fn in spec.get('roofpaint', []):
        fn(m, mb, ma, bld, lit_edge, dark_edge, hb, hb2, flat, blend)
    m0 = m.copy()
    for k, (a, b) in enumerate(roofs):                                  # de près : deux tons, un par parcelle
        m0[bld & (ri == k)] = P[a]
        m0[bld & (ri == k) & (r01(ph, 8) < 0.5)] = P[b]
    if g.get('edges', False):                                           # acrotères, si la ville les demande
        m0[lit_edge] = P[g['edge_lit']]
        m0[dark_edge] = P[g['edge_dark']]
    for mask, name in spec.get('near', []):                             # détails de près seulement
        m0[mask & bld & ~lit_edge & ~dark_edge] = P[name]
    for (sel_name, name, dens) in spec.get('specks', []):
        sel = (m == P[sel_name]) & (ma == 0) if sel_name else bld
        m0[sel & (hb2 < dens)] = P[name]

    # arbres : ombre peinte
    t = spec['trees']
    if len(t):
        tx, ty, tz, tw, th = t.T
        R = 4
        oy_, ox_ = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1))
        for dx, dy in zip(ox_.ravel(), oy_.ravel()):
            cx = ((tx - KSH[0] * th * 0.75) * K).astype(int) + dx
            cy = ((ty - KSH[1] * th * 0.75) * K).astype(int) + dy
            ok = (dx * dx + dy * dy <= (tw * K * 1.05) ** 2) & (cx >= 0) & (cx < NX) & (cy >= 0) & (cy < NY)
            shadow[cx[ok], cy[ok]] = True
    # ombres portées : dans la carte de près seulement (au loin, plus fines qu'un pixel, elles scintillent)
    m0 = np.where(shadow, pal.luts[0][m0], m0)
    ma[shadow] = 0
    tag[shadow] = 0
    return {'z': z, 'kind': kind, 'map': m0, 'map_far': m, 'mapb': mb, 'mapa': ma, 'tag': tag,
            'open_water': water & (wd > 2.5) & ~dilate(~water, 2)}


def build_mesh(w, spec, pal, seed):
    P = pal.ix
    z = w['z']
    nx, ny = z.shape
    me = mq.Mesh()
    I, J = np.meshgrid(np.arange(nx, dtype=np.float32), np.arange(ny, dtype=np.float32), indexing='ij')
    B = 3000.0
    me.quads(np.array([[-B, -B, 0.0]]), np.array([[B, -B, 0.0]]), np.array([[B, B, 0.0]]), np.array([[-B, B, 0.0]]),
             pk(0, flags=F_MAP))
    sel = (z > 0).ravel()
    i, j, zz = I.ravel()[sel], J.ravel()[sel], z.ravel()[sel]
    me.quads(np.stack([i, j, zz], 1), np.stack([i + 1, j, zz], 1), np.stack([i + 1, j + 1, zz], 1),
             np.stack([i, j + 1, zz], 1), pk(0, flags=F_MAP))
    # façades : ton selon l'orientation, trame de fenêtres
    table = np.zeros((len(spec['kinds']), 3), np.uint32)
    for k, (lit, mid, dark, win) in enumerate(spec['kinds']):
        for tn, name in enumerate((lit, mid, dark)):
            table[k, tn] = pk(P[name], P[win], 3) if win else pk(P[name])
    low = np.uint32(F_WALL << 18)
    kind = w['kind']
    for (di, dj, tone) in ((1, 0, 2), (-1, 0, 0), (0, 1, 2), (0, -1, 1)):
        if spec.get('sun_tones'):                                        # ton selon le soleil : 0 en plein soleil, 1 rasant, 2 à l'ombre
            tone = sun_tone(di, dj)
        si, sj = slice(max(0, -di), nx - max(0, di)), slice(max(0, -dj), ny - max(0, dj))
        ti, tj = slice(max(0, di), nx - max(0, -di)), slice(max(0, dj), ny - max(0, -dj))
        hi_, lo = z[si, sj].ravel(), z[ti, tj].ravel()
        s = hi_ > lo + 0.05
        ii, jj, hi_, lo = I[si, sj].ravel()[s], J[si, sj].ravel()[s], hi_[s], lo[s]
        mat = table[kind[si, sj].ravel()[s], tone] | np.where(hi_ - lo < 4.5, low, np.uint32(0))
        if di == 1:
            a, b = np.stack([ii + 1, jj], 1), np.stack([ii + 1, jj + 1], 1)
        elif di == -1:
            a, b = np.stack([ii, jj], 1), np.stack([ii, jj + 1], 1)
        elif dj == 1:
            a, b = np.stack([ii, jj + 1], 1), np.stack([ii + 1, jj + 1], 1)
        else:
            a, b = np.stack([ii, jj], 1), np.stack([ii + 1, jj], 1)
        mz = hi_
        if 'mansard' in spec:                                            # façade jusqu'à la corniche, puis brisis à lucarnes
            mn = spec['mansard']
            sp = mn['hauss'][si, sj].ravel()[s] & ~mn['court'][ti, tj].ravel()[s] & (hi_ - lo > 3.0)
            mz = np.where(sp, hi_ - mn['h'], hi_)
            if 'court_mat' in mn:                                        # murs de cour : dans l'ombre, sans travées
                mat = np.where(mn['court'][ti, tj].ravel()[s], np.uint32(mn['court_mat']), mat)
            if sp.any():
                me.quads(np.column_stack([a, mz])[sp], np.column_stack([b, mz])[sp], np.column_stack([b, hi_])[sp],
                         np.column_stack([a, hi_])[sp], np.full(int(sp.sum()), mn['mats'][tone], np.uint32))
        me.quads(np.column_stack([a, lo]), np.column_stack([b, lo]), np.column_stack([b, mz]),
                 np.column_stack([a, mz]), mat)
    spec['boxes'].emit(me)
    an8 = (np.arange(8) + 0.5) * (2 * math.pi / 8)

    def prism(cx, cy, r, z0, z1, top, sides):
        ring = [np.stack([cx + r * math.cos(a_), cy + r * math.sin(a_)], 1) for a_ in an8]
        for k in range(8):
            a_, b_ = ring[k], ring[(k + 1) % 8]
            lit = float(np.array([math.cos(an8[k] + math.pi / 8), math.sin(an8[k] + math.pi / 8)]) @ SUN)
            me.quads(np.column_stack([a_, z0]), np.column_stack([b_, z0]), np.column_stack([b_, z1]),
                     np.column_stack([a_, z1]), sides[0 if lit > 0.3 else (1 if lit > -0.4 else 2)])
        cap = [np.column_stack([r_, z1]) for r_ in ring]
        me.quads(cap[0], cap[1], cap[2], cap[3], top)
        me.quads(cap[0], cap[3], cap[4], cap[7], top)
        me.quads(cap[7], cap[4], cap[5], cap[6], top)

    t = spec['trees']
    if len(t):
        tx, ty, tz, tw, th = t.T
        if spec.get('tree_simple'):                                      # houppier d'un seul volume : dessus uni, flanc éclairé
            prism(tx, ty, tw * 1.08, tz + 0.2, tz + th, pk(P['T1']), (pk(P['T0']), pk(P['T2']), pk(P['T3'])))
        else:
            prism(tx, ty, tw * 1.08, tz + 0.2, tz + th * 0.62, pk(P['T1']), (pk(P['T2']), pk(P['T3']), pk(P['T3'])))
            prism(tx - 0.26 * tw, ty - 0.2 * tw, tw * 0.76, tz + th * 0.62, tz + th, pk(P['T0'], P['T1'], 0, F_FAR),
                  (pk(P['T0'], P['T1'], 0, F_FAR), pk(P['T1']), pk(P['T2'])))
    for (cx, cy, r, z0, z1, top, sides) in spec.get('prisms', []):
        prism(np.array([cx], np.float32), np.array([cy], np.float32), r, np.array([z0], np.float32),
              np.array([z1], np.float32), top, sides)

    # reflets sur l'eau : les traits d'écume de la maquette, clairsemés
    sr = np.random.default_rng(seed + 3)
    NS = spec.get('strokes', 12000)
    qx, qy = sr.uniform(0, WX, NS), sr.uniform(0, WY, NS)
    ok = w['open_water'][(qx * K).astype(int), (qy * K).astype(int)]
    qx, qy = qx[ok], qy[ok]
    ph, ln = sr.integers(0, 4, len(qx)), sr.integers(0, 5, len(qx))
    for sg in (0, 1):
        q = np.zeros((len(qx), 6), DT)
        q['p'][:, :, 0], q['p'][:, :, 1], q['p'][:, :, 2] = qx[:, None], qy[:, None], 0.12
        base = (np.uint32(P['FOAM']) | np.uint32(sg << 10) | (ph.astype(np.uint32) << 11) | (ln.astype(np.uint32) << 13)
                | np.uint32(F_STROKE << 18))
        for k, corner in enumerate((0, 1, 3, 0, 3, 2)):
            q['m'][:, k] = base | np.uint32(corner << 8)
        me.parts.append(q.reshape(-1))

    # nuages : tas de boules ombrées (comme la maquette), plus haut que les tours
    czmin, czmax, ncl, rmin, rmax = spec['clouds']
    cr = np.random.default_rng(seed + 2)
    cb = spec.get('cloud_box', (-60, WX + 40, 20, WY - 20))
    cand = np.stack([cr.uniform(cb[0], cb[1], 2500), cr.uniform(cb[2], cb[3], 2500)], 1)
    centers = []
    keep_sun = spec.get('cloud_free')                                   # (p, q, rayon) : segment au sol que l'ombre des nuages évite
    for c in cand:
        if keep_sun is not None:
            sc = c - KSH * (czmin + czmax) / 2
            hit = False
            for p_, q_, rr in keep_sun:
                d_ = np.array(q_, float) - np.array(p_, float)
                t_ = np.clip(((sc - p_) @ d_) / (d_ @ d_), 0, 1)
                hit = hit or np.linalg.norm(sc - (np.array(p_, float) + t_ * d_)) < rr
            if hit:
                continue
        if all((c[0] - o[0]) ** 2 + (c[1] - o[1]) ** 2 > spec.get('cloud_gap', 60) ** 2 for o in centers):
            centers.append(c)
        if len(centers) >= ncl:
            break
    puffs = []
    for cx, cy in centers:
        big = cr.uniform(rmin, rmax)
        cz = cr.uniform(czmin, czmax)
        ang = cr.uniform(0, math.pi)
        nbig = int(cr.integers(2, 5))
        mine = []
        for k in range(nbig):
            off = (k - (nbig - 1) / 2) * big * 1.0 + cr.uniform(-1, 1)
            r = big * cr.uniform(0.75, 1.0)
            mine.append([cx + math.cos(ang) * off + cr.uniform(-1.5, 1.5), cy + math.sin(ang) * off + cr.uniform(-1.5, 1.5),
                         cz + r * 0.15, r])
        for k in range(int(cr.integers(4, 9))):
            b = mine[int(cr.integers(0, len(mine)))]
            r, a2 = b[3] * cr.uniform(0.45, 0.7), cr.uniform(0, 2 * math.pi)
            mine.append([b[0] + math.cos(a2) * b[3] * 0.4, b[1] + math.sin(a2) * b[3] * 0.4, b[2] + b[3] * 0.62 + r * 0.2, r])
        for k in range(int(cr.integers(2, 6))):
            b = mine[int(cr.integers(0, nbig))]
            r, a2 = b[3] * cr.uniform(0.35, 0.52), cr.uniform(0, 2 * math.pi)
            mine.append([b[0] + math.cos(a2) * b[3] * 0.92, b[1] + math.sin(a2) * b[3] * 0.92, b[2] - b[3] * 0.2, r])
        zb = min(q_[2] - 0.6 * q_[3] for q_ in mine)
        zt = max(q_[2] + 0.85 * q_[3] for q_ in mine)
        puffs += [q_ + [zb, zt] for q_ in mine]
    puffs = np.array(puffs, np.float32)
    px, py, pz, pr, pzb, pzt = puffs.T
    VS = 0.85
    thetas = np.radians([0.0, 22.0, 45.0, 68.0, 92.0, 116.0])
    L3 = np.array([SUN[0], SUN[1], 0.5]) / math.sqrt(1 + 0.5 ** 2)
    tones = np.array([pk(P['C3'], flags=F_CLOUD), pk(P['C2'], P['C3'], 1, F_CLOUD), pk(P['C2'], flags=F_CLOUD),
                      pk(P['C1'], P['C2'], 1, F_CLOUD), pk(P['C1'], P['C2'], 2, F_CLOUD), pk(P['C1'], flags=F_CLOUD)], np.uint32)
    for l in range(len(thetas) - 1):
        t0_, t1_ = thetas[l], thetas[l + 1]
        tm = (t0_ + t1_) / 2
        for k in range(8):
            a0, a1 = an8[k], an8[(k + 1) % 8]
            am = an8[k] + math.pi / 8
            nrm = np.array([math.sin(tm) * math.cos(am), math.sin(tm) * math.sin(am), math.cos(tm)])
            lam = float(nrm @ L3)
            hf = (pz + VS * pr * math.cos(tm) - pzb) / (pzt - pzb)
            lvl = np.digitize(0.62 * lam + 0.85 * (hf - 0.52), [-0.34, -0.14, 0.06, 0.26, 0.46])
            pt = lambda th_, a_: np.stack([px + pr * math.sin(th_) * math.cos(a_), py + pr * math.sin(th_) * math.sin(a_),   # noqa: E731
                                           pz + VS * pr * math.cos(th_)], 1)
            me.quads(pt(t0_, a0), pt(t0_, a1), pt(t1_, a1), pt(t1_, a0), tones[lvl])
    MG = 96
    mask = np.zeros((WX + 2 * MG, WY + 2 * MG), np.uint8)
    gx = np.arange(mask.shape[0])[:, None] - MG + 0.5
    gy = np.arange(mask.shape[1])[None, :] - MG + 0.5
    for x_, y_, z_, r_ in puffs[:, :4]:
        sx_, sy_ = x_ - KSH[0] * z_, y_ - KSH[1] * z_
        x0, x1 = int(max(0, sx_ - r_ + MG - 1)), int(min(mask.shape[0], sx_ + r_ + MG + 2))
        y0, y1 = int(max(0, sy_ - r_ + MG - 1)), int(min(mask.shape[1], sy_ + r_ + MG + 2))
        if x1 > x0 and y1 > y0:
            mask[x0:x1, y0:y1] |= ((gx[x0:x1] - sx_) ** 2 + (gy[:, y0:y1] - sy_) ** 2 <= (r_ * 0.95) ** 2)
    return me.done(), mask, MG


def park_trees(rng, mask, dens, step=2.6, size=(0.95, 1.5), z=None):
    gx, gy = np.meshgrid(np.arange(4, WX - 4, step), np.arange(4, WY - 4, step), indexing='ij')
    gx = gx + rng.uniform(-0.8, 0.8, gx.shape)
    gy = gy + rng.uniform(-0.8, 0.8, gy.shape)
    ix, iy = (gx * K).astype(int).ravel(), (gy * K).astype(int).ravel()
    d = dens[ix, iy] if isinstance(dens, np.ndarray) else dens
    keep = mask[ix, iy] & (rng.random(ix.shape) < d)
    tx, ty = gx.ravel()[keep], gy.ravel()[keep]
    tw = rng.uniform(size[0], size[1], tx.shape)
    return np.stack([tx, ty, np.zeros_like(tx), tw, tw * rng.uniform(1.5, 2.1, tx.shape)], 1).astype(np.float32)


def row_trees(rng, pts, step, off, w=0.95):
    p = along(pts, step, off)
    if not len(p):
        return np.zeros((0, 5), np.float32)
    p = p[(p[:, 0] > 4) & (p[:, 0] < WX - 4) & (p[:, 1] > 4) & (p[:, 1] < WY - 4)]
    tw = rng.uniform(w * 0.9, w * 1.15, len(p))
    return np.stack([p[:, 0], p[:, 1], np.zeros(len(p)), tw, tw * 1.8], 1).astype(np.float32)




# ------------------------------------------------------------------ caméra
def camera_table(cam, nframes):
    sub = 8
    n = nframes * sub + 1
    t = np.arange(n) / (FPS * sub)
    u = t / DUR
    e = u * u * (3 - 2 * u)
    yaw = np.radians(cam['yaw'][0] + (cam['yaw'][1] - cam['yaw'][0]) * e)
    vx, vy = np.sin(yaw) * cam['speed'], np.cos(yaw) * cam['speed']
    x = cam['start'][0] + np.concatenate([[0], np.cumsum((vx[1:] + vx[:-1]) / 2)]) / (FPS * sub)
    y = cam['start'][1] + np.concatenate([[0], np.cumsum((vy[1:] + vy[:-1]) / 2)]) / (FPS * sub)
    zc = cam['z'][0] + (cam['z'][1] - cam['z'][0]) * e + 1.5 * np.sin(t * 1.3)
    roll = np.clip(-1.15 * np.gradient(yaw, t), -0.30, 0.30)
    pitch = np.radians(cam['pitch'][0] + (cam['pitch'][1] - cam['pitch'][0]) * e)
    return [(np.array([x[i], y[i], zc[i]]), float(yaw[i]), float(pitch[i]), float(roll[i])) for i in range(0, n, sub)]


def main():
    ap = argparse.ArgumentParser()
    import plans
    PLANS = plans.PLANS
    ap.add_argument('city', choices=sorted(PLANS))
    ap.add_argument('--gpu', default='radeon', choices=['radeon', 'intel'])
    ap.add_argument('--seed', type=int, default=1811)
    ap.add_argument('--out')
    ap.add_argument('--frames')
    ap.add_argument('--stills')
    ap.add_argument('--dump')
    ap.add_argument('--json')
    a = ap.parse_args()
    out = Path(a.out or f'sortie/{a.city}.mp4')

    t0 = time.perf_counter()
    cols, plan = PLANS[a.city]
    pal = CityPal({**COMMON, **cols})
    spec = plan(sys.modules[__name__], a.seed, pal.ix)
    w = assemble(spec, pal, a.seed)
    mesh, mask, mg = build_mesh(w, spec, pal, a.seed)
    t_world = time.perf_counter() - t0
    nframes = int(round(DUR * FPS))
    if os.environ.get('CAM'):                                            # essais de caméra : vitesse, lacet de fin
        sp_, y1_ = os.environ['CAM'].split(',')
        spec['camera'] = {**spec['camera'], 'speed': float(sp_), 'yaw': (spec['camera']['yaw'][0], spec['camera']['yaw'][0] + float(y1_))}
    cams = camera_table(spec['camera'], nframes)
    zs = np.maximum(w['z'], spec['zshadow'])
    for eye, *_ in cams:                                                 # garde-fou : caméra au-dessus des toits
        i, j = int(np.clip(eye[0], 6, WX - 7)), int(np.clip(eye[1], 6, WY - 7))
        top = zs[i - 6:i + 7, j - 6:j + 7].max()
        assert eye[2] - top > 8.0, f'caméra trop basse à {eye} (toit {top})'
    t1 = time.perf_counter()
    mq.GEOM_WGSL = mq.GEOM_WGSL.replace('WIN_S', os.environ.get('WIN_S', str(spec.get('win_shift', 1))) + 'u')
    mq.GEOM_WGSL = mq.GEOM_WGSL.replace('WALL_K', str(float(os.environ.get('WALL_K', spec.get('wall_k', 2.0)))))
    eng = mq.Engine(a.gpu, 4, mesh, w, mask, mg, pal)
    fog = spec.get('fog', (250.0, 40.0, 110.0))
    f, r, u = mq.basis(*cams[0][1:])
    eng.frame(mq.view_proj(cams[0][0], f, r, u), cams[0][0], 0, *fog)
    t_init = time.perf_counter() - t1

    out.parent.mkdir(parents=True, exist_ok=True)
    todo = [int(x) for x in a.frames.split(',')] if a.frames else list(range(nframes))
    stills = {int(round(float(s) * FPS)): s for s in a.stills.split(',')} if a.stills else {}
    ff = None
    if not a.frames:
        part = out.with_suffix('.part.mp4')
        ff = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{NW}x{NH}',
             '-framerate', str(FPS), '-i', '-', '-vf', f'scale={NW * SCALE}:{NH * SCALE}:flags=neighbor',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS),
             '-movflags', '+faststart', str(part)], stdin=subprocess.PIPE)
    md5 = hashlib.md5()
    frames = np.zeros((len(todo), NH, NW), np.uint8) if a.dump else None
    ncol, tg = [], 0.0
    t2 = time.perf_counter()
    for k, n in enumerate(todo):
        eye, yaw, pitch, roll = cams[n]
        f, r, u = mq.basis(yaw, pitch, roll)
        ta = time.perf_counter()
        idx = eng.frame(mq.view_proj(eye, f, r, u), eye, n, *fog).copy()
        tg += time.perf_counter() - ta
        skym = idx == mq.SKY_CODE
        idx[skym] = mq.sky_bands(f, r, u, pal.sky)[skym]
        md5.update(idx.tobytes())
        ncol.append(len(np.unique(idx)))
        if frames is not None:
            frames[k] = idx
        rgb = pal.table[idx]
        if ff:
            ff.stdin.write(rgb.tobytes())
        if a.frames or n in stills:
            name = f'{a.city}_img_{n:03d}.png' if a.frames else f'{a.city}_{float(stills[n]):.2f}s.png'
            Image.fromarray(rgb).resize((NW * SCALE, NH * SCALE), Image.NEAREST).save(out.parent / name)
    if ff:
        ff.stdin.close()
        ff.wait()
        os.replace(part, out)
    total = time.perf_counter() - t2
    if a.dump:
        np.save(a.dump, frames)
    res = {
        'city': a.city, 'gpu': eng.info.get('device'), 'backend': eng.info.get('backend_type'), 'seed': a.seed,
        'frames': len(todo), 'triangles': len(mesh) // 3, 'trees': int(len(spec['trees'])),
        'worldBuildSec': round(t_world, 2), 'gpuInitSec': round(t_init, 2), 'renderSec': round(total, 2),
        'secPer100Frames': round(total / len(todo) * 100, 2), 'msPerFrameTotal': round(total / len(todo) * 1000, 1),
        'msPerFrameGpu': round(tg / len(todo) * 1000, 1),
        'colorsPerFrame': [int(min(ncol)), int(np.median(ncol)), int(max(ncol))], 'paletteSize': len(pal.rgb),
        'md5NativeIndexFrames': md5.hexdigest(),
        'md5Mp4': hashlib.md5(out.read_bytes()).hexdigest() if ff else None,
        'load1min': round(os.getloadavg()[0], 2),
    }
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
