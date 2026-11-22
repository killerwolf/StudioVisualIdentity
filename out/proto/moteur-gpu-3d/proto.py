#!/usr/bin/env python3
"""
proto.py — prototype de phase 0 du moteur 3D sur carte graphique (wgpu-py, Metal). Ce n'est PAS un short de preuve.

Scène minimale : une vallée en terrasses (maillage de triangles construit par numpy à partir d'une graine), une caméra
qui avance en virant. Rendu en pixel art indexé :

  1. passe « géométrie » sur la carte graphique, à SS × (270×480), dans une cible ENTIÈRE r8uint : chaque fragment
     écrit un code = matière × 8 + palier de brume. Aucune couleur, aucun mélange, aucun anticrénelage flottant ;
  2. passe « vote » sur la carte graphique : chaque pixel natif 270×480 prend le code MAJORITAIRE de ses SS×SS
     échantillons (égalité : le plus petit code). On reste en palette indexée ;
  3. relecture de 129 600 octets, table code -> indice de palette -> RVB (numpy), ciel en paliers (numpy) ;
  4. tuyau vers ffmpeg, qui agrandit ×4 au plus proche voisin (1080×1920) et encode en H.264 yuv420p, 30 i/s.

L'horloge est pilotée : l'image n est un pur calcul de t = n / 30 (aucun temps réel, aucun état caché).
Les ombres portées du relief sont calculées une fois par monde sur le processeur et rangées dans la matière :
pas de carte d'ombre sur la carte graphique, donc pas de scintillement d'ombre.

USAGE (depuis ce dossier)
  .venv/bin/python proto.py --out sortie/proto.mp4                 # 6 s, Radeon, SS = 4
  .venv/bin/python proto.py --gpu intel --no-video --dump /chemin/hors/depot/intel.npy
  options : --gpu radeon|intel  --ss 1|2|4|8  --seconds 6  --seed 2611  --cell 1.0  --stills 0.5,3,5.5
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
STEP = 2.5            # hauteur d'une terrasse (unités monde)
NX, NY = 448, 704     # étendue du monde (unités monde)
NSTEPS = 6            # paliers de brume 0..5 ; le dernier est la couleur du bas du ciel
SKY_CODE = 255

# ------------------------------------------------------------------ palette (provisoire, propre au prototype)
MATS = ['WATER', 'WATER_SH', 'SAND', 'GRASS_L', 'GRASS_M', 'FOREST', 'GRASS_SH', 'ROCK', 'ROCK_SH', 'SNOW', 'SNOW_SH',
        'EARTH_L', 'EARTH_M', 'EARTH_D', 'STONE_L', 'STONE_M', 'STONE_D']
M = {n: i for i, n in enumerate(MATS)}
BASE = {
    'WATER': '#2F7FC1', 'WATER_SH': '#1F5C9A', 'SAND': '#E9D79A', 'GRASS_L': '#A4D65A', 'GRASS_M': '#6FB83E',
    'FOREST': '#2E7D3A', 'GRASS_SH': '#3F8F4A', 'ROCK': '#A79F93', 'ROCK_SH': '#7C766F', 'SNOW': '#F6FAFB',
    'SNOW_SH': '#B9CADB', 'EARTH_L': '#D9A86A', 'EARTH_M': '#B5804C', 'EARTH_D': '#7D5536',
    'STONE_L': '#C9C2B6', 'STONE_M': '#948C82', 'STONE_D': '#625C58',
}
FAMILY = {  # la brume fond chaque matière dans la rampe de sa famille : peu de couleurs au loin
    'WATER': 'W', 'WATER_SH': 'W', 'SAND': 'ML', 'GRASS_L': 'GL', 'GRASS_M': 'GL', 'FOREST': 'GD', 'GRASS_SH': 'GD',
    'ROCK': 'ML', 'ROCK_SH': 'MD', 'SNOW': 'ML', 'SNOW_SH': 'MD', 'EARTH_L': 'ML', 'EARTH_M': 'MD', 'EARTH_D': 'MD',
    'STONE_L': 'ML', 'STONE_M': 'MD', 'STONE_D': 'MD',
}
FAMILY_BASE = {'W': '#3F8BC8', 'GL': '#86C255', 'GD': '#3E8A48', 'ML': '#CDBE9C', 'MD': '#8E8274'}
HAZE = '#DDEDF3'
SKY = ['#DDEDF3', '#C6E2F0', '#A9D3EC', '#8BC2E6', '#70B2E0']   # du bas vers le haut ; SKY[0] = HAZE
FOG_MIX = [0.0, 0.22, 0.44, 0.64, 0.82, 1.0]


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def build_palette():
    """Renvoie (palette RVB uint8 [n,3], table code -> indice de palette [256])."""
    colors, index = [], {}

    def add(rgb):
        rgb = tuple(int(round(c)) for c in rgb)
        if rgb not in index:
            index[rgb] = len(colors)
            colors.append(rgb)
        return index[rgb]

    haze = np.array(hex2rgb(HAZE), float)
    lut = np.zeros(256, np.uint8)
    for name, m in M.items():
        fam = np.array(hex2rgb(FAMILY_BASE[FAMILY[name]]), float)
        for s in range(NSTEPS):
            if s == 0:
                rgb = hex2rgb(BASE[name])
            else:
                rgb = fam + (haze - fam) * FOG_MIX[s]
            lut[m * 8 + s] = add(rgb)
    sky = [add(hex2rgb(c)) for c in SKY]
    return np.array(colors, np.uint8), lut, np.array(sky, np.uint8)


# ------------------------------------------------------------------ monde
def vnoise(nx, ny, scale, rng):
    """Bruit de valeur lissé (numpy seul), dans [0, 1], tableau [nx, ny]."""
    gx, gy = int(nx / scale) + 3, int(ny / scale) + 3
    g = rng.random((gx, gy))
    x = np.arange(nx) / scale
    y = np.arange(ny) / scale
    x0, y0 = x.astype(int), y.astype(int)
    fx, fy = x - x0, y - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = g[np.ix_(x0, y0)]
    b = g[np.ix_(x0 + 1, y0)]
    c = g[np.ix_(x0, y0 + 1)]
    d = g[np.ix_(x0 + 1, y0 + 1)]
    fx = fx[:, None]
    fy = fy[None, :]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def river_x(y):
    return NX / 2 + 28.0 * np.sin(y / 90.0)


def build_world(seed, cell):
    """Carte de niveaux entiers (terrasses) et carte de matières, sur une grille de pas `cell`."""
    rng = np.random.default_rng(seed)
    nx, ny = int(NX / cell), int(NY / cell)
    k = 1.0 / cell
    n = (0.55 * vnoise(nx, ny, 120 * k, rng) + 0.27 * vnoise(nx, ny, 48 * k, rng)
         + 0.13 * vnoise(nx, ny, 20 * k, rng) + 0.05 * vnoise(nx, ny, 9 * k, rng))
    ridge = 1.0 - np.abs(2.0 * vnoise(nx, ny, 150 * k, rng) - 1.0)
    n = 0.6 * n + 0.4 * ridge * n * 1.6
    X = (np.arange(nx)[:, None] + 0.5) * cell
    Y = (np.arange(ny)[None, :] + 0.5) * cell
    d = np.abs(X - river_x(Y))
    v = np.clip(d / 95.0, 0, 1)
    v = v * v * (3 - 2 * v)
    height = (0.07 + 0.93 * v) * n * 84.0 + np.clip((d - 5.0) / 6.0, 0, 1) * 1.2
    height[d < 4.5 + 2.0 * vnoise(nx, ny, 30 * k, rng)] = 0.0
    lev = np.floor(height / STEP).astype(np.int32)

    # ombre portée du relief, une fois par monde : soleil au sud-ouest
    sun_xy = np.array([-0.77, -0.64])
    slope = 0.55                                  # tangente de la hauteur du soleil
    shade = np.zeros(lev.shape, bool)
    h = lev * STEP
    for i in range(1, int(48 / cell) + 1):
        ox, oy = int(round(sun_xy[0] * i)), int(round(sun_xy[1] * i))
        if ox == 0 and oy == 0:
            continue
        src = np.roll(np.roll(h, -ox, axis=0), -oy, axis=1)   # hauteur du voisin côté soleil
        shade |= src > h + math.hypot(ox, oy) * cell * slope + 0.5
    # matières des dessus
    tex = vnoise(nx, ny, 14 * k, rng)
    tex2 = vnoise(nx, ny, 5 * k, rng)
    mat = np.full(lev.shape, M['GRASS_M'], np.uint32)
    mat[(tex > 0.55) | ((lev % 2 == 0) & (tex > 0.42))] = M['GRASS_L']
    mat[(lev >= 4) & (lev < 15) & (tex2 * 0.6 + tex * 0.4 > 0.56)] = M['FOREST']
    mat[lev == 1] = M['SAND']
    rock = lev >= 15 + (tex * 3).astype(int)
    mat[rock] = M['ROCK']
    snow = lev >= 20 + (tex2 * 2).astype(int)
    mat[snow] = M['SNOW']
    mat[lev == 0] = M['WATER']
    sh = shade
    mat[sh & (mat == M['WATER'])] = M['WATER_SH']
    mat[sh & np.isin(mat, [M['GRASS_L'], M['GRASS_M'], M['FOREST'], M['SAND']])] = M['GRASS_SH']
    mat[sh & (mat == M['ROCK'])] = M['ROCK_SH']
    mat[sh & (mat == M['SNOW'])] = M['SNOW_SH']
    mineral = rock | snow
    return lev, mat, mineral


def build_mesh(lev, mat, mineral, cell):
    """Triangles (x, y, z float32 + matière uint32) : un dessus par case, une contremarche par arête descendante."""
    nx, ny = lev.shape
    dt = np.dtype([('p', np.float32, 3), ('m', np.uint32)])
    parts = []

    def quads(p0, p1, p2, p3, m):
        q = np.zeros((len(m), 6), dt)
        for k, p in enumerate((p0, p1, p2, p0, p2, p3)):
            q['p'][:, k, :] = p
        q['m'][:] = m[:, None]
        parts.append(q.reshape(-1))

    I, J = np.meshgrid(np.arange(nx), np.arange(ny), indexing='ij')
    i, j, z = I.ravel() * cell, J.ravel() * cell, lev.ravel() * STEP
    c = cell
    quads(np.stack([i, j, z], 1), np.stack([i + c, j, z], 1), np.stack([i + c, j + c, z], 1),
          np.stack([i, j + c, z], 1), mat.ravel())

    def risers(sel, hi, lo, a, b, tone):
        """a, b : extrémités de l'arête (tableaux [n,2]) ; hi/lo : niveaux ; tone : 0 clair, 1 moyen, 2 sombre."""
        if not sel.any():
            return
        zh, zl = hi[sel] * STEP, lo[sel] * STEP
        a, b = a[sel], b[sel]
        m = np.where(mineral_flat[sel], M['STONE_L'] + tone, M['EARTH_L'] + tone).astype(np.uint32)
        quads(np.column_stack([a, zl]), np.column_stack([b, zl]), np.column_stack([b, zh]), np.column_stack([a, zh]), m)

    # voisin à l'est (+x) : la paroi regarde l'est -> sombre ; à l'ouest -> claire ; au sud (−y, vers la caméra) -> moyenne
    for (di, dj, tone) in ((1, 0, 2), (-1, 0, 0), (0, 1, 2), (0, -1, 1)):
        si = slice(max(0, -di), nx - max(0, di))
        sj = slice(max(0, -dj), ny - max(0, dj))
        ti = slice(max(0, di), nx - max(0, -di))
        tj = slice(max(0, dj), ny - max(0, -dj))
        hi, lo = lev[si, sj], lev[ti, tj]
        sel = (hi > lo).ravel()
        ii, jj = I[si, sj].ravel() * cell, J[si, sj].ravel() * cell
        mineral_flat = mineral[si, sj].ravel()
        if di == 1:
            a, b = np.stack([ii + c, jj], 1), np.stack([ii + c, jj + c], 1)
        elif di == -1:
            a, b = np.stack([ii, jj], 1), np.stack([ii, jj + c], 1)
        elif dj == 1:
            a, b = np.stack([ii, jj + c], 1), np.stack([ii + c, jj + c], 1)
        else:
            a, b = np.stack([ii, jj], 1), np.stack([ii + c, jj], 1)
        risers(sel, hi.ravel(), lo.ravel(), a, b, tone)
    return np.concatenate(parts)


