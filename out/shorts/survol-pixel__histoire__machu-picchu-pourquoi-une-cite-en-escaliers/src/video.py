#!/usr/bin/env python3
"""
« Machu Picchu : pourquoi une cité en escaliers ? » — Survol pixel, famille histoire. RECONSTITUTION STYLISÉE.

Monde inventé d'après la disposition générale du site (aucune géométrie réelle prétendue) : une crête entre deux
sommets (au sud la montagne, au nord un pain de sucre), une cité sur l'ensellement, des terrasses agricoles étroites
à murs de pierre sur les flancs, une rivière en fer à cheval dans la vallée, des nuages bas sous la cité.
Passe A+B+C : le monde est 2,4 fois plus grand (crêtes et vallées andines jusqu'à l'horizon, seconde rivière, forêt
variée), carte de couleurs 4 fois plus fine sur la fenêtre du site, ombre portée du relief, brume en 6 paliers ;
caméra qui vole (avance, roulis dans les virages, tangage 27–40° hors coupe) ; un seul cartouche à la fois.
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
G = 1536                      # monde 2,4 fois plus large que la passe précédente (640)
C0 = G / 2
FW = 512                      # fenêtre de la carte de couleurs fine (unités), centrée sur le site
FK = 4                        # cases de couleur par cellule de hauteur dans la fenêtre
FX0 = int(C0 - FW / 2)
DH_NAT, DH_AG = 3.5 * K, 1.6 * K
CITY_Z = 72.0 * K
CUT_X0, CUT_X1 = C0 + 12 * K, C0 + 33 * K
CUT_Y0, CUT_Y1 = C0 - 27 * K, C0 - 21 * K
CUT_DEPTH = 6.0 * K
L_EARTH, L_GRAVEL, L_STONES = 1.1 * K, 2.1 * K, 3.7 * K

BIOME = {'GRANITE': '#9C968C', 'GRANITE_SH': '#5F5A55', 'THATCH': '#C9A35A', 'EARTH': '#8A5A3A', 'SNOW': '#EEF3F4',
         'FOREST_SH': '#0F3620'}   # ombre sur la forêt : vert sombre, plus de bleu nuit (retouche Fable du 18/11)
pal = S.Palette(BIOME)
pal.set_lut('shadow', {
    'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_D', 'GRASS_D': 'FOREST', 'FOREST': 'FOREST_SH', 'FOREST_SH': 'INK', 'GRANITE': 'GRANITE_SH',
    'GRANITE_SH': 'INK', 'THATCH': 'EARTH', 'EARTH': 'INK', 'OCEAN_MID': 'SH_WATER', 'SHALLOW': 'OCEAN_MID',
    'CLOUD': 'HATCH', 'HATCH': 'MUTED', 'SKY_LO': 'SKY_MID', 'SKY_MID': 'SKY_HI', 'SKY_HI': 'OCEAN_MID',
    'HAZE': 'SKY_MID', 'LAND_FAR': 'GRASS_D', 'MUTED': 'INK', 'CREAM': 'HATCH', 'FOAM': 'SHALLOW', 'SNOW': 'HATCH'})
# brume : 6 paliers par matière ; les textures se fondent au 3e palier, le dernier est HAZE (bas du ciel)
pal.set_haze({
    'GRASS_L': ['GRASS_M', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRASS_M': ['HZ_G1', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRASS_D': ['HZ_G1', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'FOREST': ['GRASS_D', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'INK': ['FOREST', 'GRASS_D', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'FOREST_SH': ['FOREST', 'GRASS_D', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRANITE': ['HZ_R1', 'HZ_R1', 'HZ_G3', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRANITE_SH': ['MUTED', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'THATCH': ['HZ_R1', 'HZ_R1', 'HZ_G3', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'EARTH': ['GRANITE_SH', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'MUTED': ['MUTED', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'OCEAN_MID': ['HZ_W1', 'HZ_W1', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SH_WATER': ['OCEAN_MID', 'HZ_W1', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SHALLOW': ['HZ_W1', 'WATER_FAR', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'FOAM': ['SHALLOW', 'WATER_FAR', 'HZ_W2', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SNOW': ['SNOW', 'SNOW', 'HZ_G4', 'HZ_G4', 'HAZE', 'HAZE'],
})

_W = {}


def gauss(xx, yy, x0, y0, sx, sy, h):
    return h * np.exp(-(((xx - x0) / sx) ** 2 + ((yy - y0) / sy) ** 2))


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def site_height(xx, yy, n1, n2):
    """Relief continu (avant quantification) : massif, rivière en fer à cheval, crêtes andines jusqu'au bord du monde."""
    mass = np.maximum.reduce([
        gauss(xx, yy, C0, C0 - 70 * K, 40 * K, 34 * K, 125 * K),        # la montagne au sud
        gauss(xx, yy, C0 + 4 * K, C0 + 60 * K, 25 * K, 21 * K, 104 * K),  # le pain de sucre au nord (cône, retouche Fable)
        gauss(xx, yy, C0, C0 - 6 * K, 36 * K, 48 * K, 76 * K),          # la crête de l'ensellement
    ]) + 7 * K * n1
    rcx, rcy, rr = C0, C0 + 12 * K, 92 * K
    rc = np.hypot(xx - rcx, yy - rcy)
    d_arc = np.where(yy > C0 - 30 * K, np.abs(rc - rr), 1e9)
    d_w = np.where(yy <= C0 - 30 * K, np.abs(xx - (rcx - math.sqrt(rr ** 2 - (42 * K) ** 2))), 1e9)
    d_e = np.where(yy <= C0 - 30 * K, np.abs(xx - (rcx + math.sqrt(rr ** 2 - (42 * K) ** 2))), 1e9)
    d_riv = np.minimum.reduce([d_arc, d_w, d_e]) + 3 * K * n2
    # crêtes andines : bruit « en arêtes » (1 − |n|) à deux échelles, vallées entre elles ; montent loin du site
    big = S.vnoise(xx, yy, 260.0, SEED + 41, 3)
    rid = 1.0 - np.abs(S.vnoise(xx, yy, 150.0, SEED + 43, 3))
    rid2 = 1.0 - np.abs(S.vnoise(xx, yy, 60.0, SEED + 47, 2))
    ridges = (55 * K + 40 * K * big) * (0.35 + 0.65 * rid ** 1.6) + 14 * K * rid2
    ring = smooth((rc - 110 * K) / (70 * K))
    outer = ridges * ring
    # le bord du monde redescend (invisible : dernier palier de brume)
    edge = np.minimum.reduce([xx, yy, G - xx, G - yy])
    outer *= 0.25 + 0.75 * smooth((edge - 20) / 160)
    Hn = np.maximum(mass, outer) * (0.12 + 0.88 * smooth((d_riv - 5 * K) / (34 * K))) + 3 * K
    river = d_riv < 5 * K
    # seconde rivière lointaine (l'Urubamba en aval, stylisée) : vallée sinueuse au nord-ouest
    s2 = (yy - C0) * 0.9 + (xx - C0) * 0.45
    meander = 60 * np.sin(s2 / 140.0) + 25 * S.vnoise(xx, yy, 90.0, SEED + 53, 2)
    d2 = np.abs((xx - C0) * 0.9 - (yy - C0) * 0.45 + 330 + meander)
    far = rc > 230 * K
    Hn = np.where(far, Hn * (0.1 + 0.9 * smooth((d2 - 6) / 70)) + 3 * K, Hn)
    river |= far & (d2 < 7)
    return Hn, river, rc


