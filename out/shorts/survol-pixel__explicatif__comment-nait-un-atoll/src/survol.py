#!/usr/bin/env python3
"""
survol.py — moteur de l'identité « Survol pixel ». Copie identique dans chaque short (convention de trait-continu).

Principe : un petit monde en pixel art 16 bits survolé par UNE caméra sténopé (cible, distance, cap, tangage, roulis)
pour tout le short. Rendu à 270×480 en indices de palette, agrandi ×4 au plus proche voisin (1080×1920).

- Sol et relief : lancer de rayon par pixel sur une carte de hauteurs EN TERRASSES (valeurs constantes par cellule),
  marche à pas fixes dans la boîte englobante du relief + 6 bissections. Hors de la boîte : intersection rayon–plan
  z = 0 en forme close (le « Mode 7 » généralisé, valable de 0° à 90° de tangage). Le même moteur sert tout le short :
  le piqué 70° → 15° ne change jamais de technique (C1).
- Contremarches (flancs) : un impact sur une paroi (rayon nettement sous le dessus de la cellule touchée) prend la
  couleur de flanc du matériau, claire si la paroi regarde la lumière (nord-ouest), sombre sinon (C2).
- Coupe : une région « coupée » de la carte (dessus = socle à z = −D) montre sur ses parois la coupe du terrain,
  colorée par une fonction de la scène (basalte / calcaire / eau, ou pierres / gravier / terre).
- Lointain : carte de couleurs réduite par vote majoritaire (mip 1/2, 1/4, 1/8, jamais de moyenne : on reste dans la
  palette) choisie selon l'empreinte du pixel au sol (C3). Brume quantifiée par bandes de distance (tables d'indices).
- Ciel en paliers plats selon l'élévation du rayon (s'incline avec le roulis).
- Nuages : piles de disques horizontaux dessinés au pixel près à la taille projetée (jamais agrandis), moitié basse
  hachurée une ligne sur deux, ombre plate au sol décalée selon l'altitude (une seule altitude de nuages).
- Objets : panneaux (« billboards ») dessinés en code, réduits au plus proche voisin, jamais agrandis au-delà de 1:1
  (C4), ombre = silhouette projetée au sol, décalage proportionnel à la hauteur.
- Texte : Jersey 10/15/20 (@fontsource 5.3.0) rendu par PIL sans anticrénelage (fontmode "1") à la résolution native,
  sur coordonnées entières, dans des cartouches crème à cadre encre et ombre plate ; largeur ≤ 214 px natifs vérifiée
  par assertion (C5–C9). Jamais de texte dans la carte projetée.

Chaque image est un pur calcul de t (aucun état caché) : rendu déterministe, graines dans short.json.
"""
import math, os, sys, json, time, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
NW, NH, SCALE, FPS = 270, 480, 4, 30
W, H = NW * SCALE, NH * SCALE
# zones sûres en pixels natifs (×4 = 220 / 320 / 120 / 64 px)
SAFE_T, SAFE_B, SAFE_R, SAFE_L = 55, 80, 30, 16
TEXT_MAXW = 214
CX_SAFE = (SAFE_L + NW - SAFE_R) // 2      # = 128, centre de la bande sûre

# ---------------------------------------------------------------- palette
CORE = {
    'OCEAN': '#1E5AA8', 'OCEAN_MID': '#2C74BE', 'SHALLOW': '#3FA0D0', 'LAGOON': '#7CCBEB', 'FOAM': '#E6FAFF',
    'SH_WATER': '#143F7E', 'GRASS_L': '#93D94E', 'GRASS_M': '#5DB534', 'GRASS_D': '#2F7A2A', 'FOREST': '#174A22',
    'CLOUD': '#FBFDFE', 'HATCH': '#AFBBC6', 'SKY_HI': '#6FB4E3', 'SKY_MID': '#96CBEB', 'SKY_LO': '#BFE2F1',
    'HAZE': '#EFE2BF', 'CREAM': '#FBF3D5', 'INK': '#14213D', 'WATER_FAR': '#5B9DCD', 'LAND_FAR': '#92B9A4',
    'RED': '#B5341A', 'GOLD': '#FFC94A', 'MUTED': '#5A5F73', 'CLOUD_RIM': '#CFE3F2',
}


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Palette:
    """Table de palette indexée : noyau fixe + couleurs « biome » de l'épisode."""

    def __init__(self, extra):
        self.names = list(CORE) + list(extra)
        self.hex = dict(CORE) | dict(extra)
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.rgb = np.array([hex2rgb(self.hex[n]) for n in self.names], np.uint8)
        n = len(self.names)
        self.shadow = np.arange(n, dtype=np.uint8)   # ombre portée : indice -> indice plus sombre
        self.haze1 = np.arange(n, dtype=np.uint8)    # brume 1 (lointain)
        self.haze2 = np.arange(n, dtype=np.uint8)    # brume 2 (bande d'horizon)
        self.speckle = np.arange(n, dtype=np.uint8)  # micro-détail : moucheture sous la cellule (identité = aucune)

    def __getitem__(self, k):
        return self.idx[k]

    def set_lut(self, lut, mapping):
        for a, b in mapping.items():
            getattr(self, lut)[self.idx[a]] = self.idx[b]


# ---------------------------------------------------------------- easing
def clamp01(u):
    return min(max(u, 0.0), 1.0)


def in_out_sine(u):
    u = clamp01(u)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def ease(name, u):
    u = clamp01(u)
    if name == 'linear':
        return u
    if name == 'inOutSine':
        return in_out_sine(u)
    if name == 'inOutCubic':
        return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    if name == 'outCubic':
        return 1 - (1 - u) ** 3
    if name == 'inCubic':
        return u ** 3
    raise ValueError(name)


# ---------------------------------------------------------------- caméra
CAM_KEYS = ('tx', 'ty', 'tz', 'dist', 'yaw', 'pitch', 'roll')