# ------------------------------------------------------------------ caméra (pur calcul de t)
VFOV = math.radians(58.0)
NEAR, FAR = 2.0, 420.0


def camera(t):
    y = 90.0 + 30.0 * t
    eye = np.array([river_x(y), y, 40.0 + 3.0 * math.sin(0.8 * t)])
    yaw = math.atan2(28.0 / 90.0 * math.cos(y / 90.0), 1.0)          # suit la rivière
    yaw_rate = -(28.0 / 90.0) * math.sin(y / 90.0) / 90.0 * 30.0
    roll = max(-0.22, min(0.22, -2.4 * yaw_rate))                      # s'incline dans le virage
    pitch = math.radians(-23.0 - 4.0 * math.sin(0.6 * t))
    f = np.array([math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)])
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    r, u = r * math.cos(roll) + u * math.sin(roll), u * math.cos(roll) - r * math.sin(roll)
    return eye, f, r, u


def view_proj(eye, f, r, u):
    V = np.eye(4)
    V[0, :3], V[1, :3], V[2, :3] = r, u, -f
    V[:3, 3] = -V[:3, :3] @ eye
    th = math.tan(VFOV / 2)
    P = np.zeros((4, 4))
    P[0, 0] = 1 / (th * NW / NH)
    P[1, 1] = 1 / th
    P[2, 2] = FAR / (NEAR - FAR)
    P[2, 3] = NEAR * FAR / (NEAR - FAR)
    P[3, 2] = -1
    return P @ V