def world():
    if _W:
        return _W['w']
    yy, xx = np.mgrid[0:G, 0:G].astype(np.float32) + 0.5
    n1 = S.vnoise(xx, yy, 60.0, SEED, 3)
    n2 = S.vnoise(xx, yy, 16.0, SEED + 5, 2)
    Hn, river, rc = site_height(xx, yy, n1, n2)
    # quantification : naturelle (marches de 6) ; terrasses agricoles (marches de 2,5) ; cité (plateau)
    e = np.sqrt(((xx - C0) / (17 * K)) ** 2 + ((yy - (C0 - 2 * K)) / (27 * K)) ** 2)
    city = e < 1
    skirt = CITY_Z - (e - 1) * 10 * K
    # le pain de sucre entre dans la couronne des terrasses : au-dessus de la cité, c'est la montagne (naturelle,
    # boisée), pas des murs de terrasse ; c'étaient ces murs gris qui en faisaient une aiguille (retouche Fable)
    peak = (e >= 1) & (e < 2.2) & (Hn > skirt + 2 * K) & (yy > C0 + 20 * K)
    agz = (e >= 1) & (e < 2.2) & ~peak
    flank = CITY_Z - 12 * K - (e - 2.2) * 40 * K
    Hn = np.where(agz, np.maximum(skirt, Hn), np.where(e >= 2.2, np.maximum(flank, Hn), Hn))
    top = np.floor(Hn / DH_NAT) * DH_NAT
    top = np.where(agz, np.floor(Hn / DH_AG) * DH_AG, top)
    top = np.where(city, CITY_Z, top)
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
    snow = top > 128 * K
    # seuil de la roche nue (carte, réglable par endroit) : 100 (×K) partout. Le pain de sucre (sommet 105) n'a plus
    # que sa cime en granite : ses flancs sont boisés depuis qu'ils ne sont plus des murs de terrasse (voir peak)
    RZ = np.full((G, G), 100 * K, np.float32)
    # couleurs grossières (1 case par cellule) — hors fenêtre fine
    col = np.full((G, G), pal['GRASS_D'], np.uint8)
    lvl_n = np.floor(top / DH_NAT).astype(int)
    # forêt naturelle : deux verts en grandes plages (bruit) ; pas de bande par marche : les rayures d'une marche sur
    # deux, à 1 px au loin, scintillaient (A-B-A ≈ 8 % au survol). Retouche Fable : sol clair, FOREST réservé aux pieds
    # de marche, clairières GRASS_M en plages
    col[S.vnoise(xx, yy, 22.0, SEED + 91, 2) < -0.45] = pal['GRASS_M']
    col[(top < 10 * K)] = pal['GRASS_M']
    col[(top > RZ)] = pal['GRANITE']
    col[snow] = pal['SNOW']
    lvl_a = np.floor(top / DH_AG).astype(int)
    col[agz & (lvl_a % 2 == 0)] = pal['GRASS_L']
    col[agz & (lvl_a % 2 == 1)] = pal['GRASS_M']
    col[city] = pal['GRANITE']
    col[plaza & city] = pal['GRASS_L']
    col[bld] = pal['THATCH']
    roof_sh = bld & (((xx - C0) % (6 * K)) > 3.6 * K)
    col[roof_sh] = pal['EARTH']
    col[river] = pal['OCEAN_MID']
    col[river & (rng.random((G, G)) < 0.05)] = pal['FOAM']
    higher = np.zeros((G, G), bool)
    lower_n = np.zeros((G, G), bool)
    for sh in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        higher |= np.roll(top, sh, (0, 1)) > top + 0.1
        lower_n |= np.roll(top, sh, (0, 1)) < top - 0.1
    foot = higher & ~river & ~bld
    lip = lower_n & ~higher & agz & ~river
    col[lip] = pal['GRASS_L']
    col[foot & agz] = pal['GRASS_D']
    col[foot & ~agz & ~city & (top <= RZ)] = pal['FOREST']
    col[foot & (top > RZ)] = pal['GRANITE_SH']
    col[foot & city & ~plaza] = pal['GRANITE_SH']
    # contremarches naturelles : éclairée GRASS_M, ombrée GRASS_D (un ton d'écart gardé ; GRASS_D / FOREST avant la
    # retouche Fable : la forêt faisait 22 % de pixels sombres contre 3–6 % dans la source)
    fl = np.full((G, G), pal['GRASS_M'], np.uint8)
    fd = np.full((G, G), pal['GRASS_D'], np.uint8)
    stone = agz | city | bld | (top > RZ)
    fl[stone] = pal['GRANITE']
    fd[stone] = pal['GRANITE_SH']
    fl[snow] = pal['GRANITE']
    cut = (xx > CUT_X0) & (xx < CUT_X1) & (yy > CUT_Y0) & (yy < CUT_Y1)
    top0 = top.copy()
    top = np.where(cut, top - CUT_DEPTH, top)
    col[cut] = pal['GRANITE_SH']
    wild = ~agz & ~city & ~river & ~cut & (top > 6 * K) & (top < RZ) & ((e > 2.3) | peak)
    # ---- carte fine (FK cases par cellule) sur la fenêtre du site : textures organiques, houppiers semés
    fine = fine_colours(top, top0, col, agz, city, plaza, bld, river, wild, cut, RZ)
    shade = S.relief_shade(top, (0.30, -0.62), reach=60, slope=1.0 / math.hypot(0.30, 0.62))
    shade &= ~river & ~cut
    w = S.World(top, col, fl, fd, cut=cut, section=section_fn(top0), outside=pal['GRASS_D'], zmin=-1.0,
                outside_tile=outside_tile(), cut_top0=top0, coursed=stone & ~(top > RZ),
                fine=(FX0, FX0, FK, fine), shade=shade)
    trees = S.scatter_trees(wild & (np.abs(xx - C0) < FW / 2 - 4) & (np.abs(yy - C0) < FW / 2 - 4), top, SEED + 31,
                            density=0.5, r=(0.9, 2.2), cluster=(n2 - 0.02) * 3.2)
    _W.update(w=w, top0=top0, agz=agz, trees=trees)
    return w


