#!/usr/bin/env python3
"""
« Machu Picchu : pourquoi une cité en escaliers ? » — Survol pixel, famille histoire. RECONSTITUTION STYLISÉE.

Monde inventé d'après la disposition générale du site (aucune géométrie réelle prétendue) : une crête entre deux
sommets (au sud la montagne, au nord un pain de sucre), une cité sur l'ensellement, des terrasses agricoles étroites
à murs de pierre sur les flancs, une rivière en fer à cheval dans la vallée, des nuages bas sous la cité.
Une entaille « maquette » coupe trois terrasses : la coupe montre, de haut en bas, terre, gravier, pierres, puis la
roche ; des gouttes de pluie (pixels bleus en pas entiers) traversent les couches et sortent au pied du mur.
Un lama (personnage original dessiné en code) se tient sur une terrasse, avec son ombre.

Faits (vérifiés, sources dans short.json) : ≈ 2 430 m ; XVe siècle (Pachacutec ; radiocarbone 2021 : occupation dès
≈ 1420) ; terrasses = murs de soutènement remblayés, couches pierres / gravier / terre de bas en haut, drainage qui
limite l'érosion et les glissements ; révélée au monde en 1911 (Hiram Bingham, guidé par des habitants).
"""
import math, sys, os
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import survol as S  # noqa: E402

DIR = Path(__file__).resolve().parents[1].name
CACHE = os.environ.get('SURVOL_CACHE', f'/private/tmp/survol-pixel/{DIR}')
SEED = 1911
DUR = 18.8
K = 1.8                       # échelle du monde (unités par « mètre de maquette »)
G = 640
C0 = G / 2
DH_NAT, DH_AG = 6.0 * K, 2.5 * K
CITY_Z = 72.0 * K
CUT_X0, CUT_X1 = C0 + 12 * K, C0 + 33 * K
CUT_Y0, CUT_Y1 = C0 - 27 * K, C0 - 21 * K
CUT_DEPTH = 6.0 * K
L_EARTH, L_GRAVEL, L_STONES = 1.1 * K, 2.1 * K, 3.7 * K

BIOME = {'GRANITE': '#9C968C', 'GRANITE_SH': '#5F5A55', 'THATCH': '#C9A35A', 'EARTH': '#8A5A3A'}
pal = S.Palette(BIOME)
pal.set_lut('shadow', {
    'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_D', 'GRASS_D': 'FOREST', 'FOREST': 'INK', 'GRANITE': 'GRANITE_SH',
    'GRANITE_SH': 'INK', 'THATCH': 'EARTH', 'EARTH': 'INK', 'OCEAN_MID': 'SH_WATER', 'SHALLOW': 'OCEAN_MID',
    'CLOUD': 'HATCH', 'HATCH': 'MUTED', 'SKY_LO': 'SKY_MID', 'SKY_MID': 'SKY_HI', 'SKY_HI': 'OCEAN_MID',
    'HAZE': 'SKY_MID', 'LAND_FAR': 'GRASS_D', 'MUTED': 'INK', 'CREAM': 'HATCH', 'FOAM': 'SHALLOW'})
pal.set_lut('haze1', {n: 'LAND_FAR' for n in ('GRASS_L', 'GRASS_M', 'GRASS_D', 'FOREST', 'GRANITE', 'GRANITE_SH',
                                              'THATCH', 'EARTH', 'OCEAN_MID', 'SHALLOW', 'FOAM')})
pal.set_lut('haze2', {n: 'HAZE' for n in pal.names if n not in ('CLOUD', 'HATCH', 'CREAM', 'INK')})

_W = {}