def sky_bands(f, r, u, sky_idx):
    """Indice de palette du ciel par pixel natif : paliers selon l'élévation du rayon (suit le roulis)."""
    th = math.tan(VFOV / 2)
    x = ((np.arange(NW) + 0.5) / NW * 2 - 1) * th * NW / NH
    y = (1 - (np.arange(NH) + 0.5) / NH * 2) * th
    dz = f[2] + x[None, :] * r[2] + y[:, None] * u[2]
    n = np.sqrt(1 + x[None, :] ** 2 + y[:, None] ** 2)
    band = np.digitize(dz / n, [0.03, 0.10, 0.19, 0.30])
    return sky_idx[band]


# ------------------------------------------------------------------ carte graphique
GEOM_WGSL = """
struct U { vp: mat4x4f, cam: vec4f, fog: vec4f };
@group(0) @binding(0) var<uniform> u: U;
struct VO {
    @builtin(position) pos: vec4f,
    @location(0) world: vec3f,
    @location(1) @interpolate(flat) mat: u32,
};
@vertex
fn vs(@location(0) p: vec3f, @location(1) mat: u32) -> VO {
    var o: VO;
    o.pos = u.vp * vec4f(p, 1.0);
    o.world = p;
    o.mat = mat;
    return o;
}
fn hash01(c: vec2i) -> f32 {                      // entiers seulement : identique sur toutes les cartes
    var h = bitcast<u32>(c.x) * 374761393u + bitcast<u32>(c.y) * 668265263u;
    h = (h ^ (h >> 13u)) * 1274126177u;
    h = h ^ (h >> 16u);
    return f32(h & 0xffffu) / 65535.0;
}
const T = array<f32, 5>(1.0, 1.35, 1.75, 2.15, 2.6);
@fragment
fn fs(v: VO) -> @location(0) u32 {
    let d = distance(v.world, u.cam.xyz);
    // frontière des paliers crénelée, fixée dans le monde (cases de fog.z unités)
    let c = vec2i(floor((v.world.xy + vec2f(0.37, 0.37)) / u.fog.z));
    let dj = d + (hash01(c) - 0.5) * u.fog.y;
    var s = 0u;
    for (var i = 0; i < 5; i++) {
        if (dj > u.fog.x * T[i]) { s = u32(i) + 1u; }
    }
    return v.mat * 8u + s;
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
    for (var i = 0; i < N; i++) {
        s[i] = textureLoad(g, base + vec2i(i %% SS, i / SS), 0).r;
    }
    var best = 0u;
    var bestn = 0;
    for (var i = 0; i < N; i++) {
        var n = 0;
        for (var j = 0; j < N; j++) {
            if (s[j] == s[i]) { n++; }
        }
        if (n > bestn || (n == bestn && s[i] < best)) { best = s[i]; bestn = n; }
    }
    return best;
}
"""