class CameraPath:
    """Une seule caméra pour tout le short : clés (t, {tx,ty,tz,dist,yaw,pitch,roll}, easing du segment qui y mène).
    Position = cible − avant × distance. yaw en degrés (0 = regarde vers +y, le nord), pitch en degrés sous l'horizon
    (90 = verticale), roll en degrés."""

    def __init__(self, keys):
        self.keys = keys

    def at(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return dict(ks[0][1])
        for (t0, a, _), (t1, b, e) in zip(ks, ks[1:]):
            if t <= t1:
                u = ease(e, (t - t0) / max(t1 - t0, 1e-9))
                return {k: a[k] + (b[k] - a[k]) * u for k in CAM_KEYS}
        return dict(ks[-1][1])


class Cam:
    def __init__(self, p, focal):
        yaw, pitch, roll = (math.radians(p[k]) for k in ('yaw', 'pitch', 'roll'))
        f = np.array([math.cos(pitch) * math.sin(yaw), math.cos(pitch) * math.cos(yaw), -math.sin(pitch)])
        r = np.array([math.cos(yaw), -math.sin(yaw), 0.0])
        u = np.cross(r, f)
        cr, sr = math.cos(roll), math.sin(roll)
        r, u = r * cr + u * sr, -r * sr + u * cr
        self.f, self.r, self.u = f, r, u
        self.pos = np.array([p['tx'], p['ty'], p['tz']]) - f * p['dist']
        self.F = focal
        self.cx, self.cy = NW / 2, NH / 2
        self.pitch = p['pitch']

    def project(self, P):
        """point(s) monde -> (sx, sy, profondeur). P : (..., 3)."""
        v = np.asarray(P, float) - self.pos
        zc = v @ self.f
        xc = v @ self.r
        yc = v @ self.u
        zc_safe = np.where(zc > 1e-6, zc, 1e-6)
        return self.cx + self.F * xc / zc_safe, self.cy - self.F * yc / zc_safe, zc

    def rays(self):
        i = (np.arange(NW, dtype=np.float32) + 0.5 - self.cx) / self.F
        j = (np.arange(NH, dtype=np.float32) + 0.5 - self.cy) / self.F
        I, J = np.meshgrid(i, j)
        d = (self.f[None, None, :] + I[..., None] * self.r[None, None, :] - J[..., None] * self.u[None, None, :])
        return d.astype(np.float32)   # (NH, NW, 3), composante le long de f = 1 -> t = profondeur


# ---------------------------------------------------------------- monde
def mode_down(c):
    """Réduction ×2 par vote majoritaire (indices, pas de moyenne). Égalité -> coin haut gauche."""
    G = c.shape[0] // 2 * 2
    a, b, cc, d = c[0:G:2, 0:G:2], c[0:G:2, 1:G:2], c[1:G:2, 0:G:2], c[1:G:2, 1:G:2]
    na = (a == b).astype(np.int8) + (a == cc) + (a == d)
    nb = (b == a).astype(np.int8) + (b == cc) + (b == d)
    nc = (cc == a).astype(np.int8) + (cc == b) + (cc == d)
    nd = (d == a).astype(np.int8) + (d == b) + (d == cc)
    out = a.copy()
    best = na.copy()
    for v, n in ((b, nb), (cc, nc), (d, nd)):
        m = n > best
        out[m] = v[m]
        best[m] = n[m]
    return out


class World:
    """Carte de hauteurs en terrasses (dessus constant par cellule, 1 cellule = 1 unité monde) et carte de couleurs.
    top : hauteur du dessus (eau = 0, socle de coupe = -depth) ; col : indice de couleur du dessus ;
    flank_lit / flank_dark : indice de flanc par cellule ; cut : masque de coupe ; section(x, y, z, cut_side) -> indices."""

    def __init__(self, top, col, flank_lit, flank_dark, cut=None, section=None, outside=0, zmin=-1.0, levels=3,
                 outside_tile=None, cut_top0=None, coursed=None):
        self.G = top.shape[0]
        self.coursed = coursed        # masque des parois appareillées (assises + joints décalés), None = aucune
        self.top = top.astype(np.float32)
        self.col = [col.astype(np.uint8)]
        for _ in range(levels):
            self.col.append(mode_down(self.col[-1]))
        self.flank_lit = flank_lit.astype(np.uint8)
        self.flank_dark = flank_dark.astype(np.uint8)
        self.cut = cut if cut is not None else np.zeros_like(top, bool)
        self.section = section
        self.cut_top0 = cut_top0      # dessus d'origine de la région coupée : la coupe n'est vue que du dedans
        # flancs raides vus par la tranche : biais de niveau de mip selon la pente locale (anti-moiré, C3 étendu)
        tp = np.maximum(self.top, 0)
        grad = np.zeros_like(tp)
        for sh in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            grad = np.maximum(grad, np.abs(np.roll(tp, sh, (0, 1)) - tp))
        self.steep = np.clip(1.6 * np.log2(1.0 + grad), 0, 3).astype(np.float32)
        self.outside = outside
        self.tile = None
        if outside_tile is not None:
            self.tile = [outside_tile.astype(np.uint8)]
            for _ in range(levels):
                self.tile.append(mode_down(self.tile[-1]))
        nz = (np.abs(self.top) > 1e-4)
        if cut is not None and cut.any():
            from scipy.ndimage import binary_dilation
            nz |= binary_dilation(cut, iterations=4)
        ys, xs = np.nonzero(nz)
        if len(xs):
            self.bbox = (float(xs.min()) - 1, float(xs.max()) + 2, float(ys.min()) - 1, float(ys.max()) + 2,
                         min(float(self.top.min()), zmin) - 0.01, float(self.top.max()) + 0.01)
        else:
            self.bbox = None


# ---------------------------------------------------------------- rendu du sol
def hash01(ix, iy, k=0):
    """Bruit blanc fixe dans le monde : entiers -> [0, 1) (hachage entier, déterministe, sans état)."""
    h = (np.asarray(ix, np.int64) * 73856093) ^ (np.asarray(iy, np.int64) * 19349663) ^ (np.asarray(k, np.int64) * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return ((h & 0xFFFF).astype(np.float32)) / 65536.0


def ragged(shape, seed, amp=1.0):
    """Décalage fixe par cellule dans [-amp/2, amp/2) : rend crénelés les seuils d'un champ continu (bandes de
    hauts-fonds, plages, lisières) avec quelques cellules isolées, comme la source."""
    return ((np.random.default_rng(seed).random(shape) - 0.5) * amp).astype(np.float32)


class Renderer:
    def __init__(self, pal, focal=416.0, sun=(0.30, -0.62), sky=None, haze_d=(None, None), steps=96, mip_bias=0.0,
                 micro=0.12, jitter=0.42, course=0.0):
        self.pal = pal
        self.micro = micro            # probabilité de moucheture par sous-cellule (texels agrandis seulement)
        self.jitter = jitter          # amplitude (en cellules) du décalage de lecture : bords crénelés sous la cellule
        self.course = course          # hauteur d'assise des parois appareillées (unités monde), 0 = pas d'appareil
        self.focal = focal
        self.sun = np.array(sun, np.float32)                  # décalage d'ombre au sol par unité d'altitude
        Ll = np.array([-sun[0], -sun[1]], np.float32)         # direction horizontale vers la lumière
        self.light_h = Ll / np.linalg.norm(Ll)
        self.sky = sky or [(0.8, 'HAZE'), (4.5, 'SKY_LO'), (11.0, 'SKY_MID'), (90.0, 'SKY_HI')]
        self.haze_d = haze_d
        self.steps = steps
        self.mip_bias = mip_bias

    # -- lancer de rayon dans la boîte du relief
    def _march(self, w, o, d, tin, tout):
        top, G = w.top, w.G
        n = len(tin)
        hit_t = np.full(n, np.inf, np.float32)
        lo_t = np.zeros(n, np.float32)
        steps = self.steps
        step = (tout - tin) / steps
        active = np.arange(n)
        chunk = 12
        k0 = 0
        prev_t = tin.copy()
        while k0 <= steps and len(active):
            ks = np.arange(k0, min(k0 + chunk, steps + 1), dtype=np.float32)
            T = tin[active, None] + step[active, None] * ks[None, :]
            px = o[0] + T * d[active, 0, None]
            py = o[1] + T * d[active, 1, None]
            pz = o[2] + T * d[active, 2, None]
            xi = np.clip(px.astype(np.int32), 0, G - 1)
            yi = np.clip(py.astype(np.int32), 0, G - 1)
            inside = pz < top[yi, xi]
            anyin = inside.any(1)
            first = inside.argmax(1)
            sel = np.nonzero(anyin)[0]
            if len(sel):
                ids = active[sel]
                fk = first[sel]
                hit_t[ids] = T[sel, fk]
                prevT = np.where(fk > 0, T[sel, np.maximum(fk - 1, 0)], prev_t[ids])
                lo_t[ids] = np.where((fk == 0) & (k0 == 0), tin[ids], prevT)
            keep = ~anyin
            prev_t[active[keep]] = T[keep, -1]
            active = active[keep]
            k0 += chunk
        found = np.isfinite(hit_t)
        ids = np.nonzero(found)[0]
        lo, hi = lo_t[ids], hit_t[ids]
        dd = d[ids]
        for _ in range(6):
            mid = (lo + hi) * 0.5
            px = o[0] + mid * dd[:, 0]
            py = o[1] + mid * dd[:, 1]
            pz = o[2] + mid * dd[:, 2]
            xi = np.clip(px.astype(np.int32), 0, G - 1)
            yi = np.clip(py.astype(np.int32), 0, G - 1)
            ins = pz < top[yi, xi]
            hi = np.where(ins, mid, hi)
            lo = np.where(ins, lo, mid)
        hit_t[ids] = hi
        lo_t[ids] = lo
        return hit_t, lo_t

    def ground(self, w, cam, t_anim, shadow_disks=(), foam_phase=0):
        pal = self.pal
        cxi, cyi = int(cam.pos[0]), int(cam.pos[1])
        if 0 <= cxi < w.G and 0 <= cyi < w.G:
            assert cam.pos[2] > w.top[cyi, cxi] + 1.0, f'caméra sous le relief ({cam.pos.round(1)})'
        d = cam.rays().reshape(-1, 3)
        o = cam.pos.astype(np.float32)
        n = d.shape[0]
        idx = np.zeros(n, np.uint8)
        depth = np.full(n, np.inf, np.float32)
        dz = d[:, 2]
        # plan z = 0 (forme close)
        with np.errstate(divide='ignore', invalid='ignore'):
            tp = np.where(dz < -1e-6, (0.0 - o[2]) / dz, np.inf).astype(np.float32)
        t_hit = tp.copy()
        kind = np.zeros(n, np.int8)                # 0 = dessus, 1 = paroi
        lo_hit = np.zeros(n, np.float32)
        # boîte du relief
        if w.bbox is not None:
            x0, x1, y0, y1, z0, z1 = w.bbox
            with np.errstate(divide='ignore', invalid='ignore'):
                tmin = np.full(n, -np.inf, np.float32)
                tmax = np.full(n, np.inf, np.float32)
                for a, (b0, b1) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
                    da = d[:, a]
                    ta = (b0 - o[a]) / da
                    tb = (b1 - o[a]) / da
                    lo_ = np.minimum(ta, tb)
                    hi_ = np.maximum(ta, tb)
                    par = np.abs(da) < 1e-9
                    inside_slab = (o[a] >= b0) & (o[a] <= b1)
                    lo_ = np.where(par, np.where(inside_slab, -np.inf, np.inf), lo_)
                    hi_ = np.where(par, np.where(inside_slab, np.inf, -np.inf), hi_)
                    tmin = np.maximum(tmin, lo_)
                    tmax = np.minimum(tmax, hi_)
            tmin = np.maximum(tmin, 0.01)
            act = np.nonzero((tmax > tmin) & (tmin < tp))[0]   # l'eau hors boîte, touchée avant, reste prioritaire
            if len(act):
                ht, lt = self._march(w, o, d[act], tmin[act].astype(np.float32), tmax[act].astype(np.float32))
                ok = np.isfinite(ht)
                a2 = act[ok]
                t_hit[a2] = ht[ok]
                lo_hit[a2] = lt[ok]
                # rayons qui traversent la boîte sans toucher : ils ne doivent pas reprendre le plan z=0 dans la boîte
                miss = act[~ok]
                if len(miss):
                    px = o[0] + tp[miss] * d[miss, 0]
                    py = o[1] + tp[miss] * d[miss, 1]
                    inb = (px >= x0) & (px <= x1) & (py >= y0) & (py <= y1)
                    t_hit[miss[inb]] = np.inf
        hitm = np.isfinite(t_hit)
        hi_ids = np.nonzero(hitm)[0]
        th = t_hit[hi_ids]
        dd = d[hi_ids]
        hx = o[0] + th * dd[:, 0]
        hy = o[1] + th * dd[:, 1]
        hz = o[2] + th * dd[:, 2]
        G = w.G
        ingrid = (hx >= 0) & (hx < G) & (hy >= 0) & (hy < G)
        xi = np.clip(hx.astype(np.int32), 0, G - 1)
        yi = np.clip(hy.astype(np.int32), 0, G - 1)
        topv = w.top[yi, xi]
        is_wall = ingrid & (topv - hz > 0.12)
        # empreinte du pixel au sol -> niveau de mip (vote majoritaire)
        dn = np.linalg.norm(dd, axis=1)
        inc = np.abs(dd[:, 2]) / dn
        fp = th * dn / cam.F * np.sqrt(1.0 / np.maximum(inc, 0.08))
        lg = np.log2(np.maximum(fp, 1e-6))
        # le biais de pente ne joue qu'au loin (pixel ≥ 1/2 cellule) : la vue rapprochée reste nette
        bias = np.where(lg > -1.5, w.steep[yi, xi], 0.0)
        lvl = np.clip(np.floor(lg + self.mip_bias + bias), 0, len(w.col) - 1).astype(np.int32)
        cidx = np.full(len(hi_ids), w.outside, np.uint8)
        for L in range(len(w.col)):
            m = (lvl == L) & ingrid
            if m.any():
                c = w.col[L]
                cidx[m] = c[np.clip(yi[m] >> L, 0, c.shape[0] - 1), np.clip(xi[m] >> L, 0, c.shape[1] - 1)]
        if w.tile is not None:
            for L in range(len(w.tile)):
                m = (lvl == L) & ~ingrid
                if m.any():
                    c = w.tile[L]
                    cidx[m] = c[np.floor(hy[m] / (1 << L)).astype(np.int64) % c.shape[0],
                                np.floor(hx[m] / (1 << L)).astype(np.int64) % c.shape[1]]
        # micro-détail sous la cellule (texels agrandis, niveau 0 seulement) : la lecture de la carte est décalée par
        # un bruit fixe dans le monde, sur une sous-grille de 2^m cases par cellule choisie pour qu'une sous-case fasse
        # ≈ 1–2 pixels natifs ; les frontières de couleur deviennent des escaliers irréguliers au lieu de grands carrés,
        # et une moucheture (table pal.speckle) sème des touffes. Indices de palette seulement : rien n'est moyenné.
        if self.micro > 0 or self.jitter > 0:
            mm = (lvl == 0) & ingrid & ~is_wall
            if mm.any():
                mi = np.nonzero(mm)[0]
                m = np.clip(np.floor(-np.log2(np.maximum(fp[mi], 1e-3))), 0, 3).astype(np.int64)
                n_sub = (1 << m).astype(np.float32)
                sx_ = np.floor(hx[mi] * n_sub).astype(np.int64)
                sy_ = np.floor(hy[mi] * n_sub).astype(np.int64)
                h1 = hash01(sx_, sy_, m)
                h2 = hash01(sx_ + 7919, sy_ - 104729, m)
                if self.jitter > 0:
                    sub = m >= 1
                    jx = np.where(sub, (h1 - 0.5) * 2 * self.jitter, 0.0)
                    jy = np.where(sub, (h2 - 0.5) * 2 * self.jitter, 0.0)
                    xj = np.clip((hx[mi] + jx).astype(np.int32), 0, G - 1)
                    yj = np.clip((hy[mi] + jy).astype(np.int32), 0, G - 1)
                    same = np.abs(w.top[yj, xj] - topv[mi]) < 0.05      # même dessus : on ne lit pas une autre marche
                    if w.cut is not None:
                        same &= w.cut[yj, xj] == w.cut[yi[mi], xi[mi]]
                    cidx[mi] = np.where(same, w.col[0][yj, xj], cidx[mi])
                if self.micro > 0:
                    h3 = hash01(sx_ - 31337, sy_ + 4242, m)
                    # seulement quand une cellule couvre ≥ 2 pixels : à 1 pixel par cellule, la moucheture crénèle
                    # (mesuré : +0,9 point de pixels qui changent par image sur les flancs de Machu Picchu)
                    cidx[mi] = np.where((h3 < self.micro) & (m >= 1), pal.speckle[cidx[mi]], cidx[mi])
        # parois
        if is_wall.any():
            wi = np.nonzero(is_wall)[0]
            lo = lo_hit[hi_ids[wi]]
            pxp = o[0] + lo * dd[wi, 0]
            pyp = o[1] + lo * dd[wi, 1]
            xp = np.clip(pxp.astype(np.int32), 0, G - 1)
            yp = np.clip(pyp.astype(np.int32), 0, G - 1)
            nx = (xp - xi[wi]).astype(np.float32)
            ny = (yp - yi[wi]).astype(np.float32)
            lit = (nx * self.light_h[0] + ny * self.light_h[1]) > 0
            wc = np.where(lit, w.flank_lit[yi[wi], xi[wi]], w.flank_dark[yi[wi], xi[wi]])
            # au loin (mip ≥ 1), la contremarche prend la couleur réduite du dessus : plus d'alternance dessus/flanc
            far = lvl[wi] >= 1
            if self.course > 0 and w.coursed is not None:
                # appareil de pierre : une assise sombre toutes les `course` unités, joints verticaux décalés d'une
                # demi-pierre d'une assise à l'autre ; seulement si l'assise fait ≥ 3 pixels natifs (pas de moiré)
                cw = w.coursed[yi[wi], xi[wi]] & (fp[wi] * 3.0 < self.course)
                if cw.any():
                    hzw = hz[wi]
                    alg = np.where(np.abs(nx) > 0, hy[wi], hx[wi])
                    row = np.floor(hzw / self.course)
                    bed = (hzw / self.course - row) < np.maximum(0.2, fp[wi] / self.course)
                    joint = ((alg / (1.8 * self.course) + 0.5 * (row % 2)) % 1.0) < np.maximum(0.1, fp[wi] / (1.8 * self.course))
                    wc = np.where(cw & (bed | joint), pal.shadow[wc], wc)
            wc = np.where(far, cidx[wi], wc)
            if w.section is not None:
                from_cut = w.cut[yp, xp] & ~w.cut[yi[wi], xi[wi]]
                if w.cut_top0 is not None:
                    pzp = o[2] + lo * dd[wi, 2]
                    from_cut &= pzp < w.cut_top0[yp, xp] - 0.05
                if from_cut.any():
                    s = np.nonzero(from_cut)[0]
                    along = np.where(np.abs(nx[s]) > 0, hy[wi][s], hx[wi][s])
                    wc[s] = w.section(hx[wi][s], hy[wi][s], hz[wi][s], xi[wi][s], yi[wi][s], along, t_anim)
            cidx[wi] = wc
        # ombres (nuages et objets) : disques au sol
        sh = np.zeros(len(hi_ids), bool)
        for (sx, sy, R) in shadow_disks:
            sh |= (hx - sx) ** 2 + (hy - sy) ** 2 < R * R
        cidx = np.where(sh & ~is_wall, pal.shadow[cidx], cidx)
        # brume quantifiée par bandes de distance horizontale
        hd = th * np.sqrt(dd[:, 0] ** 2 + dd[:, 1] ** 2)
        h1, h2 = self.haze_d
        if h1 is not None:
            cidx = np.where(hd > h1, pal.haze1[cidx], cidx)
        if h2 is not None:
            cidx = np.where(hd > h2, pal.haze2[cidx], cidx)
        idx[hi_ids] = cidx
        depth[hi_ids] = th
        # ciel en paliers selon l'élévation du rayon
        sky_ids = np.nonzero(~hitm)[0]
        if len(sky_ids):
            ds = d[sky_ids]
            el = np.degrees(np.arcsin(np.clip(ds[:, 2] / np.linalg.norm(ds, axis=1), -1, 1)))
            sc = np.full(len(sky_ids), pal[self.sky[-1][1]], np.uint8)
            for lim, name in reversed(self.sky):
                sc[el < lim] = pal[name]
            idx[sky_ids] = sc
        hitinfo = {'ids': hi_ids, 'x': hx, 'y': hy, 'z': hz}
        return idx.reshape(NH, NW), depth.reshape(NH, NW), hitinfo


# ---------------------------------------------------------------- nuages
class Cloud:
    """Nuage = tas de boules (« coton ») : une couronne de 3–5 boules à l'altitude z, 1–3 boules empilées au-dessus,
    parfois une boule sommitale. disks : (dx, dy, dz, rayon) en unités monde. lobes règle la taille du tas."""

    def __init__(self, x, y, z, R, lobes=3, seed=0):
        rng = np.random.default_rng(seed)
        self.x, self.y, self.z, self.R = x, y, z, R
        self.disks = []
        nb = int(rng.integers(3, 6)) + max(0, lobes - 3)
        a0 = rng.uniform(0, 2 * math.pi)
        for k in range(nb):
            a = a0 + 2 * math.pi * k / nb + rng.uniform(-0.3, 0.3)
            d = R * rng.uniform(0.35, 0.65)
            self.disks.append((math.cos(a) * d, math.sin(a) * d, 0.0, R * rng.uniform(0.42, 0.62)))
        for k in range(int(rng.integers(1, 3)) + (1 if lobes >= 3 else 0)):
            a = rng.uniform(0, 2 * math.pi)
            d = R * rng.uniform(0.0, 0.3)
            self.disks.append((math.cos(a) * d, math.sin(a) * d, R * rng.uniform(0.38, 0.55), R * rng.uniform(0.45, 0.6)))
        if lobes >= 3 and rng.random() < 0.6:
            self.disks.append((rng.uniform(-0.15, 0.15) * R, rng.uniform(-0.15, 0.15) * R, R * 0.8, R * 0.38))

    def at(self, t, drift=(0.0, 0.0)):
        return self.x + drift[0] * t, self.y + drift[1] * t


def draw_clouds(idx, depth, cam, pal, clouds, t, drift=(0.0, 0.0)):
    """Chaque boule = disque écran au rayon projeté (dessiné au pixel près, jamais agrandi), légèrement aplati en
    rasante ; haut blanc, moitié basse hachurée une ligne sur deux, liseré bleuté au bas, reflet sommital.
    Ordre du peintre (loin -> près, bas -> haut) et test de profondeur contre le sol."""
    CL, HA, RIM = pal['CLOUD'], pal['HATCH'], pal['CLOUD_RIM']
    flat = 0.62 + 0.38 * math.sin(math.radians(max(cam.pitch, 0.0)))
    items = []
    for c in clouds:
        cx, cy = c.at(t, drift)
        for (dx, dy, dz, r) in c.disks:
            P = np.array([cx + dx, cy + dy, c.z + dz])
            sx, sy, zc = cam.project(P)
            if zc < 1:
                continue
            items.append((float(zc), float(sx), float(sy), r, dz))
    items.sort(key=lambda it: (-round(it[0] / 4), it[4]))
    for zc, sx, sy, r, dz in items:
        rp = cam.F * r / zc
        if rp < 0.6:
            continue
        ax, ay = max(rp, 0.6), max(rp * flat, 0.6)
        x0, x1 = int(math.floor(sx - ax)), int(math.ceil(sx + ax))
        y0, y1 = int(math.floor(sy - ay)), int(math.ceil(sy + ay))
        if x1 < 0 or y1 < 0 or x0 >= NW or y0 >= NH:
            continue
        x0c, x1c, y0c, y1c = max(x0, 0), min(x1, NW - 1), max(y0, 0), min(y1, NH - 1)
        if x1c < x0c or y1c < y0c:
            continue
        jj, ii = np.mgrid[y0c:y1c + 1, x0c:x1c + 1]
        u = (ii + 0.5 - sx) / ax
        v = (jj + 0.5 - sy) / ay
        m = u * u + v * v <= 1.0
        dsub = depth[y0c:y1c + 1, x0c:x1c + 1]
        m &= dsub > zc
        if not m.any():
            continue
        sub = idx[y0c:y1c + 1, x0c:x1c + 1]
        col = np.full(m.shape, CL, np.uint8)
        lower = (v > 0.12 - 0.25 * u) & (ay >= 2)
        col[lower & (jj % 2 == 0)] = HA
        rim = m & ~np.roll(m, -1, axis=0)
        rim[-1, :] = m[-1, :]
        col[rim & (v > 0.3)] = RIM
        sub[m] = col[m]
        dsub[m] = zc


def cloud_shadow_disks(clouds, sun, t, drift=(0.0, 0.0), ground_z=0.0):
    """Ombre plate au sol : les boules de la couronne, décalées selon l'altitude (une seule altitude de nuages)."""
    out = []
    for c in clouds:
        cx, cy = c.at(t, drift)
        h = c.z - ground_z
        for (dx, dy, dz, r) in c.disks:
            if dz > 0.01:
                continue
            out.append((cx + dx + sun[0] * h, cy + dy + sun[1] * h, r * 1.05))
    return out


# ---------------------------------------------------------------- arbres en grappes
def scatter_trees(mask, ground, seed, density=0.5, r=(0.9, 1.6), cluster=None, jitter=0.45):
    """Arbres semés sur les cellules de `mask` (proba `density` par cellule, modulée par `cluster` dans [0, 1]) :
    renvoie (N, 4) = x, y, z du pied, rayon (unités monde). Fixe, calculé une fois."""
    rng = np.random.default_rng(seed)
    p = np.full(mask.shape, density, np.float32)
    if cluster is not None:
        p = p * np.clip(cluster, 0, 1)
    keep = mask & (rng.random(mask.shape) < p)
    ys, xs = np.nonzero(keep)
    n = len(xs)
    x = xs + 0.5 + rng.uniform(-jitter, jitter, n)
    y = ys + 0.5 + rng.uniform(-jitter, jitter, n)
    z = ground[ys, xs]
    rr = rng.uniform(r[0], r[1], n)
    return np.stack([x, y, z, rr], 1).astype(np.float32)


_STAMPS = {}


def tree_stamp(rp):
    """Boule d'arbre de rayon rp pixels : 0 = vide, 1 = ombre propre, 2 = feuillage, 3 = reflet, 4 = éclat."""
    if rp in _STAMPS:
        return _STAMPS[rp]
    n = 2 * rp + 1
    j, i = np.mgrid[0:n, 0:n] - rp
    u, v = i / max(rp, 1), j / max(rp, 1)
    rad = u * u + v * v
    st = np.zeros((n, n), np.uint8)
    inside = (i * i + j * j) <= rp * rp + rp * 0.8
    st[inside] = 2
    st[inside & (u + v > 0.75)] = 1
    st[inside & ((u + 0.4) ** 2 + (v + 0.45) ** 2 < 0.28)] = 3
    if rp >= 3:
        st[inside & ((u + 0.45) ** 2 + (v + 0.5) ** 2 < 0.05)] = 4
    if rp == 1:
        st[:] = 0
        st[1, 1] = 2
        st[0, 1] = st[1, 0] = 3
        st[1, 2] = st[2, 1] = 1
    _STAMPS[rp] = st
    return st


def draw_trees(idx, depth, cam, pal, trees, sun, colors=('FOREST', 'GRASS_D', 'GRASS_M', 'GRASS_L'), lift=1.0,
               max_r=7, shadows=True):
    """Boules de feuillage au rayon projeté (pixel près, plafonnées à max_r : jamais d'agrandissement d'un dessin),
    ombre portée plate au sol décalée selon la hauteur (table d'ombre), reflet haut-gauche, ombre propre bas-droite.
    colors : (ombre propre, feuillage, reflet, éclat)."""
    if trees is None or not len(trees):
        return
    sh_c, base_c, hi_c, sp_c = (pal[c] for c in colors)
    C = np.stack([trees[:, 0], trees[:, 1], trees[:, 2] + trees[:, 3] * lift], 1)
    sx, sy, zc = cam.project(C)
    rp = cam.F * trees[:, 3] / np.maximum(zc, 1e-3)
    # seuil 1,25 px : en dessous, la carte de couleurs (forêt sombre) suffit ; les boules de 1 px qui apparaissent et
    # disparaissent d'une image à l'autre faisaient grésiller les rasantes (allers-retours A-B-A mesurés ×3).
    vis = (zc > 1) & (rp >= 1.25) & (sx > -10) & (sx < NW + 10) & (sy > -10) & (sy < NH + 10)
    if not vis.any():
        return
    ids = np.nonzero(vis)[0]
    # pas de test sur le seul pixel du pied (il bascule sur les arêtes des marches) : l'occultation se fait pixel par
    # pixel ci-dessous, avec une profondeur constante par arbre.
    order = ids[np.argsort(-zc[ids])]
    # ombres d'abord (sur le sol seulement)
    hgt = trees[order, 3] * (1.0 + lift)
    G_ = np.stack([trees[order, 0] + sun[0] * hgt, trees[order, 1] + sun[1] * hgt, trees[order, 2]], 1)
    gx, gy, gz = cam.project(G_)
    flat = max(0.35, math.sin(math.radians(max(cam.pitch, 0.0))))
    for k, ti in enumerate(order if shadows else ()):
        r_ = int(min(max_r, round(rp[ti])))
        if r_ < 1 or gz[k] < 1:
            continue
        x0, y0 = int(round(gx[k])) - r_, int(round(gy[k] - r_ * flat))
        hh = max(1, int(round((2 * r_ + 1) * flat)))
        m = tree_stamp(r_)[np.minimum((np.arange(hh) / flat).astype(int), 2 * r_)] > 0
        h, w_ = m.shape
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w_, NW), min(y0 + h, NH)
        if xb <= xa or yb <= ya:
            continue
        mm = m[ya - y0:yb - y0, xa - x0:xb - x0] & (np.abs(depth[ya:yb, xa:xb] - gz[k]) < 6.0 + 0.05 * gz[k])
        sub = idx[ya:yb, xa:xb]
        sub[mm] = pal.shadow[sub[mm]]
    lut = np.array([0, sh_c, base_c, hi_c, sp_c], np.uint8)
    for ti in order:
        r_ = int(min(max_r, round(rp[ti])))
        if r_ < 1:
            continue
        st = tree_stamp(r_)
        x0, y0 = int(round(sx[ti])) - r_, int(round(sy[ti])) - r_
        h, w_ = st.shape
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w_, NW), min(y0 + h, NH)
        if xb <= xa or yb <= ya:
            continue
        s_ = st[ya - y0:yb - y0, xa - x0:xb - x0]
        dsub = depth[ya:yb, xa:xb]
        mm = (s_ > 0) & (dsub > zc[ti] - 2.5 * trees[ti, 3])
        idx[ya:yb, xa:xb][mm] = lut[s_[mm]]
        dsub[mm] = np.minimum(dsub[mm], zc[ti])


