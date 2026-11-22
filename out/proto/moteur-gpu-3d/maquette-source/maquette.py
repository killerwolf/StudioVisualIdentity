#!/usr/bin/env python3
"""
maquette.py — seconde maquette du moteur wgpu (phase 0), visée « qualité source ». Ce n'est PAS un short de preuve.

Un monde inventé : une côte (mer à l'ouest, plaine en terrasses, forêts, rivière, lac, montagnes à l'est), survolée par
une caméra qui avance et vire vers l'intérieur des terres. 5 s, 150 images, 270×480 agrandi ×4 (1080×1920).

Chaîne (tout en entiers côté carte graphique, voir la note de conception) :
  processeur, une fois : relief en terrasses, CARTE PEINTE du sol à 2 texels par unité (prés tramés, lignes de niveau,
      sable, roche, neige, bandes de profondeur de l'eau, frange d'écume, traits d'écume animés, ombres portées du
      relief et des arbres), maillage (dessus, contremarches, arbres en volumes, nuages en volumes), masque d'ombre
      des nuages, tables d'ombre et de brume ;
  carte graphique, par image : passe géométrie à 4 × (270×480) qui écrit un INDICE DE PALETTE par fragment
      (carte peinte ou matière du sommet, trame fixée dans le monde, ombre des nuages par table, brume en paliers
      tramés par table), puis vote majoritaire 4×4 ;
  processeur, par image : ciel en paliers tramés, palette, tuyau vers ffmpeg (×4 au plus proche voisin).

L'image n est un pur calcul de n (horloge pilotée). Graine dans --seed.

USAGE (depuis ce dossier, avec le .venv du prototype)
  ../.venv/bin/python maquette.py --out sortie/maquette.mp4 --stills 0.5,1.5,2.5,3.5,4.5 --json sortie/mesures.json
  options : --gpu radeon|intel  --ss 1|2|4  --seed 1811  --frames 0,45,90 (images isolées, sans vidéo)  --dump x.npy
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
import wgpu
from PIL import Image

NW, NH, SCALE, FPS = 270, 480, 4, 30
DUR = 5.0
WX, WY = 896, 1150          # monde, en unités ; une case = 1 unité, un texel de carte = 0,5 unité
K = 2                       # texels par unité
STEP = 2.0                  # hauteur d'une terrasse
SKY_CODE = 255
SUN = np.array([-0.80, -0.60])      # direction horizontale VERS le soleil (sud-ouest)
SUN_TAN = 1.15                      # tangente de sa hauteur
KSH = SUN / SUN_TAN                 # décalage horizontal de l'ombre par unité de hauteur (vers le soleil)

# ------------------------------------------------------------------ palette (propre à la maquette)
COL = {
    # prés
    'G1': '#C2EB5C', 'G2': '#97DA44', 'G3': '#6CC43C', 'G4': '#43A23B', 'G5': '#2C7F38',
    # arbres
    'T0': '#58AD3E', 'T1': '#3A8F3B', 'T2': '#27703A', 'T3': '#184F34',
    # sable, terre, roche, neige
    'S1': '#F4E6AE', 'S2': '#DEC88A', 'S3': '#B79C68',
    'R1': '#C4BDB2', 'R2': '#9A938E', 'R3': '#716B74', 'N1': '#FFFFFF', 'N2': '#CFDDF0',
    # eau
    'W0': '#7FD8EC', 'W1': '#45B0E0', 'W2': '#2C8BD0', 'W3': '#216FBC', 'W4': '#1B59A4', 'FOAM': '#F2FCFF',
    # nuages
    'C1': '#FFFFFF', 'C2': '#CDD5F0', 'C3': '#9EABD8',
    # ombres
    'SH_G': '#2E8A48', 'SH_GD': '#1F6540', 'SH_T': '#123F33', 'SH_S': '#B5A27C', 'SH_R': '#5E5A6C',
    'SH_N': '#A9BCDD', 'SH_W': '#17478F', 'SH_W1': '#2A78BE', 'SH_F': '#9CC4E6',
}
SHADE = {'G1': 'SH_G', 'G2': 'SH_G', 'G3': 'SH_G', 'G4': 'SH_GD', 'G5': 'SH_GD', 'T0': 'T2', 'T1': 'T3', 'T2': 'SH_T',
         'T3': 'SH_T', 'S1': 'SH_S', 'S2': 'SH_S', 'S3': 'SH_R', 'R1': 'R3', 'R2': 'SH_R', 'R3': 'SH_R', 'N1': 'SH_N',
         'N2': 'SH_N', 'W0': 'SH_W1', 'W1': 'SH_W1', 'W2': 'SH_W', 'W3': 'SH_W', 'W4': 'SH_W', 'FOAM': 'SH_F'}
HAZE = '#D3EAF7'
SKYC = ['#D3EAF7', '#C3E2F5', '#B0D8F2', '#9CCDEF', '#89C2EB']
FOG_MIX = [0.0, 0.12, 0.26, 0.42, 0.62, 1.0]
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


class Pal:
    def __init__(self):
        self.rgb, self.by_rgb, self.ix = [], {}, {}
        for n, h in COL.items():
            self.ix[n] = self.add(hex2rgb(h))
        nb = len(self.rgb)
        haze = np.array(hex2rgb(HAZE), float)
        self.luts = np.zeros((7, 256), np.uint8)             # ligne 0 : ombre ; lignes 1..6 : paliers de brume 0..5
        self.luts[0] = np.arange(256)
        for n, s in SHADE.items():
            self.luts[0, self.ix[n]] = self.ix[s]
        for s in range(6):
            for i in range(nb):
                c = np.array(self.rgb[i], float)
                m = c + (haze - c) * FOG_MIX[s]
                if 0 < s < 5:
                    m = np.round(m / 12.0) * 12.0            # regroupe les teintes voisines : palette bornée
                self.luts[1 + s, i] = self.add(np.clip(m, 0, 255)) if s else i
        self.sky = np.array([self.add(hex2rgb(c)) for c in SKYC], np.uint8)
        assert len(self.rgb) < 250, len(self.rgb)
        self.table = np.zeros((256, 3), np.uint8)
        self.table[:len(self.rgb)] = self.rgb

    def add(self, rgb):
        rgb = tuple(int(round(float(c))) for c in rgb)
        if rgb not in self.by_rgb:
            self.by_rgb[rgb] = len(self.rgb)
            self.rgb.append(rgb)
        return self.by_rgb[rgb]


# ------------------------------------------------------------------ bruits (numpy seul, graine)
def vnoise(nx, ny, scale, rng):
    gx, gy = int(nx / scale) + 3, int(ny / scale) + 3
    g = rng.random((gx, gy))
    x, y = np.arange(nx) / scale, np.arange(ny) / scale
    x0, y0 = x.astype(int), y.astype(int)
    fx, fy = x - x0, y - y0
    fx, fy = (fx * fx * (3 - 2 * fx))[:, None], (fy * fy * (3 - 2 * fy))[None, :]
    a, b = g[np.ix_(x0, y0)], g[np.ix_(x0 + 1, y0)]
    c, d = g[np.ix_(x0, y0 + 1)], g[np.ix_(x0 + 1, y0 + 1)]
    return ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy).astype(np.float32)


def hash2(nx, ny, k):
    """Hachage entier par texel, dans [0, 1) : la trame, fixée dans le monde."""
    x = np.arange(nx, dtype=np.uint32)[:, None]
    y = np.arange(ny, dtype=np.uint32)[None, :]
    h = x * np.uint32(374761393) + y * np.uint32(668265263) + np.uint32((k * 2246822519) & 0xFFFFFFFF)
    h = (h ^ (h >> np.uint32(13))) * np.uint32(1274126177)
    h = h ^ (h >> np.uint32(16))
    return (h & np.uint32(0xFFFF)).astype(np.float32) / 65536.0


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ monde
def build_world(seed, pal):
    rng = np.random.default_rng(seed)
    P = pal.ix
    nx, ny = WX * K, WY * K
    X = ((np.arange(nx) + 0.5) / K)[:, None].astype(np.float32)
    Y = ((np.arange(ny) + 0.5) / K)[None, :].astype(np.float32)
    n = lambda sc: vnoise(nx, ny, sc * K, rng)                           # noqa: E731
    # s : distance signée au rivage (positive = terre). Côte à l'ouest, découpée en caps et en anses.
    s = (X - 265.0) + 150.0 * (n(190) - 0.5) + 60.0 * (n(70) - 0.5) + 16.0 * (n(22) - 0.5)
    s += 46.0 * np.exp(-(((X - 150) / 20.0) ** 2 + ((Y - 505) / 30.0) ** 2))      # un îlot rocheux
    s += 40.0 * np.exp(-(((X - 85) / 14.0) ** 2 + ((Y - 760) / 18.0) ** 2))       # un écueil
    p = np.clip(s / 400.0, 0, 1)
    ridge = 1.0 - np.abs(2.0 * n(120) - 1.0)
    roll = n(55)
    h = 1.2 + 9.0 * smooth(s / 70.0) * (0.35 + roll) + 92.0 * p * p * (0.3 + 0.7 * ridge) + 5.0 * (n(18) - 0.5) * p
    # rivière : des montagnes vers la mer ; lac dans la plaine
    yr = 640.0 + 55.0 * np.sin(X / 65.0) + 30.0 * np.sin(X / 23.0 + 1.0)
    wr = 2.2 + 4.5 * np.clip(1.0 - s / 260.0, 0, 1)
    river = (np.abs(Y - yr) < wr + 1.5 * (n(12) - 0.5)) & (s > 0) & (X < 640)
    lake = (((X - 430) / 36.0) ** 2 + ((Y - 430) / 24.0) ** 2 + 0.5 * (n(25) - 0.5)) < 1.0
    valley = np.exp(-((Y - yr) / (9.0 + wr * 2)) ** 2) * (s > 0)
    h = h * (1 - 0.55 * valley)
    lk = np.exp(-(((X - 430) / 70.0) ** 2 + ((Y - 430) / 52.0) ** 2))
    h = h * (1 - 0.72 * lk) + 1.5 * lk
    land = s > 0
    # --- cases (1 unité) : niveau entier, altitude du dessus
    hc, sc = h[::K, ::K], s[::K, ::K]
    lev = np.maximum(1, np.floor(hc / STEP)).astype(np.int32)
    z = lev * STEP
    beach_c = (sc < 5.0) & (sc > 0)
    z = np.where(beach_c, 0.5, z)
    rc, lc = river[::K, ::K], lake[::K, ::K]
    z = np.where(rc | lc, np.maximum(z - STEP, 0.5), z)
    # la rivière ne remonte jamais : altitude plafonnée par le cumul depuis la mer
    sea_c = sc <= 0
    z = np.where(sea_c, 0.0, z).astype(np.float32)
    zf = np.repeat(np.repeat(z, K, 0), K, 1)                               # altitude par texel
    levf = np.repeat(np.repeat(lev, K, 0), K, 1)
    water_in = river | lake

    # --- ombre portée du relief (par case), soleil au sud-ouest
    shade_c = np.zeros(z.shape, bool)
    for i in range(1, 60):
        ox, oy = int(round(SUN[0] * i)), int(round(SUN[1] * i))
        src = np.roll(np.roll(z, -ox, 0), -oy, 1)
        shade_c |= src > z + math.hypot(ox, oy) * SUN_TAN + 0.6
    shadow = np.repeat(np.repeat(shade_c, K, 0), K, 1)

    # --- carte peinte : par texel, un ton A, un ton B et la part de B en seizièmes. La carte graphique choisit entre A
    # et B avec une matrice de Bayer posée sur les pixels natifs : de la trame partout, sans texel isolé qui scintille.
    hs = hash2(nx, ny, 1)
    hb = hash2(nx // 2 + 1, ny // 2 + 1, 21).repeat(2, 0).repeat(2, 1)[:nx, :ny]      # blocs de 2×2 texels
    m = np.zeros((nx, ny), np.uint8)
    mb = np.zeros((nx, ny), np.uint8)
    ma = np.zeros((nx, ny), np.uint8)
    tag = np.zeros((nx, ny), np.uint8)

    def ramp(mask, f, names, width=0.8):
        f = np.clip(f, 0, len(names) - 1 - 1e-4)
        i = np.floor(f).astype(int)
        fr = np.clip((f - i - 0.5 + width / 2) / width, 0, 1)
        lut = np.array([P[x] for x in names], np.uint8)
        m[mask] = lut[i][mask]
        mb[mask] = lut[i + 1][mask]
        ma[mask] = np.round(fr * 15)[mask]

    def flat(mask, name):
        m[mask] = P[name]
        ma[mask] = 0

    # prés : 4 verts ; lumière directionnelle sur les pentes (plus clair face au soleil)
    gxh, gyh = np.gradient(h, 1.0 / K)
    lum = -(gxh * SUN[0] + gyh * SUN[1])
    g = n(26) + 0.5 * n(9) + 0.10 * (levf % 2)
    ramp(land, np.interp(g, [0.42, 0.62, 0.88, 1.12], [0, 1, 2, 3]) + np.clip(lum * 1.5, -1.2, 1.2) + 0.9 * (n(4) - 0.5),
         ['G4', 'G3', 'G2', 'G1'], width=0.45)
    # lignes de niveau : filet sombre sur le bord d'une terrasse dont la paroi tourne le dos à la caméra (nord, est),
    # filet clair sur le bord qui regarde le soleil (ouest, sud)
    zE, zN = np.roll(zf, -1, 0), np.roll(zf, -1, 1)
    zW, zS = np.roll(zf, 1, 0), np.roll(zf, 1, 1)
    dark_edge = (zf > zE + 0.1) | (zf > zN + 0.1)
    lit_edge = ((zf > zW + 0.1) | (zf > zS + 0.1)) & ~dark_edge
    foot = ((zE > zf + 0.1) | (zN > zf + 0.1))                              # pied d'une paroi vue de face
    flat(lit_edge & land, 'G1')
    flat(dark_edge & land, 'G5')
    hq = np.floor(h / 1.0)
    mid = ((hq > np.roll(hq, -1, 0)) | (hq > np.roll(hq, -1, 1))) & ~dark_edge & ~lit_edge & land
    darker = np.arange(256, dtype=np.uint8)
    for a_, b_ in (('G1', 'G2'), ('G2', 'G3'), ('G3', 'G4'), ('G4', 'G5')):
        darker[P[a_]] = P[b_]
    m[mid] = darker[m[mid]]
    ma[mid] = 0
    # forêts : bouquets sombres sur terre claire
    fo = n(34) + 0.6 * n(11)
    forest = (fo > 1.02) & land & (s > 9) & (h < 50) & ~water_in
    grove = (fo > 0.93) & (hash2(nx // 8 + 1, ny // 8 + 1, 5).repeat(8, 0).repeat(8, 1)[:nx, :ny] < 0.14) & land & (s > 9) & (h < 50) & ~water_in
    lone = (hash2(nx // 4 + 1, ny // 4 + 1, 9).repeat(4, 0).repeat(4, 1)[:nx, :ny] < 0.012) & land & (s > 9) & (h < 40) & ~water_in
    wood = forest | grove | lone
    flat(forest | grove, 'T3')
    # roche et neige, éclairées par la pente
    rk = h + 10.0 * (n(15) - 0.5)
    rock = (rk > 44) & land
    ramp(rock, 1.0 + np.clip(lum * 2.0, -1.0, 1.0) + 0.7 * (n(8) - 0.5), ['R3', 'R2', 'R1'])
    flat(rock & dark_edge, 'R3')
    snow = (rk > 57) & land
    ramp(snow, 0.75 + np.clip(lum * 2.2, -0.75, 0.25), ['N2', 'N1'])
    flat(snow & dark_edge, 'N2')
    # sable : plage et berges, puis frange tramée sable / pré
    slim = 5.0 + 3.0 * (n(10) - 0.5)
    sand = land & (s < slim)
    flat(sand, 'S1')
    fringe = land & ~sand & (s < slim + 4.5) & ~wood
    mb[fringe] = P['S1']
    ma[fringe] = np.round(13 * np.clip(1 - (s - slim) / 4.5, 0, 1))[fringe]
    # mer : bandes de profondeur à bords tramés, hauts-fonds
    d = -s + 26.0 * (n(60) - 0.5) + 10.0 * (n(20) - 0.5)
    bar = n(45)
    d = d - 34.0 * smooth((bar - 0.66) / 0.2) * smooth((-s - 20) / 40.0)       # bancs clairs au large
    sea = ~land
    ramp(sea, np.interp(d, [4.2, 6.8, 13.0, 21.0, 34.0, 54.0, 76.0, 116.0], [4, 3, 3, 2, 2, 1, 1, 0]),
         ['W4', 'W3', 'W2', 'W1', 'W0'])
    # frange d'écume au rivage : pleine au bord, tramée ensuite, et une part qui bat à 2 Hz
    ds = -s
    solid = sea & (ds < 1.3 + 1.2 * (n(6) - 0.5))
    fb = sea & (ds < 5.5) & ~solid
    mb[fb] = P['FOAM']
    ma[fb] = np.round(12 * np.clip(1 - ds / 5.5, 0, 1))[fb]
    flat(solid, 'FOAM')
    fr = sea & (ds < 4.5) & (hb < 0.30)
    tag[fr] = 1 + (hash2(nx, ny, 7)[fr] * 4).astype(np.uint8)
    # rivière et lac
    wd = water_in & land
    flat(wd, 'W1')
    rad = ((X - 430) / 36.0) ** 2 + ((Y - 430) / 24.0) ** 2
    ramp(lake & wd, np.interp(rad, [0.30, 0.62], [0.0, 1.0]) + np.zeros_like(h), ['W2', 'W1'])
    flat(wd & foot, 'S2')
    tag[wd & (hb < 0.03)] = 1 + (hash2(nx, ny, 7)[wd & (hb < 0.03)] * 4).astype(np.uint8)

    # --- arbres : grappes sur une grille perturbée, plus denses au cœur des bois
    tr = np.random.default_rng(seed + 1)
    gx, gy = np.meshgrid(np.arange(4, WX - 4, 2.7), np.arange(4, WY - 4, 2.7), indexing='ij')
    gx = gx + tr.uniform(-0.9, 0.9, gx.shape)
    gy = gy + tr.uniform(-0.9, 0.9, gy.shape)
    ix, iy = (gx * K).astype(int).ravel(), (gy * K).astype(int).ravel()
    keep = wood[ix, iy] & (tr.random(ix.shape) < np.where(forest[ix, iy], 0.92, 0.75)) & ~sand[ix, iy] & ~rock[ix, iy]
    tx, ty = gx.ravel()[keep], gy.ravel()[keep]
    tz = z[tx.astype(int), ty.astype(int)]
    tw = tr.uniform(0.95, 1.55, tx.shape)
    th = tw * tr.uniform(1.5, 2.1, tx.shape)
    trees = np.stack([tx, ty, tz, tw, th], 1).astype(np.float32)
    # ombre portée de chaque arbre, peinte dans la carte (à l'opposé du soleil)
    R = 4
    oy_, ox_ = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1))
    for dx, dy in zip(ox_.ravel(), oy_.ravel()):
        cx = ((tx - KSH[0] * th * 0.75) * K).astype(int) + dx
        cy = ((ty - KSH[1] * th * 0.75) * K).astype(int) + dy
        ok = (dx * dx + dy * dy <= (tw * K * 1.05) ** 2) & (cx >= 0) & (cx < nx) & (cy >= 0) & (cy < ny)
        shadow[cx[ok], cy[ok]] = True
    # mouchetures : par blocs de 2×2 texels, seulement dans la carte de près (les réductions partent de la carte nue)
    m0 = m.copy()
    for a_, b_, dens in (('S1', 'S2', 0.12), ('R1', 'R3', 0.04), ('R2', 'R3', 0.04), ('G2', 'G1', 0.03),
                         ('G3', 'G2', 0.03), ('W2', 'W1', 0.010), ('W3', 'W2', 0.010), ('W4', 'W3', 0.008)):
        m0[(m == P[a_]) & (hb < dens)] = P[b_]
    m0[wd & (m == P['W1']) & (hb < 0.08)] = P['W0']
    m = np.where(shadow, pal.luts[0][m], m)
    m0 = np.where(shadow, pal.luts[0][m0], m0)
    mb = np.where(shadow, pal.luts[0][mb], mb)
    tag[shadow & land] = 0
    return {'z': z, 'map': m0, 'map_far': m, 'mapb': mb, 'mapa': ma, 'tag': tag, 'rock': (rock | snow)[::K, ::K],
            'snow': snow[::K, ::K], 'sand': sand[::K, ::K], 'water': (water_in | sea)[::K, ::K], 'trees': trees,
            'open_sea': sea & (ds > 6.0)}


def mode2x2(a):
    """Réduction ×2 par vote majoritaire (jamais de moyenne) ; à égalité, le texel en haut à gauche."""
    x, y = a.shape[0] // 2 * 2, a.shape[1] // 2 * 2
    q = [a[0:x:2, 0:y:2], a[1:x:2, 0:y:2], a[0:x:2, 1:y:2], a[1:x:2, 1:y:2]]
    out = q[0].copy()
    best = sum((q[0] == o).astype(np.int8) for o in q)
    for c in q[1:]:
        n = sum((c == o).astype(np.int8) for o in q)
        out = np.where(n > best, c, out)
        best = np.maximum(best, n)
    return out


def any2x2(a):
    x, y = a.shape[0] // 2 * 2, a.shape[1] // 2 * 2
    return np.maximum(np.maximum(a[0:x:2, 0:y:2], a[1:x:2, 0:y:2]), np.maximum(a[0:x:2, 1:y:2], a[1:x:2, 1:y:2]))


def pk(a, b=0, mode=0, flags=0):
    return np.uint32(a) | (np.uint32(b) << 8) | (np.uint32(mode) << 16) | (np.uint32(flags) << 18)


F_MAP, F_CLOUD, F_FAR, F_STROKE = 1, 2, 4, 8
DT = np.dtype([('p', np.float32, 3), ('m', np.uint32)])


class Mesh:
    def __init__(self):
        self.parts = []

    def quads(self, p0, p1, p2, p3, m):
        n = len(p0)
        q = np.zeros((n, 6), DT)
        for k, p in enumerate((p0, p1, p2, p0, p2, p3)):
            q['p'][:, k, :] = p
        q['m'][:] = np.broadcast_to(np.asarray(m, np.uint32), (n,))[:, None]
        self.parts.append(q.reshape(-1))

    def done(self):
        return np.concatenate(self.parts)


def build_mesh(w, pal, seed):
    P = pal.ix
    z = w['z']
    nx, ny = z.shape
    me = Mesh()
    I, J = np.meshgrid(np.arange(nx, dtype=np.float32), np.arange(ny, dtype=np.float32), indexing='ij')
    # mer : un seul grand plan (la carte est lue par position, bornée à ses bords)
    B = 3000.0
    me.quads(np.array([[-B, -B, 0.0]]), np.array([[B, -B, 0.0]]), np.array([[B, B, 0.0]]), np.array([[-B, B, 0.0]]),
             pk(0, flags=F_MAP))
    # dessus des cases de terre
    sel = (z > 0).ravel()
    i, j, zz = I.ravel()[sel], J.ravel()[sel], z.ravel()[sel]
    me.quads(np.stack([i, j, zz], 1), np.stack([i + 1, j, zz], 1), np.stack([i + 1, j + 1, zz], 1),
             np.stack([i, j + 1, zz], 1), pk(0, flags=F_MAP))
    # contremarches : ton selon l'orientation (ouest et sud éclairées)
    tones = {'g': (P['G4'], P['G4'], P['T3']), 'r': (P['R1'], P['R1'], P['R3']), 's': (P['S2'], P['S2'], P['S3']),
             'n': (P['N1'], P['N1'], P['N2'])}
    kind = np.where(w['snow'], 3, np.where(w['rock'], 1, np.where(w['sand'] | w['water'], 2, 0)))
    for (di, dj, tone) in ((1, 0, 2), (-1, 0, 0), (0, 1, 2), (0, -1, 1)):
        si, sj = slice(max(0, -di), nx - max(0, di)), slice(max(0, -dj), ny - max(0, dj))
        ti, tj = slice(max(0, di), nx - max(0, -di)), slice(max(0, dj), ny - max(0, -dj))
        hi, lo = z[si, sj].ravel(), z[ti, tj].ravel()
        s = hi > lo + 0.05
        ii, jj, hi, lo = I[si, sj].ravel()[s], J[si, sj].ravel()[s], hi[s], lo[s]
        kk = np.maximum(kind[si, sj].ravel()[s], np.where(hi - lo > 2 * STEP + 0.1, 1, 0) * (kind[si, sj].ravel()[s] == 0))
        mat = np.choose(kk, [pk(tones['g'][tone]), pk(tones['r'][tone]), pk(tones['s'][tone]), pk(tones['n'][tone])])
        if di == 1:
            a, b = np.stack([ii + 1, jj], 1), np.stack([ii + 1, jj + 1], 1)
        elif di == -1:
            a, b = np.stack([ii, jj], 1), np.stack([ii, jj + 1], 1)
        elif dj == 1:
            a, b = np.stack([ii, jj + 1], 1), np.stack([ii + 1, jj + 1], 1)
        else:
            a, b = np.stack([ii, jj], 1), np.stack([ii + 1, jj], 1)
        me.quads(np.column_stack([a, lo]), np.column_stack([b, lo]), np.column_stack([b, hi]),
                 np.column_stack([a, hi]), mat)

    def box(cx, cy, hw, z0, z1, top, west, south, east, north):
        x0, x1, y0, y1 = cx - hw, cx + hw, cy - hw, cy + hw
        c = lambda *v: np.stack(np.broadcast_arrays(*v), 1)              # noqa: E731
        me.quads(c(x0, y0, z1), c(x1, y0, z1), c(x1, y1, z1), c(x0, y1, z1), top)
        me.quads(c(x0, y0, z0), c(x0, y1, z0), c(x0, y1, z1), c(x0, y0, z1), west)
        me.quads(c(x0, y0, z0), c(x1, y0, z0), c(x1, y0, z1), c(x0, y0, z1), south)
        me.quads(c(x1, y0, z0), c(x1, y1, z0), c(x1, y1, z1), c(x1, y0, z1), east)
        me.quads(c(x0, y1, z0), c(x1, y1, z0), c(x1, y1, z1), c(x0, y1, z1), north)

    # arbres : deux volumes empilés, dessus clair moucheté, flancs sombres à l'opposé du soleil
    t = w['trees']
    tx, ty, tz, tw, th = t.T
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

    prism(tx, ty, tw * 1.08, tz + 0.2, tz + th * 0.62, pk(P['T1']), (pk(P['T2']), pk(P['T3']), pk(P['T3'])))
    prism(tx - 0.26 * tw, ty - 0.2 * tw, tw * 0.76, tz + th * 0.62, tz + th, pk(P['T0'], P['T1'], 0, F_FAR),
          (pk(P['T0'], P['T1'], 0, F_FAR), pk(P['T1']), pk(P['T2'])))

    # traits d'écume au large : des quadrilatères posés sur l'eau, élargis par le shader pour rester visibles au loin
    sr = np.random.default_rng(seed + 3)
    NS = 34000
    qx, qy = sr.uniform(-320, WX, NS), sr.uniform(0, WY, NS)
    osea = w['open_sea']
    ok = (qx < 0) | osea[np.clip((qx * K).astype(int), 0, osea.shape[0] - 1), np.clip((qy * K).astype(int), 0, osea.shape[1] - 1)]
    qx, qy = qx[ok], qy[ok]
    ph, ln = sr.integers(0, 4, len(qx)), sr.integers(0, 8, len(qx))
    for seg in (0, 1):
        q = np.zeros((len(qx), 6), DT)
        q['p'][:, :, 0], q['p'][:, :, 1], q['p'][:, :, 2] = qx[:, None], qy[:, None], 0.12
        base = (np.uint32(P['FOAM']) | np.uint32(seg << 10) | (ph.astype(np.uint32) << 11) | (ln.astype(np.uint32) << 13)
                | np.uint32(F_STROKE << 18))
        for k, corner in enumerate((0, 1, 3, 0, 3, 2)):
            q['m'][:, k] = base | np.uint32(corner << 8)
        me.parts.append(q.reshape(-1))

    # nuages : tas de coton en volumes. Chaque nuage = quelques grosses boules, de plus petites empilées dessus et au
    # bord ; chaque boule est une sphère à facettes, ombrée par facette (soleil) et par étage (le bas du tas est sombre)
    cr = np.random.default_rng(seed + 2)
    cand = np.stack([cr.uniform(-60, WX + 40, 2500), cr.uniform(20, WY - 20, 2500)], 1)
    centers = []
    for c in cand:
        if all((c[0] - o[0]) ** 2 + (c[1] - o[1]) ** 2 > 40 ** 2 for o in centers):
            centers.append(c)
        if len(centers) >= 300:
            break
    puffs = []
    for cx, cy in centers:
        big = cr.uniform(4.2, 7.4)
        cz = cr.uniform(24, 34)
        ang = cr.uniform(0, math.pi)
        nbig = int(cr.integers(2, 5))
        mine = []
        for k in range(nbig):
            off = (k - (nbig - 1) / 2) * big * 1.0 + cr.uniform(-1, 1)
            r = big * cr.uniform(0.75, 1.0)
            mine.append([cx + math.cos(ang) * off + cr.uniform(-1.5, 1.5), cy + math.sin(ang) * off + cr.uniform(-1.5, 1.5),
                         cz + r * 0.15, r])
        for k in range(int(cr.integers(4, 9))):                      # boules empilées
            b = mine[int(cr.integers(0, len(mine)))]
            r, a2 = b[3] * cr.uniform(0.45, 0.7), cr.uniform(0, 2 * math.pi)
            mine.append([b[0] + math.cos(a2) * b[3] * 0.4, b[1] + math.sin(a2) * b[3] * 0.4, b[2] + b[3] * 0.62 + r * 0.2, r])
        for k in range(int(cr.integers(2, 6))):                      # petites boules au bord
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
    L3 = np.array([SUN[0], SUN[1], 0.5]) / math.sqrt(1 + 0.5 ** 2)          # soleil abaissé pour le modelé
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
            zmid = pz + VS * pr * math.cos(tm)
            hf = (zmid - pzb) / (pzt - pzb)
            val = 0.62 * lam + 0.85 * (hf - 0.52)
            lvl = np.digitize(val, [-0.34, -0.14, 0.06, 0.26, 0.46])
            pt = lambda th_, a_: np.stack([px + pr * math.sin(th_) * math.cos(a_), py + pr * math.sin(th_) * math.sin(a_),   # noqa: E731
                                           pz + VS * pr * math.cos(th_)], 1)
            me.quads(pt(t0_, a0), pt(t0_, a1), pt(t1_, a1), pt(t1_, a0), tones[lvl])
    # masque d'ombre des nuages : disques projetés sur le plan z = 0, 1 texel par unité, marge pour la dérive
    MG = 64
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


# ------------------------------------------------------------------ caméra : table calculée une fois, lue par n
VFOV = math.radians(58.0)
NEAR, FAR = 3.0, 760.0


def camera_table(nframes):
    sub = 8
    n = nframes * sub + 1
    t = np.arange(n) / (FPS * sub)
    u = t / DUR
    e = u * u * (3 - 2 * u)
    yaw = np.radians(8.0 + 38.0 * e)                       # vire vers l'est, vers l'intérieur des terres
    speed = 50.0
    vx, vy = np.sin(yaw) * speed, np.cos(yaw) * speed
    x = 212.0 + np.concatenate([[0], np.cumsum((vx[1:] + vx[:-1]) / 2)]) / (FPS * sub)
    y = 150.0 + np.concatenate([[0], np.cumsum((vy[1:] + vy[:-1]) / 2)]) / (FPS * sub)
    zc = 78.0 - 8.0 * e + 2.0 * np.sin(t * 1.3)
    yaw_rate = np.gradient(yaw, t)
    roll = np.clip(-1.15 * yaw_rate, -0.30, 0.30)
    pitch = np.radians(-25.0 + 5.0 * e)
    return [(np.array([x[i], y[i], zc[i]]), float(yaw[i]), float(pitch[i]), float(roll[i])) for i in range(0, n, sub)]


def basis(yaw, pitch, roll):
    f = np.array([math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)])
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    r, u = r * math.cos(roll) + u * math.sin(roll), u * math.cos(roll) - r * math.sin(roll)
    return f, r, u


def view_proj(eye, f, r, u):
    V = np.eye(4)
    V[0, :3], V[1, :3], V[2, :3] = r, u, -f
    V[:3, 3] = -V[:3, :3] @ eye
    th = math.tan(VFOV / 2)
    Pm = np.zeros((4, 4))
    Pm[0, 0], Pm[1, 1] = 1 / (th * NW / NH), 1 / th
    Pm[2, 2], Pm[2, 3], Pm[3, 2] = FAR / (NEAR - FAR), NEAR * FAR / (NEAR - FAR), -1
    return Pm @ V


def sky_bands(f, r, u, sky_idx):
    th = math.tan(VFOV / 2)
    x = ((np.arange(NW) + 0.5) / NW * 2 - 1) * th * NW / NH
    y = (1 - (np.arange(NH) + 0.5) / NH * 2) * th
    dz = f[2] + x[None, :] * r[2] + y[:, None] * u[2]
    el = dz / np.sqrt(1 + x[None, :] ** 2 + y[:, None] ** 2)
    bay = (BAYER[np.arange(NH)[:, None] % 4, np.arange(NW)[None, :] % 4] + 0.5) / 16.0
    v = np.clip(el, 0, 1) * 13.0                            # paliers de plus en plus hauts, bords tramés
    band = np.clip(np.floor(v + (bay - 0.5) * 0.9), 0, len(sky_idx) - 1).astype(int)
    return sky_idx[band]


# ------------------------------------------------------------------ carte graphique
GEOM_WGSL = """
struct U { vp: mat4x4f, cam: vec4f, fog: vec4f, anim: vec4f, misc: vec4u };
@group(0) @binding(0) var<uniform> u: U;
@group(0) @binding(1) var map: texture_2d<u32>;
@group(0) @binding(2) var cmask: texture_2d<u32>;
@group(0) @binding(3) var luts: texture_2d<u32>;
struct VO {
    @builtin(position) pos: vec4f,
    @location(0) world: vec3f,
    @location(1) local: vec3f,
    @location(2) @interpolate(flat) mat: u32,
};
@vertex
fn vs(@location(0) p: vec3f, @location(1) mat: u32) -> VO {
    var o: VO;
    var w = p;
    if (((mat >> 18u) & 2u) != 0u) { w = vec3f(p.xy + u.anim.xy, p.z); }     // les nuages dérivent
    if (((mat >> 18u) & 8u) != 0u) {
        // trait d'écume : deux segments en zigzag, orientés dans le monde, jamais plus fins qu'un pixel natif
        let corner = (mat >> 8u) & 3u;
        let seg = f32((mat >> 10u) & 1u) * 2.0 - 1.0;
        let ph = (mat >> 11u) & 3u;
        let ln = f32((mat >> 13u) & 7u);
        let px = distance(p, u.cam.xyz) / 433.0;                 // taille monde d'un pixel natif à cette distance
        let hw = max(0.24, 0.60 * px);
        let hl = max(0.30 + 0.09 * ln, 1.3 * px);
        let dir = vec2f(0.342, 0.940);
        let perp = vec2f(0.940, -0.342);
        let sx = f32(corner & 1u) * 2.0 - 1.0;
        let sy = f32((corner >> 1u) & 1u) * 2.0 - 1.0;
        var c = p.xy + seg * (dir * hl + perp * hw);
        c = c + dir * sy * hl + perp * sx * hw;
        if (((ph + u.misc.x) %% 4u) >= 2u) { c = p.xy; }          // caché une phase sur deux : il bat
        w = vec3f(c, p.z);
    }
    o.pos = u.vp * vec4f(w, 1.0);
    o.world = w;
    o.local = p;
    o.mat = mat;
    return o;
}
fn hashi(q: vec3i) -> u32 {
    var h = bitcast<u32>(q.x) * 374761393u + bitcast<u32>(q.y) * 668265263u + bitcast<u32>(q.z) * 2246822519u;
    h = (h ^ (h >> 13u)) * 1274126177u;
    return h ^ (h >> 16u);
}
const T = array<f32, 5>(1.0, 1.32, 1.68, 2.08, 2.5);
const BAYER = array<f32, 16>(0., 8., 2., 10., 12., 4., 14., 6., 3., 11., 1., 9., 15., 7., 13., 5.);
const SS = %(ss)d;
@fragment
fn fs(v: VO) -> @location(0) u32 {
    let flags = v.mat >> 18u;
    var idx = v.mat & 255u;
    if ((flags & 1u) != 0u) {
        let dd = distance(v.world, u.cam.xyz);
        var lv = 0;
        if (dd > u.fog.z) { lv = 1; }
        if (dd > u.fog.z * 2.0) { lv = 2; }
        if (dd > u.fog.z * 4.0) { lv = 3; }
        let size = vec2i(textureDimensions(map, lv));
        let tc = clamp(vec2i(floor(v.world.xy * 2.0)) >> vec2u(u32(lv)), vec2i(0), size - vec2i(1));
        let m = textureLoad(map, tc, lv);
        idx = m.r;
        let nb = vec2i(v.pos.xy) / SS;
        if (f32(m.a) > BAYER[(nb.y & 3) * 4 + (nb.x & 3)]) { idx = m.b; }
        let lt = max(lv - 1, 0);
        let st = vec2i(textureDimensions(map, lt));
        let tg = textureLoad(map, clamp(vec2i(floor(v.world.xy * 2.0)) >> vec2u(u32(lt)), vec2i(0), st - vec2i(1)), lt).g;
        if (lv < 3 && tg != 0u && ((tg + u.misc.x) %% 4u) < 2u) { idx = u.misc.w; }
        if (false && m.g != 0u && ((m.g + u.misc.x) %% 4u) < 2u) { idx = u.misc.w; }       // écume qui bat
    } else {
        var mode = (v.mat >> 16u) & 3u;
        let dd = distance(v.world, u.cam.xyz);
        if (dd > u.fog.z * 2.6 && (flags & 4u) != 0u) { idx = (v.mat >> 8u) & 255u; }
        if (dd > u.fog.z * 1.5 || (flags & 8u) != 0u) { mode = 0u; }
        let q = vec3i(floor(v.local * 2.0 + vec3f(0.013, 0.017, 0.011)));
        if (mode == 1u && ((q.x + q.y + q.z) & 1) != 0) { idx = (v.mat >> 8u) & 255u; }
        if (mode == 2u && (hashi(q) & 7u) == 0u) { idx = (v.mat >> 8u) & 255u; }
    }
    if ((flags & 2u) == 0u) {                                                      // ombre des nuages
        let sp = v.world.xy + u.anim.zw * v.world.z - u.anim.xy + vec2f(f32(u.misc.y), f32(u.misc.y));
        let sc = vec2i(floor(sp));
        let ms = vec2i(textureDimensions(cmask));
        if (sc.x >= 0 && sc.y >= 0 && sc.x < ms.x && sc.y < ms.y && textureLoad(cmask, sc, 0).r != 0u) {
            idx = textureLoad(luts, vec2i(i32(idx), 0), 0).r;
        }
    }
    // brume : paliers selon la distance, bords tramés par une matrice de Bayer posée sur les pixels natifs
    let d = distance(v.world, u.cam.xyz);
    let n = vec2i(v.pos.xy) / SS;
    let b = (BAYER[(n.y & 3) * 4 + (n.x & 3)] + 0.5) / 16.0 - 0.5;
    let dj = d + b * u.fog.y;
    var s = 0;
    for (var i = 0; i < 5; i++) {
        if (dj > u.fog.x * T[i]) { s = i + 1; }
    }
    return textureLoad(luts, vec2i(i32(idx), 1 + s), 0).r;
}
"""

VOTE_WGSL = """
@group(0) @binding(0) var g: texture_2d<u32>;
@vertex
fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
    var p = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
    return vec4f(p[i], 0.0, 1.0);
}
const SS = %(ss)d;
const N = %(n)d;
@fragment
fn fs(@builtin(position) pos: vec4f) -> @location(0) u32 {
    let base = vec2i(pos.xy) * SS;
    var s: array<u32, N>;
    for (var i = 0; i < N; i++) { s[i] = textureLoad(g, base + vec2i(i %% SS, i / SS), 0).r; }
    var best = 0u;
    var bestn = 0;
    for (var i = 0; i < N; i++) {
        var n = 0;
        for (var j = 0; j < N; j++) { if (s[j] == s[i]) { n++; } }
        if (n > bestn || (n == bestn && s[i] < best)) { best = s[i]; bestn = n; }
    }
    return best;
}
"""


class Engine:
    def __init__(self, gpu, ss, mesh, w, mask, mg, pal):
        adapters = wgpu.gpu.enumerate_adapters_sync()
        match = [a for a in adapters if gpu in a.info['device'].lower()]
        if not match:
            sys.exit(f"carte « {gpu} » introuvable ; vues : {[a.info['device'] for a in adapters]}")
        self.info = dict(match[0].info)
        self.device = d = match[0].request_device_sync()
        self.ss, self.mg, self.foam = ss, mg, pal.ix['FOAM']
        gw, gh = NW * ss, NH * ss
        TU = wgpu.TextureUsage

        def tex(arr, fmt, bpp):
            a = np.ascontiguousarray(arr)
            h, wd = a.shape[:2]
            t = d.create_texture(size=(wd, h, 1), format=fmt, usage=TU.TEXTURE_BINDING | TU.COPY_DST)
            d.queue.write_texture({'texture': t}, a.tobytes(), {'bytes_per_row': wd * bpp, 'rows_per_image': h}, (wd, h, 1))
            return t

        # carte peinte et ses réductions par vote : le détail plus fin qu'un pixel ne scintille pas au loin
        NLOD = 4
        code = lambda a_: a_.astype(np.uint32) | (w['mapb'].astype(np.uint32) << 8) | (w['mapa'].astype(np.uint32) << 16)   # noqa: E731
        mp, far, tg = code(w['map']), code(w['map_far']), w['tag']
        self.t_map = d.create_texture(size=(mp.shape[0], mp.shape[1], 1), format='rgba8uint', mip_level_count=NLOD,
                                      usage=TU.TEXTURE_BINDING | TU.COPY_DST)
        for lv in range(NLOD):
            rgba = np.ascontiguousarray(np.stack([(mp & 255).T, tg.T, ((mp >> 8) & 255).T, ((mp >> 16) & 255).T], 2).astype(np.uint8))
            d.queue.write_texture({'texture': self.t_map, 'mip_level': lv}, rgba.tobytes(),
                                  {'bytes_per_row': rgba.shape[1] * 4, 'rows_per_image': rgba.shape[0]},
                                  (rgba.shape[1], rgba.shape[0], 1))
            mp, tg = mode2x2(far if lv == 0 else mp), (any2x2(tg) if lv == 0 else mode2x2(tg))
        self.t_mask = tex(mask.T, 'r8uint', 1)
        self.t_luts = tex(pal.luts, 'r8uint', 1)
        self.gtex = d.create_texture(size=(gw, gh, 1), format='r8uint', usage=TU.RENDER_ATTACHMENT | TU.TEXTURE_BINDING)
        self.depth = d.create_texture(size=(gw, gh, 1), format='depth32float', usage=TU.RENDER_ATTACHMENT)
        self.out = d.create_texture(size=(NW, NH, 1), format='r8uint', usage=TU.RENDER_ATTACHMENT | TU.COPY_SRC)
        self.vbuf = d.create_buffer_with_data(data=mesh, usage=wgpu.BufferUsage.VERTEX)
        self.nverts = len(mesh)
        self.ubuf = d.create_buffer(size=128, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST)
        gmod = d.create_shader_module(code=GEOM_WGSL % {'ss': ss})
        self.gpipe = d.create_render_pipeline(
            layout='auto',
            vertex={'module': gmod, 'entry_point': 'vs', 'buffers': [{
                'array_stride': 16, 'step_mode': 'vertex',
                'attributes': [{'format': 'float32x3', 'offset': 0, 'shader_location': 0},
                               {'format': 'uint32', 'offset': 12, 'shader_location': 1}]}]},
            primitive={'topology': 'triangle-list', 'cull_mode': 'none'},
            depth_stencil={'format': 'depth32float', 'depth_write_enabled': True, 'depth_compare': 'less'},
            fragment={'module': gmod, 'entry_point': 'fs', 'targets': [{'format': 'r8uint'}]},
        )
        self.gbind = d.create_bind_group(layout=self.gpipe.get_bind_group_layout(0), entries=[
            {'binding': 0, 'resource': {'buffer': self.ubuf}},
            {'binding': 1, 'resource': self.t_map.create_view()},
            {'binding': 2, 'resource': self.t_mask.create_view()},
            {'binding': 3, 'resource': self.t_luts.create_view()}])
        vmod = d.create_shader_module(code=VOTE_WGSL % {'ss': ss, 'n': ss * ss})
        self.vpipe = d.create_render_pipeline(
            layout='auto', vertex={'module': vmod, 'entry_point': 'vs'}, primitive={'topology': 'triangle-list'},
            fragment={'module': vmod, 'entry_point': 'fs', 'targets': [{'format': 'r8uint'}]})
        self.vbind = d.create_bind_group(layout=self.vpipe.get_bind_group_layout(0),
                                         entries=[{'binding': 0, 'resource': self.gtex.create_view()}])
        self.gview, self.dview, self.oview = self.gtex.create_view(), self.depth.create_view(), self.out.create_view()

    def frame(self, vp, eye, n, d_ref=250.0, amp=float(os.environ.get('MQ_AMP', '40')), lod=float(os.environ.get('MQ_LOD', '110'))):
        d = self.device
        t = n / FPS
        drift = (round(2.2 * t * 2) / 2, round(0.9 * t * 2) / 2)          # dérive des nuages, par demi-unité
        uf = np.zeros(28, np.float32)
        uf[:16] = vp.T.astype(np.float32).ravel()
        uf[16:19] = eye
        uf[20:23] = (d_ref, amp, lod)
        uf[24:28] = (drift[0], drift[1], -KSH[0], -KSH[1])
        ui = np.array([n // 8, self.mg, 0, self.foam], np.uint32)        # phase d'écume : 4 états, 8 images chacun
        d.queue.write_buffer(self.ubuf, 0, uf.tobytes() + ui.tobytes())
        enc = d.create_command_encoder()
        rp = enc.begin_render_pass(
            color_attachments=[{'view': self.gview, 'clear_value': (SKY_CODE, 0, 0, 0), 'load_op': 'clear',
                                'store_op': 'store'}],
            depth_stencil_attachment={'view': self.dview, 'depth_clear_value': 1.0, 'depth_load_op': 'clear',
                                      'depth_store_op': 'discard'})
        rp.set_pipeline(self.gpipe)
        rp.set_bind_group(0, self.gbind)
        rp.set_vertex_buffer(0, self.vbuf)
        rp.draw(self.nverts)
        rp.end()
        rp = enc.begin_render_pass(color_attachments=[{'view': self.oview, 'clear_value': (0, 0, 0, 0),
                                                       'load_op': 'clear', 'store_op': 'store'}])
        rp.set_pipeline(self.vpipe)
        rp.set_bind_group(0, self.vbind)
        rp.draw(3)
        rp.end()
        d.queue.submit([enc.finish()])
        data = d.queue.read_texture({'texture': self.out}, {'bytes_per_row': NW}, (NW, NH, 1))
        return np.frombuffer(data, np.uint8).reshape(NH, NW)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='radeon', choices=['radeon', 'intel'])
    ap.add_argument('--ss', type=int, default=4, choices=[1, 2, 4])
    ap.add_argument('--seed', type=int, default=1811)
    ap.add_argument('--out', default='sortie/maquette.mp4')
    ap.add_argument('--frames', help='numéros d\'images isolées (PNG dans le dossier de --out), sans vidéo')
    ap.add_argument('--stills', help='instants en secondes, PNG 1080×1920 à côté de --out')
    ap.add_argument('--dump', help='écrit les images natives (indices de palette) en .npy')
    ap.add_argument('--json')
    a = ap.parse_args()

    t0 = time.perf_counter()
    pal = Pal()
    w = build_world(a.seed, pal)
    mesh, mask, mg = build_mesh(w, pal, a.seed)
    t_world = time.perf_counter() - t0
    nframes = int(round(DUR * FPS))
    cams = camera_table(nframes)
    for eye, *_ in cams:                                                 # garde-fou : caméra au-dessus du relief
        zc = w['z'][int(np.clip(eye[0], 0, WX - 1)), int(np.clip(eye[1], 0, WY - 1))]
        assert eye[2] - zc > 12.0, f'caméra trop basse à {eye}'
    t1 = time.perf_counter()
    eng = Engine(a.gpu, a.ss, mesh, w, mask, mg, pal)
    f, r, u = basis(*cams[0][1:])
    eng.frame(view_proj(cams[0][0], f, r, u), cams[0][0], 0)
    t_init = time.perf_counter() - t1

    out = Path(a.out)
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
        f, r, u = basis(yaw, pitch, roll)
        ta = time.perf_counter()
        idx = eng.frame(view_proj(eye, f, r, u), eye, n).copy()
        tg += time.perf_counter() - ta
        skym = idx == SKY_CODE
        idx[skym] = sky_bands(f, r, u, pal.sky)[skym]
        md5.update(idx.tobytes())
        ncol.append(len(np.unique(idx)))
        if frames is not None:
            frames[k] = idx
        rgb = pal.table[idx]
        if ff:
            ff.stdin.write(rgb.tobytes())
        if a.frames or n in stills:
            name = f'img_{n:03d}.png' if a.frames else f'still_{float(stills[n]):.2f}s.png'
            Image.fromarray(rgb).resize((NW * SCALE, NH * SCALE), Image.NEAREST).save(out.parent / name)
    if ff:
        ff.stdin.close()
        ff.wait()
        os.replace(part, out)
    total = time.perf_counter() - t2
    if a.dump:
        np.save(a.dump, frames)
    res = {
        'gpu': eng.info.get('device'), 'backend': eng.info.get('backend_type'), 'wgpu': wgpu.__version__, 'ss': a.ss,
        'seed': a.seed, 'frames': len(todo), 'triangles': len(mesh) // 3, 'trees': int(len(w['trees'])),
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