class Engine:
    def __init__(self, gpu, ss, mesh):
        adapters = wgpu.gpu.enumerate_adapters_sync()
        want = {'radeon': 'Radeon', 'intel': 'Intel'}[gpu]
        match = [a for a in adapters if want.lower() in a.info['device'].lower()]
        if not match:
            sys.exit(f"carte « {gpu} » introuvable ; vues : {[a.info['device'] for a in adapters]}")
        self.adapter = match[0]
        self.info = dict(self.adapter.info)
        self.device = d = self.adapter.request_device_sync()
        self.ss = ss
        gw, gh = NW * ss, NH * ss
        U = wgpu.TextureUsage
        self.gtex = d.create_texture(size=(gw, gh, 1), format='r8uint', usage=U.RENDER_ATTACHMENT | U.TEXTURE_BINDING)
        self.depth = d.create_texture(size=(gw, gh, 1), format='depth32float', usage=U.RENDER_ATTACHMENT)
        self.out = d.create_texture(size=(NW, NH, 1), format='r8uint', usage=U.RENDER_ATTACHMENT | U.COPY_SRC)
        self.vbuf = d.create_buffer_with_data(data=mesh, usage=wgpu.BufferUsage.VERTEX)
        self.nverts = len(mesh)
        self.ubuf = d.create_buffer(size=96, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST)
        gmod = d.create_shader_module(code=GEOM_WGSL)
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
        self.gbind = d.create_bind_group(layout=self.gpipe.get_bind_group_layout(0),
                                         entries=[{'binding': 0, 'resource': {'buffer': self.ubuf}}])
        vmod = d.create_shader_module(code=VOTE_WGSL % {'ss': ss, 'n': ss * ss})
        self.vpipe = d.create_render_pipeline(
            layout='auto',
            vertex={'module': vmod, 'entry_point': 'vs'},
            primitive={'topology': 'triangle-list'},
            fragment={'module': vmod, 'entry_point': 'fs', 'targets': [{'format': 'r8uint'}]},
        )
        self.vbind = d.create_bind_group(layout=self.vpipe.get_bind_group_layout(0),
                                         entries=[{'binding': 0, 'resource': self.gtex.create_view()}])
        self.gview, self.dview, self.oview = self.gtex.create_view(), self.depth.create_view(), self.out.create_view()

    def frame(self, vp, eye, d_ref=115.0, amp=10.0, block=4.0):
        d = self.device
        u = np.zeros(24, np.float32)
        u[:16] = vp.T.astype(np.float32).ravel()          # WGSL : matrices par colonnes
        u[16:19] = eye
        u[20:23] = (d_ref, amp, block)
        d.queue.write_buffer(self.ubuf, 0, u.tobytes())
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