# ---------------------------------------------------------------- panneaux (objets dessinés en code)
def sprite_from_ascii(rows, legend, pal):
    """rows : liste de chaînes ; legend : {char: nom de couleur} ; '.' = transparent. -> (indices, masque)."""
    h, w = len(rows), max(len(r) for r in rows)
    ind = np.zeros((h, w), np.uint8)
    m = np.zeros((h, w), bool)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in legend:
                ind[y, x] = pal[legend[ch]]
                m[y, x] = True
    return ind, m


def scale_nearest(ind, m, s):
    """Réduction au plus proche voisin (s ≤ 1) : C4, jamais d'agrandissement."""
    assert s <= 1.0 + 1e-6, f'billboard agrandi ×{s:.2f} (interdit, C4)'
    h, w = m.shape
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    ys = np.minimum((np.arange(nh) / s).astype(int), h - 1)
    xs = np.minimum((np.arange(nw) / s).astype(int), w - 1)
    return ind[np.ix_(ys, xs)], m[np.ix_(ys, xs)]


def blit(idx, depth, ind, m, x, y, z=None):
    """Colle un panneau (coin haut gauche x, y entiers), avec test de profondeur si z est donné."""
    h, w = m.shape
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, NW), min(y + h, NH)
    if x1 <= x0 or y1 <= y0:
        return
    mm = m[y0 - y:y1 - y, x0 - x:x1 - x].copy()
    if z is not None:
        mm &= depth[y0:y1, x0:x1] > z
        depth[y0:y1, x0:x1][mm] = z
    idx[y0:y1, x0:x1][mm] = ind[y0 - y:y1 - y, x0 - x:x1 - x][mm]


