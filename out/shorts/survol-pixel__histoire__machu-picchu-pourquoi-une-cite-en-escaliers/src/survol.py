#!/usr/bin/env python3
"""
survol.py — moteur de l'identité « Survol pixel ». Copie identique dans chaque short (convention de trait-continu).

Principe : un petit monde en pixel art 16 bits survolé par UNE caméra sténopé (cible, distance, cap, tangage, roulis)
pour tout le short. Rendu à 270×480 en indices de palette, agrandi ×4 au plus proche voisin (1080×1920).

- Sol et relief : lancer de rayon sur une carte de hauteurs EN TERRASSES (valeurs constantes par cellule). Passe A+B+C :
  4 rayons par pixel (2×2) puis VOTE MAJORITAIRE sur l'indice de palette (jamais de moyenne de couleurs : on reste en
  pixel art indexé). Marche en deux temps : saut des zones vides sur une carte des maxima par blocs, puis pas
  géométriques (proportionnels à la distance) + 8 bissections. Hors de la boîte : plan z = 0 en forme close (le
  « Mode 7 » généralisé, valable de 0° à 90° de tangage). Le même moteur sert tout le short (C1).
- Contremarches (flancs) : un impact sur une paroi prend la couleur de flanc du matériau, claire si la paroi regarde la
  lumière (nord-ouest), sombre sinon (C2). Plus de règle « mur lointain = couleur du dessus » : un mur reste un mur.
- Coupe : une région « coupée » de la carte (dessus = socle à z = −D) montre sur ses parois la coupe du terrain,
  colorée par une fonction de la scène.
- Couleurs : carte de couleurs FINE (k = 4 cases par cellule de hauteur) sur la fenêtre du sujet, carte grossière
  ailleurs ; réductions par vote majoritaire (jamais de moyenne). Le niveau de réduction suit l'empreinte du
  sous-rayon au sol, avec un décalage fixe dans le monde par cellule (hachage) : la transition entre deux niveaux est
  semée dans le monde au lieu d'être une ligne qui balaie l'écran. Plus de biais de pente.
- Ombrage du relief : carte d'ombre portée calculée une fois par monde (table d'ombre sur les dessus).
- Brume : 5–6 paliers (tables d'indices par matière), seuils proportionnels à une distance de référence lissée
  (fournie par la scène), frontière crénelée fixée dans le monde (hachage par cellule). Le dernier palier est la
  couleur du bas du ciel (HAZE, bleu très pâle) : pas de couture à l'horizon.
- Ciel en ~6 paliers doux selon l'élévation du rayon (s'incline avec le roulis).
- Nuages : piles de disques dessinés au pixel près à la taille projetée (jamais agrandis) ; ombres au sol par un
  masque monde tramé une fois par image.
- Objets : panneaux dessinés en code, réduits au plus proche voisin, jamais agrandis au-delà de 1:1 (C4).
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
    'HAZE': '#DCEEF5', 'CREAM': '#FBF3D5', 'INK': '#14213D', 'WATER_FAR': '#5B9DCD', 'LAND_FAR': '#92B9A4',
    'RED': '#B5341A', 'GOLD': '#FFC94A', 'MUTED': '#5A5F73', 'CLOUD_RIM': '#CFE3F2',
    # passe A : paliers de ciel et rampes de brume (bleu très pâle, jamais crème)
    'SKY_2': '#AAD6EF', 'SKY_4': '#83C0E8', 'SKY_1': '#CCE7F3',
    'HZ_G1': '#3E8A3E', 'HZ_G2': '#5E9C6C', 'HZ_G3': '#86B59C', 'HZ_G4': '#B3D3CF',
    'HZ_W1': '#4688C6', 'HZ_W2': '#7AAFD9', 'HZ_W3': '#A8CDE6',
    'HZ_R1': '#9AA3A4',
}
HAZE_STEPS = 6


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Palette:
    """Table de palette indexée : noyau fixe + couleurs « biome » de l'épisode.
    haze[k] (k = 1..HAZE_STEPS) : table d'indices du palier de brume k ; haze[0] = identité."""

    def __init__(self, extra):
        self.names = list(CORE) + list(extra)
        self.hex = dict(CORE) | dict(extra)
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.rgb = np.array([hex2rgb(self.hex[n]) for n in self.names], np.uint8)
        n = len(self.names)
        self.shadow = np.arange(n, dtype=np.uint8)   # ombre portée : indice -> indice plus sombre
        self.haze = np.tile(np.arange(n, dtype=np.uint8), (HAZE_STEPS + 1, 1))
        self.speckle = np.arange(n, dtype=np.uint8)

    def __getitem__(self, k):
        return self.idx[k]

    def set_lut(self, lut, mapping):
        for a, b in mapping.items():
            getattr(self, lut)[self.idx[a]] = self.idx[b]

    def set_haze(self, families, default=None):
        """families : {nom de couleur: [palier1, …, palier5]} (noms) ; le dernier palier est HAZE.
        default : rampe pour les couleurs non listées (ciel, nuages, texte exclus)."""
        for n in self.names:
            ramp = families.get(n, default if n not in ('CLOUD', 'HATCH', 'CREAM', 'INK', 'CLOUD_RIM', 'GOLD', 'RED')
                                else None)
            if ramp is None:
                continue
            assert len(ramp) == HAZE_STEPS, (n, ramp)
            for k, m in enumerate(ramp, 1):
                self.haze[k][self.idx[n]] = self.idx[m]


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
    (90 = verticale), roll en degrés.
    smooth=True : interpolation cubique monotone (PCHIP, C1, sans dépassement) entre les clés, pour un vol sans
    à-coups ni rebond sous le relief (l'easing est alors ignoré)."""

    def __init__(self, keys, smooth=False):
        self.keys = keys
        self.smooth = smooth

    def at(self, t):
        ks = self.keys
        if self.smooth:
            if not hasattr(self, '_pchip'):
                from scipy.interpolate import PchipInterpolator
                ts = np.array([k[0] for k in ks])
                self._pchip = {c: PchipInterpolator(ts, [k[1][c] for k in ks]) for c in CAM_KEYS}
            tt = min(max(t, ks[0][0]), ks[-1][0])
            return {c: float(self._pchip[c](tt)) for c in CAM_KEYS}
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
        self.dist = p['dist']

    def project(self, P):
        """point(s) monde -> (sx, sy, profondeur). P : (..., 3)."""
        v = np.asarray(P, float) - self.pos
        zc = v @ self.f
        xc = v @ self.r
        yc = v @ self.u
        zc_safe = np.where(zc > 1e-6, zc, 1e-6)
        return self.cx + self.F * xc / zc_safe, self.cy - self.F * yc / zc_safe, zc

    def rays(self, ss=1):
        """Sous-rayons ss×ss par pixel (centres des sous-cases) : (NH*ss, NW*ss, 3), composante le long de f = 1."""
        i = (np.arange(NW * ss, dtype=np.float32) + 0.5) / ss
        j = (np.arange(NH * ss, dtype=np.float32) + 0.5) / ss
        i = (i - self.cx) / self.F
        j = (j - self.cy) / self.F
        I, J = np.meshgrid(i, j)
        d = (self.f[None, None, :] + I[..., None] * self.r[None, None, :] - J[..., None] * self.u[None, None, :])
        return d.astype(np.float32)


# ---------------------------------------------------------------- monde
def mode_down(c):
    """Réduction ×2 par vote majoritaire (indices, pas de moyenne). Égalité -> coin haut gauche."""
    G0, G1 = c.shape[0] // 2 * 2, c.shape[1] // 2 * 2
    a, b, cc, d = c[0:G0:2, 0:G1:2], c[0:G0:2, 1:G1:2], c[1:G0:2, 0:G1:2], c[1:G0:2, 1:G1:2]
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


def vote4(a, b, c, d):
    """Vote majoritaire entre 4 tableaux d'indices ; égalité -> le premier (a) s'il est à égalité, sinon b, c."""
    na = (a == b).astype(np.int8) + (a == c) + (a == d)
    nb = (b == a).astype(np.int8) + (b == c) + (b == d)
    nc = (c == a).astype(np.int8) + (c == b) + (c == d)
    nd = (d == a).astype(np.int8) + (d == b) + (d == c)
    which = np.zeros(a.shape, np.int8)
    best = na.copy()
    for k, n in ((1, nb), (2, nc), (3, nd)):
        m = n > best
        which[m] = k
        best[m] = n[m]
    return which


def relief_shade(top, sun, reach=48, slope=0.55):
    """Ombre portée du relief (calculée une fois) : une cellule est à l'ombre si une cellule vers la lumière, à k pas,
    dépasse sa hauteur de plus de k × slope × |pas|. sun : décalage d'ombre au sol par unité d'altitude (vers l'ombre)."""
    L = -np.array(sun, np.float32)
    L /= np.linalg.norm(L)
    tp = np.maximum(top, 0).astype(np.float32)
    best = np.full(tp.shape, -1e9, np.float32)
    for k in range(1, reach + 1):
        dx, dy = int(round(L[0] * k)), int(round(L[1] * k))
        sh = np.roll(tp, (-dy, -dx), (0, 1))
        best = np.maximum(best, sh - k * slope)
    return best > tp + 0.5


class World:
    """Carte de hauteurs en terrasses (dessus constant par cellule, 1 cellule = 1 unité monde) et cartes de couleurs.
    top : hauteur du dessus (eau = 0, socle de coupe = -depth) ; col : indice de couleur du dessus (1 case / cellule) ;
    fine : (x0, y0, k, carte) carte de couleurs k fois plus fine sur la fenêtre [x0, x0 + N/k) × [y0, y0 + N/k) ;
    flank_lit / flank_dark : indice de flanc par cellule ; cut : masque de coupe ; section(...) -> indices ;
    shade : masque d'ombre portée du relief (table d'ombre sur les dessus)."""

    def __init__(self, top, col, flank_lit, flank_dark, cut=None, section=None, outside=0, zmin=-1.0, levels=4,
                 outside_tile=None, cut_top0=None, coursed=None, fine=None, shade=None):
        self.G = top.shape[0]
        self.coursed = coursed
        self.top = top.astype(np.float32)
        self.col = [col.astype(np.uint8)]
        if fine is not None:
            fx0, fy0, k, fc = fine
            self.fk = k
            self.fx0, self.fy0 = int(fx0), int(fy0)
            self.fine = [fc.astype(np.uint8)]
            lk = int(round(math.log2(k)))
            for _ in range(lk):
                self.fine.append(mode_down(self.fine[-1]))
            # la carte grossière reprend, dans la fenêtre, la réduction de la carte fine : pas de saut à la frontière
            n = self.fine[-1].shape[0]
            self.col[0][self.fy0:self.fy0 + n, self.fx0:self.fx0 + n] = self.fine[-1]
            self.fn = n
        else:
            self.fine = None
            self.fk = 1
        for _ in range(levels):
            self.col.append(mode_down(self.col[-1]))
        self.flank_lit = flank_lit.astype(np.uint8)
        self.flank_dark = flank_dark.astype(np.uint8)
        self.cut = cut if cut is not None else np.zeros_like(top, bool)
        self.section = section
        self.cut_top0 = cut_top0
        self.shade = shade
        self.outside = outside
        self.tile = None
        if outside_tile is not None:
            self.tile = [outside_tile.astype(np.uint8)]
            for _ in range(levels + 2):
                if self.tile[-1].shape[0] < 2:
                    break
                self.tile.append(mode_down(self.tile[-1]))
        # cartes des maxima par blocs (128, 32, 8, 2), dilatées d'un bloc : pas sûrs au-dessus du relief
        from scipy.ndimage import maximum_filter
        for B in (128, 32, 8, 2):
            nb = -(-self.G // B)
            pad = np.full((nb * B, nb * B), -1e9, np.float32)
            pad[:self.G, :self.G] = self.top
            bm = pad.reshape(nb, B, nb, B).max((1, 3))
            setattr(self, f'bmax{B}', maximum_filter(bm, size=3, mode='nearest').astype(np.float32))
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


# ---------------------------------------------------------------- bruit et hachage (fixes dans le monde)
def hash01(ix, iy, k=0):
    """Bruit blanc fixe dans le monde : entiers -> [0, 1) (hachage entier, déterministe, sans état)."""
    h = (np.asarray(ix, np.int64) * 73856093) ^ (np.asarray(iy, np.int64) * 19349663) ^ (np.asarray(k, np.int64) * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return ((h & 0xFFFF).astype(np.float32)) / 65536.0


def ragged(shape, seed, amp=1.0):
    """Décalage fixe par cellule dans [-amp/2, amp/2) : rend crénelés les seuils d'un champ continu."""
    return ((np.random.default_rng(seed).random(shape) - 0.5) * amp).astype(np.float32)


def vnoise(xx, yy, scale, seed, octaves=1):
    """Bruit de valeur lissé (hachage du réseau + interpolation smoothstep), rapide, fixe dans le monde : [-1, 1]."""
    acc = np.zeros(np.broadcast(xx, yy).shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = scale / (2 ** o)
        x, y = xx / s, yy / s
        x0, y0 = np.floor(x), np.floor(y)
        fx, fy = x - x0, y - y0
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x0i, y0i = x0.astype(np.int64), y0.astype(np.int64)
        k = seed * 7 + o
        a = hash01(x0i, y0i, k)
        b = hash01(x0i + 1, y0i, k)
        c = hash01(x0i, y0i + 1, k)
        d = hash01(x0i + 1, y0i + 1, k)
        v = a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy
        acc += amp * (v * 2 - 1)
        tot += amp
        amp *= 0.5
    return acc / tot


def disk_mask(disks, x0, y0, nx, ny, cell=1.0):
    """Masque monde (ny, nx) des disques (x, y, r), tramé au pas `cell` : ombres des nuages, une fois par image."""
    m = np.zeros((ny, nx), bool)
    for (sx, sy, R) in disks:
        i0, i1 = int((sx - R - x0) / cell), int((sx + R - x0) / cell) + 1
        j0, j1 = int((sy - R - y0) / cell), int((sy + R - y0) / cell) + 1
        i0c, i1c, j0c, j1c = max(i0, 0), min(i1, nx), max(j0, 0), min(j1, ny)
        if i1c <= i0c or j1c <= j0c:
            continue
        jj, ii = np.mgrid[j0c:j1c, i0c:i1c]
        px = x0 + (ii + 0.5) * cell
        py = y0 + (jj + 0.5) * cell
        m[j0c:j1c, i0c:i1c] |= (px - sx) ** 2 + (py - sy) ** 2 < R * R
    return (m, x0, y0, cell)


# ---------------------------------------------------------------- rendu du sol
class Renderer:
    def __init__(self, pal, focal=416.0, sun=(0.30, -0.62), sky=None, haze_k=(1.2, 1.6, 2.1, 2.7, 3.4, 4.3), steps=None,
                 mip_bias=0.0, course=0.0, ss=2, step_c=0.006, step_min=0.3, haze_jit=0.10, wall_speck=0.0, haze_cell=8.0):
        self.pal = pal
        self.wall_speck = wall_speck  # part de moucheture des contremarches (table pal.speckle), 0 = aucune
        self.course = course          # hauteur d'assise des parois appareillées (unités monde), 0 = pas d'appareil
        self.focal = focal
        self.sun = np.array(sun, np.float32)                  # décalage d'ombre au sol par unité d'altitude
        Ll = np.array([-sun[0], -sun[1]], np.float32)         # direction horizontale vers la lumière
        self.light_h = Ll / np.linalg.norm(Ll)
        # ciel : 6 paliers doux selon l'élévation (degrés) ; le palier du bas = HAZE = dernier palier de brume
        self.sky = sky or [(0.7, 'HAZE'), (2.2, 'SKY_1'), (4.5, 'SKY_LO'), (8.0, 'SKY_2'), (13.0, 'SKY_MID'),
                           (20.0, 'SKY_4'), (90.0, 'SKY_HI')]
        self.haze_k = haze_k          # seuils de brume en multiples de la distance de référence (lissée)
        self.haze_jit = haze_jit      # crénelage de la frontière (part du seuil), fixe dans le monde
        self.haze_cell = haze_cell    # taille (unités) des cases du crénelage : ≥ 1 px au loin, sinon il scintille
        self.mip_bias = mip_bias
        self.ss = ss
        self.step_c = step_c
        self.step_min = step_min

    # -- lancer de rayon dans la boîte du relief : pas adaptatifs conservatifs (cartes des maxima par blocs de 128, 32,
    # 8 et 2, dilatées d'un bloc : au-dessus du maximum, on avance d'un pas sûr), sinon pas géométriques ; puis bissections
    def _march(self, w, o, d, tin, tout):
        top, G = w.top, w.G
        n = len(tin)
        hit_t = np.full(n, np.inf, np.float32)
        lo_t = np.zeros(n, np.float32)
        c = np.float32(self.step_c)
        a = np.float32(self.step_min / self.step_c)
        dxy = np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2) + 1e-6
        ndz = np.maximum(-d[:, 2], 1e-6)
        t = tin.astype(np.float32).copy()
        prev = t.copy()
        act = np.arange(n)
        maps = [(getattr(w, f'bmax{B}'), B) for B in (128, 32, 8, 2)]
        it = 0
        while len(act) and it < 2000:
            it += 1
            ta = t[act]
            da = d[act]
            px = o[0] + ta * da[:, 0]
            py = o[1] + ta * da[:, 1]
            pz = o[2] + ta * da[:, 2]
            xi = px.astype(np.int32)
            yi = py.astype(np.int32)
            np.clip(xi, 0, G - 1, out=xi)
            np.clip(yi, 0, G - 1, out=yi)
            under = pz < top[yi, xi]
            if under.any():
                ids = act[under]
                hit_t[ids] = ta[under]
                lo_t[ids] = prev[ids]
            keep = ~under
            act = act[keep]
            ta, px, py, pz, xi, yi = ta[keep], px[keep], py[keep], pz[keep], xi[keep], yi[keep]
            # pas sûr : tant que le rayon reste au-dessus du maximum du voisinage (bloc dilaté), sur ≤ B en plan
            dt = c * (ta + a)
            for m, B in maps:
                bm = m[yi // B, xi // B]
                safe = np.minimum(B / dxy[act], (pz - bm) / ndz[act])
                dt = np.where(pz > bm, np.maximum(dt, safe), dt)
            prev[act] = ta
            to_a = tout[act]
            tn = np.minimum(ta + dt, to_a)          # le dernier échantillon est pris exactement à la sortie de la boîte
            t[act] = tn
            alive = ta < to_a
            act = act[alive]
        found = np.isfinite(hit_t)
        ids = np.nonzero(found)[0]
        lo, hi = lo_t[ids], hit_t[ids]
        dd = d[ids]
        for _ in range(8):
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

    def _colour(self, w, hx, hy, xi, yi, ingrid, fp):
        """Couleur du dessus par carte fine / grossière ; niveau de réduction selon l'empreinte, décalé par cellule."""
        k = w.fk
        lk = int(round(math.log2(k)))
        dith = hash01(np.floor(hx).astype(np.int64), np.floor(hy).astype(np.int64), 5) - 0.5
        Lf = np.floor(np.log2(np.maximum(fp * k, 1e-6)) + self.mip_bias + dith).astype(np.int32)
        Lf = np.clip(Lf, 0, lk + len(w.col) - 1)
        out = np.full(len(hx), w.outside, np.uint8)
        done = np.zeros(len(hx), bool)
        if w.fine is not None:
            fx = hx - w.fx0
            fy = hy - w.fy0
            inw = ingrid & (fx >= 0) & (fy >= 0) & (fx < w.fn) & (fy < w.fn)
            for L in range(lk):
                m = inw & (Lf == L)
                if m.any():
                    c = w.fine[L]
                    s = k / (1 << L)
                    out[m] = c[np.clip((fy[m] * s).astype(np.int64), 0, c.shape[0] - 1),
                               np.clip((fx[m] * s).astype(np.int64), 0, c.shape[1] - 1)]
                    done |= m
        Lc = np.maximum(Lf - lk, 0)
        for L in range(len(w.col)):
            m = ingrid & ~done & (Lc == L)
            if m.any():
                c = w.col[L]
                out[m] = c[np.clip(yi[m] >> L, 0, c.shape[0] - 1), np.clip(xi[m] >> L, 0, c.shape[1] - 1)]
        if w.tile is not None:
            for L in range(len(w.tile)):
                m = ~ingrid & ((Lc == L) if L < len(w.tile) - 1 else (Lc >= L))
                if m.any():
                    c = w.tile[L]
                    out[m] = c[np.floor(hy[m] / (1 << L)).astype(np.int64) % c.shape[0],
                               np.floor(hx[m] / (1 << L)).astype(np.int64) % c.shape[1]]
        return out

    def ground(self, w, cam, t_anim, shadow=None, haze_ref=None, shadow_disks=None):
        pal = self.pal
        cxi, cyi = int(cam.pos[0]), int(cam.pos[1])
        if 0 <= cxi < w.G and 0 <= cyi < w.G:
            assert cam.pos[2] > w.top[cyi, cxi] + 1.0, f'caméra sous le relief ({cam.pos.round(1)})'
        ss = self.ss
        SH, SW = NH * ss, NW * ss
        d = cam.rays(ss).reshape(-1, 3)
        o = cam.pos.astype(np.float32)
        n = d.shape[0]
        idx = np.zeros(n, np.uint8)
        depth = np.full(n, np.inf, np.float32)
        dz = d[:, 2]
        with np.errstate(divide='ignore', invalid='ignore'):
            tp = np.where(dz < -1e-6, (0.0 - o[2]) / dz, np.inf).astype(np.float32)
        t_hit = tp.copy()
        lo_hit = np.zeros(n, np.float32)
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
            act = np.nonzero((tmax > tmin) & (tmin < tp))[0]
            if len(act):
                ht, lt = self._march(w, o, d[act], tmin[act].astype(np.float32), tmax[act].astype(np.float32))
                ok = np.isfinite(ht)
                a2 = act[ok]
                t_hit[a2] = ht[ok]
                lo_hit[a2] = lt[ok]
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
        # empreinte du sous-rayon au sol
        dn = np.linalg.norm(dd, axis=1)
        inc = np.abs(dd[:, 2]) / dn
        fp = th * dn / (cam.F * ss) * np.sqrt(1.0 / np.maximum(inc, 0.08))
        cidx = self._colour(w, hx, hy, xi, yi, ingrid, fp)
        # ombre portée du relief (dessus seulement)
        if w.shade is not None:
            sh_r = ingrid & ~is_wall & w.shade[yi, xi]
            cidx = np.where(sh_r, pal.shadow[cidx], cidx)
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
            if self.wall_speck > 0:
                # matière des contremarches (feuillage, roche) : moucheture fixe dans le monde, cases de 0,5 unité
                alg0 = np.where(np.abs(nx) > 0, hy[wi], hx[wi])
                hs = hash01(np.floor(alg0 * 2).astype(np.int64), np.floor(hz[wi] * 2).astype(np.int64), 29)
                wc = np.where(hs < self.wall_speck, pal.speckle[wc], wc)
            if self.course > 0 and w.coursed is not None:
                # appareil de pierre : assises et joints de largeur fixe dans le monde ; il s'efface avec la distance
                # paroi par paroi (seuil tiré par cellule) au lieu de disparaître d'un coup à une distance donnée
                hcell = hash01(xi[wi], yi[wi], 17)
                cw = w.coursed[yi[wi], xi[wi]] & (fp[wi] * (2.0 + 2.0 * hcell) < self.course)
                if cw.any():
                    hzw = hz[wi]
                    alg = np.where(np.abs(nx) > 0, hy[wi], hx[wi])
                    row = np.floor(hzw / self.course)
                    bed = (hzw / self.course - row) < 0.22
                    joint = ((alg / (1.8 * self.course) + 0.5 * (row % 2)) % 1.0) < 0.12
                    wc = np.where(cw & (bed | joint), pal.shadow[wc], wc)
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
        # ombres des nuages : masque monde tramé (une fois par image)
        if shadow is not None:
            m, sx0, sy0, cell = shadow
            ix = np.floor((hx - sx0) / cell).astype(np.int64)
            iy = np.floor((hy - sy0) / cell).astype(np.int64)
            okm = (ix >= 0) & (iy >= 0) & (ix < m.shape[1]) & (iy < m.shape[0])
            shm = np.zeros(len(hx), bool)
            shm[okm] = m[iy[okm], ix[okm]]
            cidx = np.where(shm & ~is_wall, pal.shadow[cidx], cidx)
        # brume : paliers par tables, seuils proportionnels à la distance de référence, frontière crénelée fixe
        if haze_ref is not None and self.haze_k:
            hd = th * np.sqrt(dd[:, 0] ** 2 + dd[:, 1] ** 2)
            jit = 1.0 + self.haze_jit * (hash01(np.floor(hx / self.haze_cell).astype(np.int64), np.floor(hy / self.haze_cell).astype(np.int64), 9) - 0.5) * 2
            hdj = hd * jit
            step = np.zeros(len(hx), np.int32)
            for kk in self.haze_k:
                step += hdj > kk * haze_ref
            cidx = pal.haze[np.minimum(step, HAZE_STEPS), cidx]
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
        # vote majoritaire 2×2 sur l'indice de palette (pas de moyenne)
        HX = np.full(n, np.nan, np.float32)
        HY = np.full(n, np.nan, np.float32)
        HZ = np.full(n, np.nan, np.float32)
        HX[hi_ids] = hx
        HY[hi_ids] = hy
        HZ[hi_ids] = hz
        if ss == 2:
            def q4(a):
                a = a.reshape(NH, 2, NW, 2)
                return a[:, 0, :, 0], a[:, 0, :, 1], a[:, 1, :, 0], a[:, 1, :, 1]
            I4 = q4(idx)
            which = vote4(*I4)
            pick = lambda arr: np.choose(which, q4(arr))
            out_idx = np.choose(which, I4).astype(np.uint8)
            out_depth = pick(depth)
            hinfo = {'x': pick(HX), 'y': pick(HY), 'z': pick(HZ)}
        else:
            out_idx = idx.reshape(NH, NW)
            out_depth = depth.reshape(NH, NW)
            hinfo = {'x': HX.reshape(NH, NW), 'y': HY.reshape(NH, NW), 'z': HZ.reshape(NH, NW)}
        return out_idx, out_depth, hinfo


# -- marche des rayons sur GPU, FACULTATIVE : SURVOL_GPU=1 (survol_gpu.py, taichi==1.7.2, Metal). Le CPU reste le défaut
# et le secours : import sous garde, et retour au CPU au premier échec d'un appel GPU. Expérimental : parité à 1–2 ulp
# près sur 0–0,2 % des rayons (0 pixel d'écart mesuré sur 6 images), pas au bit près ; voir survol_gpu.py.
GPU = None
if os.environ.get('SURVOL_GPU') == '1':
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import survol_gpu as GPU
        _cpu_march = Renderer._march

        def _gpu_march(self, w, o, d, tin, tout):
            global GPU
            if GPU is not None:
                try:
                    return GPU.march(self, w, o, d, tin, tout)
                except Exception as e:
                    print(f'survol : échec GPU ({e}), suite du rendu sur CPU', file=sys.stderr)
                    GPU = None
            return _cpu_march(self, w, o, d, tin, tout)

        Renderer._march = _gpu_march
        print(f'survol : marche des rayons sur GPU (taichi Metal, '
              f'{GPU.device_name() or "périphérique Metal par défaut"})', file=sys.stderr)
    except Exception as e:
        GPU = None
        print(f'survol : SURVOL_GPU=1 mais GPU indisponible ({type(e).__name__}: {e}), rendu sur CPU', file=sys.stderr)

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
    rasante ; haut blanc, modelé tramé en damier sur le tiers bas droit puis croissant plein HATCH tout en bas
    (retouche Fable du 18/11 : la hachure une ligne sur deux se lisait comme un store), liseré bleuté au bas.
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
        lower = (v > 0.38 - 0.45 * u) & (ay >= 2)
        col[lower & ((ii + jj) % 2 == 0)] = HA
        col[(v > 0.72 - 0.45 * u) & (ay >= 3)] = HA
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
               max_r=7, shadows=True, haze=None):
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
    # seuil tiré par arbre dans [1,0 ; 1,8] px (hachage fixe) : les arbres n'apparaissent pas tous à la même distance ;
    # sous le seuil, la carte de couleurs fine porte déjà les houppiers (même teinte), rien ne bascule.
    thr = 1.0 + 0.8 * hash01(np.arange(len(trees)), 3, 23)
    vis = (zc > 1) & (rp >= thr) & (sx > -10) & (sx < NW + 10) & (sy > -10) & (sy < NH + 10)
    hstep = np.zeros(len(trees), np.int32)
    if haze is not None:
        # même brume que le sol (seuils × distance de référence, crénelage fixe par arbre) ; au-delà du 2e palier,
        # la carte de couleurs suffit
        ref, ks, jit = haze[:3]
        cell = haze[3] if len(haze) > 3 else 8.0
        hd = np.hypot(trees[:, 0] - cam.pos[0], trees[:, 1] - cam.pos[1])
        hd = hd * (1.0 + jit * (hash01(np.floor(trees[:, 0] / cell).astype(np.int64), np.floor(trees[:, 1] / cell).astype(np.int64), 9) - 0.5) * 2)
        for kk in ks:
            hstep += hd > kk * ref
        vis &= hstep < 3
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
        idx[ya:yb, xa:xb][mm] = pal.haze[hstep[ti]][lut[s_[mm]]] if hstep[ti] else lut[s_[mm]]
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