# ------------------------------------------------------------------ rendu
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gpu', default='radeon', choices=['radeon', 'intel'])
    ap.add_argument('--ss', type=int, default=4, choices=[1, 2, 4, 8])
    ap.add_argument('--seconds', type=float, default=6.0)
    ap.add_argument('--seed', type=int, default=2611)
    ap.add_argument('--cell', type=float, default=1.0)
    ap.add_argument('--out', default='sortie/proto.mp4')
    ap.add_argument('--no-video', action='store_true')
    ap.add_argument('--dump', help='écrit les images natives (indices de palette) en .npy')
    ap.add_argument('--stills', help='instants en secondes, PNG 1080×1920 à côté de --out')
    ap.add_argument('--json', help='écrit les mesures dans ce fichier')
    a = ap.parse_args()

    t0 = time.perf_counter()
    pal, lut, sky_idx = build_palette()
    lev, mat, mineral = build_world(a.seed, a.cell)
    mesh = build_mesh(lev, mat, mineral, a.cell)
    t_world = time.perf_counter() - t0
    # garde-fou : la caméra reste au-dessus du relief
    clear = min(camera(n / FPS)[0][2] - lev[int(camera(n / FPS)[0][0] / a.cell), int(camera(n / FPS)[0][1] / a.cell)] * STEP
                for n in range(int(a.seconds * FPS)))
    assert clear > 6.0, f'caméra trop basse : {clear:.1f}'

    t1 = time.perf_counter()
    eng = Engine(a.gpu, a.ss, mesh)
    eng.frame(view_proj(*camera(0.0)), camera(0.0)[0])       # compilation des shaders hors mesure
    t_init = time.perf_counter() - t1

    out = Path(a.out)
    ff = None
    if not a.no_video:
        out.parent.mkdir(parents=True, exist_ok=True)
        part = out.with_suffix('.part.mp4')
        ff = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{NW}x{NH}',
             '-framerate', str(FPS), '-i', '-', '-vf', f'scale={NW * SCALE}:{NH * SCALE}:flags=neighbor',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS),
             '-movflags', '+faststart', str(part)], stdin=subprocess.PIPE)
    still_frames = {int(round(float(s) * FPS)): s for s in a.stills.split(',')} if a.stills else {}
    n_frames = int(round(a.seconds * FPS))
    md5 = hashlib.md5()
    frames = np.zeros((n_frames, NH, NW), np.uint8) if a.dump else None
    t_gpu = t_cpu = t_pipe = 0.0
    ncolors = []
    t2 = time.perf_counter()
    for n in range(n_frames):
        t = n / FPS
        ta = time.perf_counter()
        eye, f, r, u = camera(t)
        code = eng.frame(view_proj(eye, f, r, u), eye)
        tb = time.perf_counter()
        idx = lut[code]
        skym = code == SKY_CODE
        idx[skym] = sky_bands(f, r, u, sky_idx)[skym]
        rgb = pal[idx]
        md5.update(idx.tobytes())
        ncolors.append(len(np.unique(idx)))
        if frames is not None:
            frames[n] = idx
        tc = time.perf_counter()
        if ff:
            ff.stdin.write(rgb.tobytes())
        if n in still_frames:
            out.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgb).resize((NW * SCALE, NH * SCALE), Image.NEAREST).save(
                out.parent / f'still_{float(still_frames[n]):.2f}s.png')
        td = time.perf_counter()
        t_gpu += tb - ta
        t_cpu += tc - tb
        t_pipe += td - tc
    if ff:
        ff.stdin.close()
        ff.wait()
        os.replace(part, out)
    total = time.perf_counter() - t2
    if a.dump:
        np.save(a.dump, frames)
    res = {
        'gpu': eng.info.get('device'), 'backend': eng.info.get('backend_type'), 'ss': a.ss, 'cell': a.cell,
        'seed': a.seed, 'frames': n_frames, 'triangles': len(mesh) // 3,
        'worldBuildSec': round(t_world, 2), 'gpuInitSec': round(t_init, 2),
        'renderSec': round(total, 2), 'secPer100Frames': round(total / n_frames * 100, 2),
        'msPerFrame': {'gpuRenderVoteReadback': round(t_gpu / n_frames * 1000, 2),
                       'cpuPaletteSky': round(t_cpu / n_frames * 1000, 2),
                       'pipeFfmpegStills': round(t_pipe / n_frames * 1000, 2)},
        'colorsPerFrame': [int(min(ncolors)), int(np.median(ncolors)), int(max(ncolors))],
        'paletteSize': int(len(pal)),
        'md5NativeIndexFrames': md5.hexdigest(),
        'md5Mp4': hashlib.md5(out.read_bytes()).hexdigest() if ff else None,
        'load1min': round(os.getloadavg()[0], 2),
    }
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