def fine_colours(top, top0, col, agz, city, plaza, bld, river, wild, cut, RZ):
    """Carte de couleurs FK fois plus fine sur la fenêtre [FX0, FX0 + FW)² : lignes de pied et de rebord fines,
    parcelles organiques sur les terrasses, houppiers semés (même teinte que les arbres dessinés), strates de roche."""
    sl = slice(FX0, FX0 + FW)
    up = lambda a: np.repeat(np.repeat(a[sl, sl], FK, 0), FK, 1)
    n = FW * FK
    fy, fx = np.mgrid[0:n, 0:n].astype(np.float32)
    X = FX0 + (fx + 0.5) / FK
    Y = FX0 + (fy + 0.5) / FK
    c = up(col)
    t = up(top)
    A, CI, PL, B, RV, WI, CU = (up(m) for m in (agz, city, plaza, bld, river, wild, cut))
    rz = up(RZ)
    # pied (trait sombre) et rebord (trait clair) : seulement la bande de 2 cases fines contre la marche voisine
    hi = np.zeros((n, n), bool)
    lo = np.zeros((n, n), bool)
    for sh in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        hi |= np.roll(t, sh, (0, 1)) > t + 0.1
        lo |= np.roll(t, sh, (0, 1)) < t - 0.1
    base = c.copy()
    # surfaces : on repart des matières, sans les lignes grossières (refaites plus fines ci-dessous)
    lvl_a = np.floor(t / DH_AG).astype(int)
    lvl_n = np.floor(t / DH_NAT).astype(int)
    nA = S.vnoise(X, Y, 3.0, SEED + 61, 2)
    nB = S.vnoise(X, Y, 1.2, SEED + 67, 1)
    nat = ~A & ~CI & ~RV & ~CU & (t <= rz)
    # retouche Fable : hors forêt semée aussi, FOREST seulement aux pieds de marche (plus de plages sombres)
    base[nat] = np.where(S.vnoise(X[nat], Y[nat], 22.0, SEED + 91, 2) < -0.45, pal['GRASS_M'], pal['GRASS_D'])
    base[nat & (t < 10 * K)] = pal['GRASS_M']
    # parcelles de culture sur les terrasses : deux verts en plages organiques, rangées le long de la marche
    terr = A & ~RV & ~CU
    base[terr] = np.where((lvl_a[terr] % 2 == 0) ^ (nA[terr] > 0.35), pal['GRASS_L'], pal['GRASS_M'])
    # forêt variée : houppiers semés (boules de 2–3 cases fines) en trois verts, clairière de-ci de-là
    fo = WI & (t > 6 * K)
    blob = (nB > 0.15)
    # retouche Fable : sol clair (GRASS_D), clairières GRASS_M plus fréquentes, sous-bois FOREST par grandes plages
    base[fo] = pal['GRASS_D']
    base[fo & blob & (nA > 0.25)] = pal['GRASS_M']
    base[fo & (S.vnoise(X, Y, 9.0, SEED + 71, 2) > 0.40)] = pal['GRASS_M']
    base[fo & (S.vnoise(X, Y, 14.0, SEED + 73, 2) < -0.35)] = pal['FOREST']
    # roche : granite à strates sombres irrégulières
    rk = (t > rz) & ~CU
    base[rk] = np.where(np.sin(t[rk] * 0.9 + 3 * nA[rk]) > 0.55, pal['GRANITE_SH'], pal['GRANITE'])
    base[rk & (t > 128 * K)] = pal['SNOW']
    # cité : dalles de granite moucheté, place verte, toits (repris de la carte grossière)
    base[CI] = np.where(nB[CI] > 0.55, pal['GRANITE_SH'], pal['GRANITE'])
    base[PL & CI] = pal['GRASS_L']
    base[B] = c[B]
    # rivière : courant à bandes et écume semée (hachage fixe, non périodique)
    rvf = RV
    base[rvf] = np.where(nA[rvf] > 0.2, pal['SHALLOW'], pal['OCEAN_MID'])
    base[rvf & (S.hash01(fx.astype(np.int64), fy.astype(np.int64), 3) < 0.04)] = pal['FOAM']
    # lignes fines
    foot = hi & ~RV & ~B
    lip = lo & ~hi & A & ~RV
    base[lip] = pal['GRASS_L']
    base[foot & A] = pal['GRASS_D']
    base[foot & ~A & ~CI & (t <= rz)] = pal['FOREST']
    base[foot & (t > rz)] = pal['GRANITE_SH']
    base[foot & CI & ~PL] = pal['GRANITE_SH']
    base[CU] = pal['GRANITE_SH']
    return base