def shade(idx, lut, m, x, y):
    h, w = m.shape
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, NW), min(y + h, NH)
    if x1 <= x0 or y1 <= y0:
        return
    mm = m[y0 - y:y1 - y, x0 - x:x1 - x]
    sub = idx[y0:y1, x0:x1]
    sub[mm] = lut[sub[mm]]


class Billboard:
    """Objet debout ou volant : pied au point monde (x, y, z) ; taille 1:1 à la distance d1 (profondeur caméra)."""

    def __init__(self, frames, d1, shadow_h=None):
        self.frames = frames          # liste de (indices, masque)
        self.d1 = d1
        self.shadow_h = shadow_h      # hauteur au-dessus du sol (None = posé au sol)

    def draw(self, idx, depth, cam, pal, x, y, z, ground_z, frame=0, sun=(0.3, -0.62), max_scale_log=None):
        ind, m = self.frames[frame % len(self.frames)]
        sx, sy, zc = cam.project(np.array([x, y, z]))
        if zc < 1:
            return None
        s = min(self.d1 / zc, 1.0)
        if max_scale_log is not None:
            max_scale_log.append(self.d1 / zc)
        si, sm = scale_nearest(ind, m, s)
        h, w = sm.shape
        # ombre : silhouette au sol, décalée selon la hauteur (vol) ou cisaillée (posé)
        hgt = (z - ground_z)
        gx, gy = x + sun[0] * hgt, y + sun[1] * hgt
        gsx, gsy, gz = cam.project(np.array([gx, gy, ground_z]))
        if gz > 1:
            if hgt > 0.5:
                # objet en vol : silhouette aplatie selon le tangage
                flat = max(0.25, math.sin(math.radians(cam.pitch)))
                sh_h = max(1, int(round(h * flat)))
                ys = np.minimum((np.arange(sh_h) / flat).astype(int), h - 1)
                smask = sm[ys]
                shade(idx, pal.shadow, smask, gsx - w / 2, gsy - sh_h / 2)
            else:
                # posé : ombre portée cisaillée vers le sud-est, écrasée
                sh_h = max(1, h // 3)
                ys = np.minimum((np.arange(sh_h) * 3).astype(int), h - 1)
                smask = sm[ys][::-1]
                shade(idx, pal.shadow, smask, sx - w / 2 + max(1, w // 3), sy - sh_h + 1)
        blit(idx, depth, si, sm, sx - w / 2, sy - h, zc - 0.5)
        return sx, sy, zc


# ---------------------------------------------------------------- texte
class Fonts:
    def __init__(self):
        base = ROOT / 'node_modules' / '@fontsource'
        self.paths = {n: base / f'jersey-{n}' / 'files' / f'jersey-{n}-latin-400-normal.woff2' for n in (10, 15, 20)}
        self.size = {10: 56 / 3, 15: 27, 20: 34}
        self.em = {10: 19, 15: 27, 20: 34}
        self.f = {n: ImageFont.truetype(str(self.paths[n]), self.size[n]) for n in (10, 15, 20)}

    def width(self, n, s):
        return int(math.ceil(self.f[n].getlength(s)))

    def mask(self, n, s):
        f = self.f[n]
        w = self.width(n, s) + 2
        h = self.em[n] + 2
        im = Image.new('1', (w, h), 0)
        dr = ImageDraw.Draw(im)
        dr.fontmode = '1'
        dr.text((0, 0), s, font=f, fill=1)
        return np.array(im, bool)


FONTS = None


def fonts():
    global FONTS
    if FONTS is None:
        FONTS = Fonts()
    return FONTS


def cartouche(idx, pal, lines, x, y, size=15, colors=None, progress=1.0, anchor='lt', pad=5, inverted=False,
              colors_line=None, outer=True):
    """Cartouche crème (ou plaque inversée encre) à cadre 1 px, coin coupé, ombre plate (2, 2) par la table d'ombre.
    lines ≤ 2, chaque ligne ≤ 214 px natifs (assertion). progress : 0→1 ouverture en hauteur (4 images).
    Renvoie la boîte (x0, y0, x1, y1)."""
    F = fonts()
    assert 1 <= len(lines) <= 2, 'au plus 2 lignes par cartouche (C5)'
    widths = [F.width(size, s) for s in lines]
    for s, wv in zip(lines, widths):
        assert wv <= TEXT_MAXW, f'ligne trop large ({wv} px natifs > {TEXT_MAXW}) : « {s} »'
    em = F.em[size]
    bw = max(widths) + 2 * pad + 2
    bh = em * len(lines) + pad + 3 + 2      # marge haute = pad (≥ 5 : accents), basse 3 (+ cadres)
    if anchor[0] == 'c':
        x = x - bw // 2
    elif anchor[0] == 'r':
        x = x - bw
    if anchor[1] == 'b':
        y = y - bh
    x, y = int(x), int(y)
    # zones sûres (C5) : boîte + liseré + ombre (2, 2) dans [16, 240] × [55, 400] natifs
    assert x - 1 >= SAFE_L and x + bw + 2 <= NW - SAFE_R and y - 1 >= SAFE_T and y + bh + 2 <= NH - SAFE_B, \
        f'cartouche hors zone sûre : {lines} ({x}, {y}, {bw}×{bh})'
    full_h = bh
    bh_draw = max(2, int(round(full_h * clamp01(progress)))) if progress < 1 else full_h
    yc = y + (full_h - bh_draw) // 2
    bg = pal['INK'] if inverted else pal['CREAM']
    fr = pal['CREAM'] if inverted else pal['INK']
    # ombre plate décalée (2, 2)
    sh = np.ones((bh_draw, bw), bool)
    sh[0, 0] = sh[0, -1] = sh[-1, 0] = sh[-1, -1] = False
    shade(idx, pal.shadow, sh, x + 2, yc + 2)
    # liseré extérieur crème (contraste sur brume / nuage / océan)
    if outer and not inverted:
        ring = np.zeros((bh_draw + 2, bw + 2), bool)
        ring[0, 2:-2] = ring[-1, 2:-2] = True
        ring[2:-2, 0] = ring[2:-2, -1] = True
        ring[1, 1] = ring[1, -2] = ring[-2, 1] = ring[-2, -2] = True
        blit(idx, None, np.full(ring.shape, pal['CREAM'], np.uint8), ring, x - 1, yc - 1)
    box = np.full((bh_draw, bw), bg, np.uint8)
    box[0, :] = box[-1, :] = fr
    box[:, 0] = box[:, -1] = fr
    m = np.ones((bh_draw, bw), bool)
    m[0, 0] = m[0, -1] = m[-1, 0] = m[-1, -1] = False      # coin coupé d'un pixel
    if bh_draw > 1:
        box[1, 1] = box[1, -2] = box[-2, 1] = box[-2, -2] = fr
    blit(idx, None, box, m, x, yc)
    if progress >= 1:
        for k, s in enumerate(lines):
            tm = F.mask(size, s)
            col = (colors_line[k] if colors_line else (colors or ('CREAM' if inverted else 'INK')))
            ind = np.full(tm.shape, pal[col], np.uint8)
            tx = x + 1 + pad + (bw - 2 - 2 * pad - widths[k]) // 2
            ty = y + 1 + pad - 1 + k * em
            blit(idx, None, ind, tm, tx, ty)
    return (x, y, x + bw, y + full_h)


def text_plain(idx, pal, s, x, y, size=10, color='INK'):
    F = fonts()
    tm = F.mask(size, s)
    blit(idx, None, np.full(tm.shape, pal[color], np.uint8), tm, int(x), int(y))
    return F.width(size, s)


def line_px(idx, pal, x0, y0, x1, y1, color='INK'):
    """Trait de 1 px natif (Bresenham)."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    c = pal[color]
    while True:
        if 0 <= x0 < NW and 0 <= y0 < NH:
            idx[y0, x0] = c
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def pin(idx, pal, gx, gy, box_pt):
    """Épingle au sol (point projeté) reliée au cartouche par un trait de 1 px (C9)."""
    line_px(idx, pal, box_pt[0], box_pt[1], gx, gy, 'INK')
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x, y = int(round(gx)) + dx, int(round(gy)) + dy
            if 0 <= x < NW and 0 <= y < NH:
                idx[y, x] = pal['INK'] if (dx or dy) else pal['GOLD']


def pinned_card(idx, pal, lines, bx, by, gx, gy, size=15):
    """Étiquette au sol : cartouche à l'écran + trait de 1 px vers l'épingle (le trait passe sous le cartouche)."""
    box = cartouche(idx, pal, lines, bx, by, size=size, anchor='lt')
    ax = box[2] - 1 if gx > (box[0] + box[2]) / 2 else box[0]
    pin(idx, pal, gx, gy, (ax, (box[1] + box[3]) // 2))
    cartouche(idx, pal, lines, bx, by, size=size, anchor='lt')
    return box


# ---------------------------------------------------------------- bruit (calculé une fois, en cache)
def noise_field(G, scale, seed, cache_dir, octaves=2):
    """Champ opensimplex G×G dans [-1, 1], mis en cache (.npy) dans cache_dir (jamais dans le dépôt)."""
    cache = Path(cache_dir) / f'noise_{G}_{scale}_{seed}_{octaves}.npy'
    if cache.exists():
        return np.load(cache)
    import opensimplex
    acc = np.zeros((G, G))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        opensimplex.seed(seed + 101 * o)
        c = np.arange(G) / scale * (2 ** o)
        acc += amp * opensimplex.noise2array(c, c)
        tot += amp
        amp *= 0.5
    acc /= tot
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, acc.astype(np.float32))
    return acc.astype(np.float32)


def foam_tile(pal, n=64, seed=0, base='OCEAN', density=1 / 150, phase=0):
    """Moutons d'écume : traits obliques de 2–3 cellules semés sur une grille jitterée ; deux phases (≤ 3 Hz)."""
    rng = np.random.default_rng(seed)
    tile = np.full((n, n), pal[base], np.uint8)
    cell = int(round(1 / math.sqrt(density)))
    for gy in range(0, n, cell):
        for gx in range(0, n, cell):
            ph = rng.integers(0, 2)
            x, y = gx + rng.integers(0, cell - 3), gy + rng.integers(0, cell - 2)
            ln = rng.integers(2, 4)
            if ph != phase and rng.random() < 0.6:
                continue
            for k in range(ln):
                tile[(y + (k // 2)) % n, (x + k) % n] = pal['FOAM']
    return tile


# ---------------------------------------------------------------- sortie
def to_rgb(idx, pal):
    return pal.rgb[idx]


def upscale(rgb):
    return np.repeat(np.repeat(rgb, SCALE, 0), SCALE, 1)


class Short:
    """Une scène : build -> frame_idx(t) (indices natifs). Le moteur gère stills, rendu, mesures.
    check(t) -> (cam, world) sert au contrôle préalable (caméra au-dessus du relief à chaque image)."""

    def __init__(self, pal, duration, frame_idx, check=None):
        self.pal = pal
        self.duration = duration
        self.frame_idx = frame_idx
        self.check = check

    def frame_rgb(self, t):
        return upscale(to_rgb(self.frame_idx(t), self.pal))

    def frame_pil(self, t):
        return Image.fromarray(self.frame_rgb(t))


def render(short, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    part = str(out) + '.part.mp4'
    n = int(round(short.duration * FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14',
                           '-pix_fmt', 'yuv420p', '-r', str(FPS), part], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        ff.stdin.write(short.frame_rgb(i / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    os.replace(part, out)
    sec = time.time() - t0
    return {'frames': n, 'seconds': round(sec, 1), 'secPer100Frames': round(sec / n * 100, 2)}


def load():
    try:
        return os.getloadavg()[0]
    except OSError:
        return None


def main(build, default_out):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=default_out)
    ap.add_argument('--stills')
    ap.add_argument('--dir')
    ap.add_argument('--native', action='store_true', help='stills aussi en PNG natif 270×480 (comptage de couleurs)')
    ap.add_argument('--bench', type=int, default=0, help='mesure N images réparties sur la durée')
    ap.add_argument('--preflight', action='store_true', help='contrôle caméra / relief sur toutes les images')
    a = ap.parse_args()
    tb = time.time()
    short = build()
    build_sec = time.time() - tb
    if a.preflight:
        n = int(round(short.duration * FPS))
        low = []
        for i in range(n):
            cam, w = short.check(i / FPS)
            cxi, cyi = int(cam.pos[0]), int(cam.pos[1])
            if 0 <= cxi < w.G and 0 <= cyi < w.G:
                clear = cam.pos[2] - float(w.top[max(cyi - 2, 0):cyi + 3, max(cxi - 2, 0):cxi + 3].max())
                low.append(clear)
                assert clear > 1.0, f'image {i} : caméra à {clear:.1f} du relief'
        print(json.dumps({'frames': n, 'minClearance': round(min(low), 1) if low else None}))
        return
    if a.bench:
        ts = np.linspace(0, short.duration - 1 / FPS, a.bench)
        l0 = load()
        t0 = time.time()
        for t in ts:
            short.frame_rgb(float(t)).tobytes()
        sec = time.time() - t0
        print(json.dumps({'frames': a.bench, 'seconds': round(sec, 2), 'secPer100Frames': round(sec / a.bench * 100, 1),
                          'load1': l0, 'buildSec': round(build_sec, 2)}))
        return
    if a.stills:
        Path(a.dir).mkdir(parents=True, exist_ok=True)
        for s in a.stills.split(','):
            name = None
            if ':' in s:
                name, s = s.split(':')
            t = float(s)
            t0 = time.time()
            ind = short.frame_idx(t)
            dt = time.time() - t0
            im = Image.fromarray(upscale(to_rgb(ind, short.pal)))
            stem = f'{name}_{t:.2f}s' if name else f'still_{t:05.2f}s'
            p = Path(a.dir) / f'{stem}.jpg'
            im.save(p, quality=92)
            if a.native:
                Image.fromarray(to_rgb(ind, short.pal)).save(Path(a.dir) / f'{stem}_native.png')
            print(p, f'{dt * 1000:.0f} ms/frame', f'{len(np.unique(ind))} couleurs')
        return
    l0 = load()
    res = render(short, a.out)
    print(json.dumps(res | {'buildSec': round(build_sec, 2), 'load1Start': l0, 'load1End': load()}))