def gauss(xx, yy, x0, y0, sx, sy, h):
    return h * np.exp(-(((xx - x0) / sx) ** 2 + ((yy - y0) / sy) ** 2))


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def world():
    if _W:
        return _W['w']
    n1 = S.noise_field(G, 60.0, SEED, CACHE, 3)
    n2 = S.noise_field(G, 16.0, SEED + 5, CACHE, 2)
    yy, xx = np.mgrid[0:G, 0:G].astype(np.float32) + 0.5
    mass = np.maximum.reduce([
        gauss(xx, yy, C0, C0 - 70 * K, 40 * K, 34 * K, 125 * K),        # la montagne au sud
        gauss(xx, yy, C0 + 4 * K, C0 + 60 * K, 15 * K, 15 * K, 108 * K),  # le pain de sucre au nord
        gauss(xx, yy, C0, C0 - 6 * K, 36 * K, 48 * K, 76 * K),          # la crête de l'ensellement
    ]) + 7 * K * n1
    # rivière en fer à cheval, ouverte au sud
    rcx, rcy, rr = C0, C0 + 12 * K, 92 * K
    rc = np.hypot(xx - rcx, yy - rcy)
    d_arc = np.where(yy > C0 - 30 * K, np.abs(rc - rr), 1e9)
    d_w = np.where(yy <= C0 - 30 * K, np.abs(xx - (rcx - math.sqrt(rr ** 2 - (42 * K) ** 2))), 1e9)
    d_e = np.where(yy <= C0 - 30 * K, np.abs(xx - (rcx + math.sqrt(rr ** 2 - (42 * K) ** 2))), 1e9)
    d_riv = np.minimum.reduce([d_arc, d_w, d_e]) + 3 * K * n2
    outer = (40 * K + 30 * K * n1) * smooth((rc - 110 * K) / (70 * K))       # montagnes alentour
    Hn = np.maximum(mass, outer) * (0.12 + 0.88 * smooth((d_riv - 5 * K) / (34 * K))) + 3 * K
    river = d_riv < 5 * K
    # quantification : naturelle (marches de 6) ; terrasses agricoles (marches de 2,5) ; cité (plateau)
    e = np.sqrt(((xx - C0) / (17 * K)) ** 2 + ((yy - (C0 - 2 * K)) / (27 * K)) ** 2)
    city = e < 1
    # jupe de terrasses autour de la cité : pente douce (marches larges), puis le relief naturel
    skirt = CITY_Z - (e - 1) * 10 * K
    agz = (e >= 1) & (e < 2.2)
    flank = CITY_Z - 12 * K - (e - 2.2) * 40 * K              # au-delà : pente naturelle raide vers la rivière
    Hn = np.where(agz, np.maximum(skirt, Hn), np.where(e >= 2.2, np.maximum(flank, Hn), Hn))
    top = np.floor(Hn / DH_NAT) * DH_NAT
    top = np.where(agz, np.floor(Hn / DH_AG) * DH_AG, top)
    top = np.where(city, CITY_Z, top)
    # bâtiments : blocs alignés (murs de granite, toits de chaume), place centrale vide
    bx = ((xx - C0) // (6 * K)).astype(int)
    by = ((yy - C0) // (5 * K)).astype(int)
    inb = (((xx - C0) % (6 * K)) > 1.2 * K) & (((yy - C0) % (5 * K)) > 1.2 * K)
    plaza = (np.abs(xx - C0) < 6 * K) & (np.abs(yy - (C0 - 2 * K)) < 9 * K)
    rng = np.random.default_rng(SEED)
    keep = rng.random((40, 40)) < 0.78
    bld = city & inb & ~plaza & keep[(bx + 20) % 40, (by + 20) % 40] & \
        (((xx - C0) / (15 * K)) ** 2 + ((yy - (C0 - 2 * K)) / (25 * K)) ** 2 < 1)
    top = np.where(bld, CITY_Z + 2.6 * K, top)
    top = np.where(river, 0.0, top).astype(np.float32)
    # couleurs
    col = np.full((G, G), pal['FOREST'], np.uint8)
    lvl_n = np.floor(top / DH_NAT).astype(int)
    col[(lvl_n % 2 == 0)] = pal['GRASS_D']
    col[n2 > 0.25] = pal['FOREST']
    col[(top < 10 * K)] = pal['GRASS_M']
    col[(top > 100 * K)] = pal['GRANITE']
    lvl_a = np.floor(top / DH_AG).astype(int)
    col[agz & (lvl_a % 2 == 0)] = pal['GRASS_L']
    col[agz & (lvl_a % 2 == 1)] = pal['GRASS_M']
    col[city] = pal['GRANITE']
    col[plaza & city] = pal['GRASS_L']
    col[bld] = pal['THATCH']
    col[river] = pal['OCEAN_MID']
    col[river & (rng.random((G, G)) < 0.05)] = pal['FOAM']
    # pied des marches : trait sombre
    higher = np.zeros((G, G), bool)
    for sh in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        higher |= np.roll(top, sh, (0, 1)) > top + 0.1
    foot = higher & ~river & ~bld
    col[foot & agz] = pal['GRASS_D']
    col[foot & ~agz & ~city & (top <= 100 * K)] = pal['FOREST']
    col[foot & (top > 100 * K)] = pal['GRANITE_SH']
    col[foot & city & ~plaza] = pal['GRANITE_SH']
    # flancs : murs de pierre (terrasses, bâtiments), forêt ailleurs
    fl = np.full((G, G), pal['GRASS_D'], np.uint8)
    fd = np.full((G, G), pal['FOREST'], np.uint8)
    stone = agz | city | bld | (top > 100 * K)
    fl[stone] = pal['GRANITE']
    fd[stone] = pal['GRANITE_SH']
    # l'entaille (maquette de coupe) dans trois terrasses du flanc est
    cut = (xx > CUT_X0) & (xx < CUT_X1) & (yy > CUT_Y0) & (yy < CUT_Y1)
    top0 = top.copy()
    top = np.where(cut, top - CUT_DEPTH, top)
    col[cut] = pal['GRANITE_SH']

    def section(hx, hy, hz, xi, yi, along, t):
        d = top0[yi, xi] - hz
        out = np.full(len(hz), pal['GRANITE_SH'], np.uint8)            # roche en place
        st = d < L_STONES                                               # pierres : blocs et joints
        mortar = ((along % (1.7 * K)) < 0.45) | (((hz + 0.5 * np.floor(along / (1.7 * K))) % (1.1 * K)) < 0.35)
        out[st] = pal['GRANITE']
        out[st & mortar] = pal['GRANITE_SH']
        gr = d < L_GRAVEL                                               # gravier : gris clair moucheté
        speck = ((np.floor(along * 1.6) * 7 + np.floor(hz * 1.6) * 3) % 5) == 0
        out[gr] = pal['HATCH']
        out[gr & speck] = pal['GRANITE_SH']
        out[d < L_EARTH] = pal['EARTH']
        out[d < 0.35 * K] = pal['GRASS_M']
        return out

    w = S.World(top, col, fl, fd, cut=cut, section=section, outside=pal['FOREST'], zmin=-1.0,
                outside_tile=np.full((8, 8), pal['FOREST'], np.uint8), cut_top0=top0)
    _W.update(w=w, top0=top0, agz=agz)
    return w


# ------------------------------------------------------------------ lama (personnage original, dessiné en code)
LLAMA = ["...EE...................",
         "...LE...................",
         "..LLLL..................",
         "..LKLL..................",
         ".MLLLL..................",
         "..LLLL..................",
         "...LLL..................",
         "...LLL..................",
         "...LLL..................",
         "...LLL..................",
         "...LLLLLLLLLLLLLLL......",
         "...LLLLLLLLLLLLLLLL.....",
         "...LLLRGRGRLLLLLLLLL....",
         "....LLRGRGRLLLLLLLLL....",
         "....LLRGRGRLLLLLLLLL.L..",
         ".....LLLLLLLLLLLLLL..LL.",
         ".....LLLLLLLLLLLLLL.....",
         ".....LL.LL....LL.LL.....",
         ".....LL.LL....LL.LL.....",
         ".....LL.LL....LL.LL.....",
         ".....LL.LL....LL.LL.....",
         ".....KK.KK....KK.KK....."]
llama = S.Billboard([S.sprite_from_ascii(LLAMA, {'E': 'EARTH', 'L': 'CREAM', 'K': 'INK', 'M': 'MUTED',
                                                 'R': 'RED', 'G': 'GOLD'}, pal)], d1=72)

CLOUDS = [S.Cloud(C0 + 70 * K, C0 + 10 * K, 52 * K, 9 * K, 3, SEED + 1),
          S.Cloud(C0 - 75 * K, C0 + 30 * K, 50 * K, 8 * K, 2, SEED + 2),
          S.Cloud(C0 + 55 * K, C0 - 100 * K, 58 * K, 10 * K, 3, SEED + 3)]
DRIFT = (1.2, 0.8)

CITY = (C0, C0 - 2 * K, CITY_Z)
CUTC = ((CUT_X0 + CUT_X1) / 2, CUT_Y1, None)
cam_path = S.CameraPath([
    (0.0, dict(tx=C0, ty=C0 + 4 * K, tz=CITY_Z, dist=520, yaw=-42, pitch=9, roll=0), 'linear'),
    (4.9, dict(tx=C0, ty=C0 + 4 * K, tz=CITY_Z, dist=430, yaw=-32, pitch=11, roll=-2), 'linear'),
    (5.5, dict(tx=C0 + 6 * K, ty=C0 - 6 * K, tz=CITY_Z - 10 * K, dist=330, yaw=-22, pitch=64, roll=0), 'inOutSine'),
    (9.3, dict(tx=C0 + 8 * K, ty=C0 - 8 * K, tz=CITY_Z - 10 * K, dist=300, yaw=0, pitch=60, roll=0), 'linear'),
    (9.9, dict(tx=(CUT_X0 + CUT_X1) / 2, ty=CUT_Y1, tz=0, dist=70, yaw=-36, pitch=19, roll=0), 'inOutSine'),
    (14.6, dict(tx=(CUT_X0 + CUT_X1) / 2 - 3, ty=CUT_Y1, tz=0, dist=60, yaw=-26, pitch=17, roll=0), 'linear'),
    (15.2, dict(tx=C0 + 4 * K, ty=C0, tz=CITY_Z, dist=300, yaw=-30, pitch=20, roll=0), 'inOutSine'),
    (18.8, dict(tx=C0, ty=C0 + 6 * K, tz=CITY_Z, dist=430, yaw=-52, pitch=16, roll=0), 'linear'),
])


def cut_target_z():
    w = world()
    xi, yi = int((CUT_X0 + CUT_X1) / 2), int(CUT_Y1 + 1)
    return float(_W['top0'][yi, xi])


R = S.Renderer(pal, focal=416.0, haze_d=(700.0, 1300.0), steps=128)

CARDS = [
    (0.12, 4.9, ['MACHU PICCHU'], 20, S.CX_SAFE, 62, 'ct', {}),
    (0.12, 4.9, ['POURQUOI', 'DES ESCALIERS ?'], 15, S.CX_SAFE, 106, 'ct', {}),
    (0.12, 4.9, ['reconstitution stylisée'], 10, S.CX_SAFE, S.NH - S.SAFE_B - 2, 'cb', {}),
    (5.5, 9.3, ['XVe SIÈCLE'], 20, S.CX_SAFE, 62, 'ct', {'inverted': True, 'colors': 'GOLD'}),
    (5.6, 9.3, ['LES INCAS BÂTISSENT', 'DES TERRASSES'], 15, S.CX_SAFE, 108, 'ct', {}),
    (9.9, 14.6, ['LA PLUIE FILE,', 'LA PENTE TIENT'], 15, S.CX_SAFE, 62, 'ct', {}),
    (15.2, 18.8, ['RÉVÉLÉE AU MONDE', 'EN 1911'], 15, S.CX_SAFE, 62, 'ct', {}),
    (5.5, 18.8, ['reconstitution stylisée'], 10, S.CX_SAFE, S.NH - S.SAFE_B - 2, 'cb', {}),
]


def pins_for(t):
    zt = cut_target_z()
    xm = (CUT_X0 + CUT_X1) / 2 + 3 * K
    out = []
    if 6.2 <= t < 9.3:
        out.append((['À 2 430 m'], (C0 + 2 * K, C0 - 2 * K, CITY_Z + 0.5), (128, 300)))
    if 10.3 <= t < 14.6:
        out.append((['terre'], (xm, FACE_Y - 0.2, zt - 0.55 * K), (18, 150)))
    if 10.9 <= t < 14.6:
        out.append((['gravier'], (xm, FACE_Y - 0.2, zt - 1.6 * K), (18, 196)))
    if 11.5 <= t < 14.6:
        out.append((['pierres'], (xm, FACE_Y - 0.2, zt - 2.9 * K), (18, 242)))
    return out


FACE_Y = math.floor(CUT_Y1 - 0.5) + 1          # plan de la paroi coupée (bord de cellule)


def rain(idx, depth, cam, t):
    """Gouttes : chute, infiltration lente dans la terre et le gravier, sortie au pied du mur (pas entiers)."""
    if not (9.6 <= t < 15.0):
        return
    top0 = _W['top0']
    c = pal['SHALLOW']
    for k in range(22):
        x = CUT_X0 + 2 + (k * 5.3 % (CUT_X1 - CUT_X0 - 4))
        xi, yi = int(x), int(CUT_Y1 + 1)
        z0 = float(top0[yi, xi])
        ph = ((t - 9.6) * 0.55 + k * 0.137) % 1.0
        if ph < 0.25:                                   # chute
            z = z0 + 8 * K * (1 - ph / 0.25)
            yy = FACE_Y - 0.6
        elif ph < 0.85:                                 # infiltration : terre puis gravier puis pierres
            z = z0 - L_STONES * ((ph - 0.25) / 0.6)
            yy = FACE_Y - 0.3
        else:                                           # sortie vers l'aval, au pied du remblai
            z = z0 - L_STONES
            x = x + 3 * K * ((ph - 0.85) / 0.15)
            yy = FACE_Y - 0.3
        sx, sy, zc = cam.project(np.array([x, yy, z]))
        i, j = int(sx), int(sy)
        n = 3 if ph < 0.25 else 2                        # traînée de 3 px en l'air, goutte de 2×2 dans le sol
        if 1 <= i < S.NW and 0 <= j < S.NH - n and (depth[j, i] > zc - 3.0):
            idx[j:j + n, i] = c
            if n == 2:
                idx[j:j + 2, i - 1] = c


LLAMA_SCALE = []


def frame_idx(t, cam_override=None):
    w = world()
    p = cam_path.at(t) if cam_override is None else cam_override
    if cam_override is None and 9.3 <= t <= 15.2:
        # la cible de la coupe se pose sur le dessus des terrasses
        pass
    cam = S.Cam(p, R.focal)
    shadows = S.cloud_shadow_disks(CLOUDS, R.sun, t, DRIFT, ground_z=CITY_Z * 0.6)
    idx, depth, _ = R.ground(w, cam, t, shadows)
    lx, ly = (CUT_X0 + CUT_X1) / 2 + 6 * K, CUT_Y0 - 3.0 * K
    gz = float(_W['top0'][int(ly), int(lx)])
    llama.draw(idx, depth, cam, pal, lx, ly, gz, gz, sun=R.sun, max_scale_log=LLAMA_SCALE)
    rain(idx, depth, cam, t)
    S.draw_clouds(idx, depth, cam, pal, CLOUDS, t, DRIFT)
    if cam_override is None:
        for (t0, t1, lines, size, x, y, anc, opt) in CARDS:
            if t0 <= t < t1:
                prog = 1.0 if t0 < 0.5 else min(1.0, (t - t0) * 30 / 4)
                S.cartouche(idx, pal, lines, S.CX_SAFE if x == 135 else x, y, size=size, anchor=anc, progress=prog, **opt)
        for lines, P, (bx, by) in pins_for(t):
            gx, gy, gz2 = cam.project(np.array(P))
            if gz2 > 1:
                S.pinned_card(idx, pal, lines, bx, by, gx, gy)
    return idx


def build():
    world()
    # la cible des plans de coupe : sur la terrasse coupée
    zt = cut_target_z()
    for k in cam_path.keys:
        if abs(k[1]['tx'] - (CUT_X0 + CUT_X1) / 2) < 6 and k[1]['tz'] == 0:
            k[1]['tz'] = zt - 1.5 * K
    return S.Short(pal, DUR, frame_idx, lambda t: (S.Cam(cam_path.at(t), R.focal), world()))


def dive(outdir):
    from PIL import Image
    build()
    Path(outdir).mkdir(parents=True, exist_ok=True)
    zt = cut_target_z()
    for pitch in (90, 70, 50, 30, 15):
        p = dict(tx=C0 + 6 * K, ty=C0 - 8 * K, tz=zt, dist=200 + (pitch - 15) * 1.2, yaw=-20, pitch=pitch, roll=0)
        ind = frame_idx(12.0, cam_override=p)
        Image.fromarray(S.upscale(S.to_rgb(ind, pal))).save(Path(outdir) / f'dive_{pitch:02d}deg.jpg', quality=90)
        print(pitch, len(np.unique(ind)), 'couleurs')


if __name__ == '__main__':
    if '--dive' in sys.argv:
        dive(sys.argv[sys.argv.index('--dir') + 1])
    else:
        S.main(build, f'{CACHE}/video.mp4')