def section_fn(top0):
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
    return section


def outside_tile():
    """Au-delà du monde (toujours dans les derniers paliers de brume) : forêt de fond texturée, non uniforme."""
    n = 128
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    v = S.vnoise(xx, yy, 11.0, SEED + 81, 2)
    t = np.full((n, n), pal['GRASS_D'], np.uint8)
    t[v > 0.2] = pal['FOREST']
    t[v < -0.35] = pal['GRASS_M']
    return t


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

DRIFT = (1.2, 0.8)
CLOUD_Z = 50 * K               # nuages bas, sous la cité (forêt de nuage), une seule altitude


def _clouds():
    """Tas de coton à une seule altitude, autour du site et jusqu'au loin dans les vallées ; jamais traversés par la
    caméra (≥ 45 unités + rayon sur tout le short)."""
    rng = np.random.default_rng(SEED + 23)
    ts = np.arange(0.0, DUR + 0.01, 0.2)
    cams = np.array([S.Cam(cam_path.at(float(t)), 416.0).pos for t in ts])
    out = []
    tries = 0
    while len(out) < 60 and tries < 12000:
        tries += 1
        far = len(out) >= 24
        span = 380 if far else 150
        x, y = C0 + rng.uniform(-span, span) * K, C0 + rng.uniform(-span, span * 0.9) * K
        if not (40 < x < G - 40 and 40 < y < G - 40):
            continue
        R_ = float(rng.uniform(9.0, 16.0)) * K
        if math.hypot(x - C0, y - C0) < 45 * K or any(math.hypot(x - c.x, y - c.y) < 30 * K for c in out):
            continue
        P = np.stack([x + DRIFT[0] * ts, y + DRIFT[1] * ts, np.full_like(ts, CLOUD_Z)], 1)
        if np.linalg.norm(P - cams, axis=1).min() < 45 + R_:
            continue
        out.append(S.Cloud(x, y, CLOUD_Z, R_, int(rng.integers(2, 5)), SEED + 100 + len(out)))
    return out


CITY = (C0, C0 - 2 * K, CITY_Z)
CUTX = (CUT_X0 + CUT_X1) / 2
# vol : approche par la vallée (avance + virage à gauche), survol des terrasses en virage, piqué lent vers la coupe,
# plan de coupe lent (lisible), remontée et départ en virage au-dessus des crêtes. Piqué (8,0 → 10,0 s) et remontée
# (13,4 → 15,6 s) ralentis d'environ 40 % (décision du 18/11) : le relief lointain scintillait sous la caméra rapide
cam_path = S.CameraPath([
    (0.0, dict(tx=C0 + 40, ty=C0 + 70, tz=CITY_Z - 30, dist=470, yaw=-50, pitch=29, roll=-11), 'linear'),
    (2.6, dict(tx=C0 + 14, ty=C0 + 26, tz=CITY_Z - 14, dist=400, yaw=-40, pitch=29, roll=-9), 'linear'),
    (5.0, dict(tx=C0 + 2, ty=C0 - 2, tz=CITY_Z - 4, dist=330, yaw=-46, pitch=33, roll=3), 'linear'),
    (7.0, dict(tx=C0 - 2, ty=C0 - 4, tz=CITY_Z - 8 * K, dist=290, yaw=-72, pitch=38, roll=9), 'linear'),
    (8.0, dict(tx=C0 + 4 * K, ty=C0 - 10 * K, tz=CITY_Z - 14 * K, dist=250, yaw=-96, pitch=36, roll=11), 'linear'),
    (10.0, dict(tx=CUTX, ty=CUT_Y1, tz=0, dist=72, yaw=-30, pitch=20, roll=0), 'linear'),
    (13.4, dict(tx=CUTX - 3, ty=CUT_Y1, tz=0, dist=62, yaw=-22, pitch=19, roll=0), 'linear'),
    (15.6, dict(tx=C0 + 4 * K, ty=C0, tz=CITY_Z, dist=300, yaw=-34, pitch=30, roll=-8), 'linear'),
    (18.8, dict(tx=C0 - 30, ty=C0 + 50, tz=CITY_Z - 20, dist=390, yaw=-66, pitch=28, roll=-13), 'linear'),
], smooth=True)

CLOUDS = []


def cut_target_z():
    world()
    xi, yi = int((CUT_X0 + CUT_X1) / 2), int(CUT_Y1 + 1)
    return float(_W['top0'][yi, xi])


R = S.Renderer(pal, focal=416.0, course=0.9 * K, wall_speck=0.3,
               sky=[(0.4, 'HAZE'), (1.2, 'SKY_1'), (2.4, 'SKY_LO'), (4.0, 'SKY_2'), (6.5, 'SKY_MID'), (10.0, 'SKY_4'), (90.0, 'SKY_HI')])   # rampe du ciel resserrée (retouche Fable)

# un seul cartouche à la fois, calé sur les lignes de narration.json (mots repérés par silencedetect) :
# (t0, t1, lignes, taille, x, y, ancre, options)
CARDS = [
    (0.12, 1.5, ['MACHU PICCHU'], 15, S.CX_SAFE, 62, 'ct', {}),
    (3.4, 5.1, ['POURQUOI', 'DES ESCALIERS ?'], 15, S.CX_SAFE, 62, 'ct', {}),
    (5.6, 7.05, ['XVe SIÈCLE'], 15, S.CX_SAFE, 62, 'ct', {'inverted': True, 'colors': 'GOLD'}),
    (7.05, 8.9, ['LES INCAS BÂTISSENT', 'DES TERRASSES'], 15, S.CX_SAFE, 62, 'ct', {}),
    (12.0, 13.9, ['LA PLUIE FILE,', 'LA PENTE TIENT'], 15, S.CX_SAFE, 62, 'ct', {}),
    (15.1, 16.9, ['RÉVÉLÉE AU MONDE', 'EN 1911'], 15, S.CX_SAFE, 62, 'ct', {}),
    (16.9, 18.8, ['reconstitution stylisée'], 10, S.CX_SAFE, S.NH - S.SAFE_B - 2, 'cb', {}),
]


def pins_for(t):
    zt = cut_target_z()
    xm = (CUT_X0 + CUT_X1) / 2 + 3 * K
    out = []
    if 1.5 <= t < 3.4:
        out.append((['À 2 430 m'], (C0 + 2 * K, C0 - 2 * K, CITY_Z + 0.5), (128, 300)))
    # l'ordre de la voix : « Pierres, gravier, terre »
    if 10.0 <= t < 10.74:
        out.append((['pierres'], (xm, FACE_Y - 0.2, zt - 2.9 * K), (18, 242)))
    if 10.74 <= t < 11.48:
        out.append((['gravier'], (xm, FACE_Y - 0.2, zt - 1.6 * K), (18, 196)))
    if 11.48 <= t < 12.0:
        out.append((['terre'], (xm, FACE_Y - 0.2, zt - 0.55 * K), (18, 150)))
    return out


FACE_Y = math.floor(CUT_Y1 - 0.5) + 1


def rain(idx, depth, cam, t):
    if not (9.6 <= t < 15.0):
        return
    top0 = _W['top0']
    c = pal['SHALLOW']
    for k in range(22):
        x = CUT_X0 + 2 + (k * 5.3 % (CUT_X1 - CUT_X0 - 4))
        xi, yi = int(x), int(CUT_Y1 + 1)
        z0 = float(top0[yi, xi])
        ph = ((t - 9.6) * 0.55 + k * 0.137) % 1.0
        if ph < 0.25:
            z = z0 + 8 * K * (1 - ph / 0.25)
            yy = FACE_Y - 0.6
        elif ph < 0.85:
            z = z0 - L_STONES * ((ph - 0.25) / 0.6)
            yy = FACE_Y - 0.3
        else:
            z = z0 - L_STONES
            x = x + 3 * K * ((ph - 0.85) / 0.15)
            yy = FACE_Y - 0.3
        sx, sy, zc = cam.project(np.array([x, yy, z]))
        i, j = int(sx), int(sy)
        n = 3 if ph < 0.25 else 2
        if 1 <= i < S.NW and 0 <= j < S.NH - n and (depth[j, i] > zc - 3.0):
            idx[j:j + n, i] = c
            if n == 2:
                idx[j:j + 2, i - 1] = c


LLAMA_SCALE = []
LAST = {}


def haze_ref(p):
    """Distance de référence de la brume : la distance de la caméra, bornée en bas (280) pour que les plans
    rapprochés (coupe) et les piqués ne fassent pas glisser tous les paliers d'un coup."""
    return max(p['dist'], 280.0)


def frame_idx(t, cam_override=None, cards=True):
    w = world()
    p = cam_path.at(t) if cam_override is None else cam_override
    cam = S.Cam(p, R.focal)
    disks = S.cloud_shadow_disks(CLOUDS, R.sun, t, DRIFT, ground_z=CITY_Z * 0.6)
    shadow = S.disk_mask(disks, 0.0, 0.0, G, G, 1.0)
    idx, depth, hit = R.ground(w, cam, t, shadow, haze_ref=haze_ref(p))
    LAST['hit'] = hit
    lx, ly = (CUT_X0 + CUT_X1) / 2 + 6 * K, CUT_Y0 - 3.0 * K
    gz = float(_W['top0'][int(ly), int(lx)])
    S.draw_trees(idx, depth, cam, pal, _W['trees'], R.sun, haze=(haze_ref(p), R.haze_k, R.haze_jit))
    llama.draw(idx, depth, cam, pal, lx, ly, gz, gz, sun=R.sun, max_scale_log=LLAMA_SCALE)
    rain(idx, depth, cam, t)
    S.draw_clouds(idx, depth, cam, pal, CLOUDS, t, DRIFT)
    LAST['clean'] = idx.copy()
    if cam_override is None and cards:
        for (t0, t1, lines, size, x, y, anc, opt) in CARDS:
            if t0 <= t < t1:
                prog = 1.0 if t0 < 0.5 else min(1.0, (t - t0) * 30 / 4)
                S.cartouche(idx, pal, lines, x, y, size=size, anchor=anc, progress=prog, **opt)
        for lines, P, (bx, by) in pins_for(t):
            gx, gy, gz2 = cam.project(np.array(P))
            if gz2 > 1:
                S.pinned_card(idx, pal, lines, bx, by, gx, gy)
    return idx


def build():
    world()
    zt = cut_target_z()
    for k in cam_path.keys:
        if abs(k[1]['tx'] - CUTX) < 6 and k[1]['tz'] == 0:
            k[1]['tz'] = zt - 1.5 * K
    if hasattr(cam_path, '_pchip'):
        del cam_path._pchip
    if not CLOUDS:
        CLOUDS[:] = _clouds()
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
