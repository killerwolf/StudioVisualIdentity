"""
plans.py — les trois plans de ville (Paris, New York, Tokyo), INVENTÉS et seulement évocateurs.

Chaque plan est une fonction (v, graine, P) -> spec, où v est le module villes (outils de tracé) et P la palette.
Unités : 1 unité ≈ 8 m ; le monde fait 896 × 1150 unités ; y = nord. Aucune donnée géographique : les tracés sont
écrits à la main (quelques lignes brisées) et le reste sort de bruits et de hachages à graine.
"""
import math

import numpy as np


def _tools(v):
    bx = v.Boxes()
    zs = np.zeros((v.WX, v.WY), np.float32)

    def sbox(x0, x1, y0, y1, z0, z1, f):
        bx.add(x0, x1, y0, y1, z0, z1, *f)
        i0, i1, j0, j1 = int(math.floor(x0)), int(math.ceil(x1)), int(math.floor(y0)), int(math.ceil(y1))
        zs[i0:i1, j0:j1] = np.maximum(zs[i0:i1, j0:j1], z1)

    return bx, zs, sbox


def _blocks(v, n):
    return v.mq.hash2(v.NX // 2 + 1, v.NY // 2 + 1, n).repeat(2, 0).repeat(2, 1)[:v.NX, :v.NY]


# =================================================================== PARIS
PARIS_COLS = {
    'PS1': '#BDB8AE', 'PS2': '#ACA79E', 'PSW': '#D9D2C2', 'SE1': '#3E7F9C', 'SE2': '#62A2BA',
    'Z1': '#B3BFD3', 'Z2': '#93A2BD', 'Z3': '#7483A1', 'Z4': '#56617C', 'ZL': '#E6E0CF', 'CH': '#C96A3C',
    'PW1': '#F3E7CB', 'PW2': '#DDCDA9', 'PW3': '#A8977A', 'PWW': '#70675A', 'CY1': '#7B7F72', 'CY2': '#666C60',
    'Q1': '#DDD4C0', 'Q2': '#CBC1AA', 'E1': '#B78F62', 'E2': '#8B6846', 'E3': '#59412E',
    'D1': '#F4CB48', 'D2': '#C99A2E', 'M1': '#6E6772', 'M2': '#504B59', 'M3': '#38343F', 'MW': '#8D8A97',
}


def paris(v, seed, P):
    """Vue vers le nord : une étoile et son arc au premier plan, le fleuve en travers avec son île, la tour en treillis
    sur l'autre rive. Plan inventé."""
    rng = np.random.default_rng(seed)
    X, Y, hi, r01, pk = v.XX, v.YY, v.hi, v.r01, v.pk
    bx, zs, sbox = _tools(v)
    hb = _blocks(v, 31)
    # le fleuve, en courbes, avec une île ; quais, ponts
    RIV = [(-40, 430), (120, 470), (250, 505), (360, 480), (470, 470), (590, 500), (720, 480), (940, 430)]
    ISL = ((374, 478), (440, 472))
    dr = v.poly(RIV)
    d_isl = v.seg(*ISL)
    hw = 14.5 + 7.0 * np.exp(-((X - 407) / 48.0) ** 2)
    island = d_isl < 6.5
    water = (dr < hw) & ~island
    wdepth = np.minimum(hw - dr, np.where(island, 0, d_isl - 6.5))
    quay = (dr < hw + 3.5) & ~water & ~island
    pl, pr_ = v.along(RIV, 43.0, 27.0), v.along(RIV, 43.0, -27.0)
    bridge = np.zeros(X.shape, bool)
    for a, b in zip(pl, pr_):
        if 60 < a[0] < 850:
            bridge |= v.seg(a, b) < 2.4
    bridge &= (dr < hw + 3.5)
    # places en étoile et avenues plantées
    E, C = (392.0, 362.0), (548.0, 450.0)
    d_av = v.seg(E, C) - 1.2
    star_rays = []
    for k in range(12):
        a = math.radians(15 + 30 * k)
        ray = [E, (E[0] + 230 * math.cos(a), E[1] + 230 * math.sin(a))]
        d_av = np.minimum(d_av, v.seg(*ray) - 0.8)
        star_rays.append(ray)
    stars = [(640, 300, 6, 160), (180, 330, 6, 150), (560, 640, 5, 150), (300, 760, 6, 160), (640, 800, 6, 170),
             (150, 640, 5, 140), (760, 560, 6, 150), (470, 900, 5, 140), (800, 180, 5, 140)]
    plaza = (np.hypot(X - E[0], Y - E[1]) < 16) | (np.hypot(X - C[0], Y - C[1]) < 11)
    for (cx, cy, nr, ln) in stars:
        a0 = rng.uniform(0, 2 * math.pi)
        for k in range(nr):
            a = a0 + 2 * math.pi * k / nr
            d_av = np.minimum(d_av, v.seg((cx, cy), (cx + ln * math.cos(a), cy + ln * math.sin(a))))
        plaza |= np.hypot(X - cx, Y - cy) < 7.5
    ring = [(450 + 250 * math.cos(t), 480 + 200 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 25)]
    d_ring = v.poly(ring)
    avenue = (d_av < 2.2) | (d_ring < 2.6)
    # îlots : une trame par quartier, 14 × 12 unités, ANGLES COUPÉS ; cours intérieures
    u, w_, did = v.districts(rng, 150.0, 8)
    fu, fv = (u % 14.0) - 1.5, (w_ % 12.0) - 1.5
    street = (fu < 0) | (fv < 0)
    cut = (np.minimum(fu, 12.5 - fu) + np.minimum(fv, 10.5 - fv)) < 1.9
    ph = hi(np.floor(u / 3.5) + (did % 997).astype(np.int64) * 7919, np.floor(w_ / 6.0), 5)
    # jardins
    T = (322.0, 526.0)
    mars = v.seg(T, (300, 625)) < 7.5
    tuil = v.seg((562, 458), (650, 470)) < 8.0
    DOME = (428.0, 562.0)
    inval = v.seg((426, 500), (428, 548)) < 6.0
    lux = ((X - 520) / 22.0) ** 2 + ((Y - 600) / 17.0) ** 2 < 1
    bois = (X < 110 + 30 * np.sin(Y / 70.0)) & (Y < 420)
    troc = np.hypot(X - 330, Y - 466) < 10
    park = (mars | tuil | inval | lux | bois | troc | (np.hypot(X - T[0], Y - T[1]) < 12)) & ~water & ~quay
    palace = (v.seg((662, 472), (716, 466)) < 2.6) | (v.seg((716, 466), (718, 452)) < 2.2)       # un long palais en équerre
    bld = ~(water | quay | bridge | plaza | avenue | street | cut | park | island) | (palace & ~water)
    bld &= ~(np.hypot(X - DOME[0], Y - DOME[1]) < 9) & ~(np.hypot(X - 470, Y - 660) < 6)
    isl_bld = island & (d_isl < 4.6) & (X < 420) & (((X - 374) % 9.0) > 1.4)                      # quelques îlots sur l'île
    bld |= isl_bld
    bc = v.cells_all(bld)
    court = v.up(v.erode(bc, 4)) & ~palace
    bld &= ~court
    H = (2.5 + 0.75 * r01(ph)).astype(np.float32)
    H[palace] = 3.6
    roof = (r01(ph, 12) < 0.14).astype(np.uint8)
    kind = np.zeros(X.shape, np.uint8)
    kind[bridge | quay] = 1
    # arbres : alignements des avenues, des quais et des jardins
    tr = [v.row_trees(rng, [E, C], 2.3, o) for o in (-3.0, 3.0)]
    for ray in star_rays:
        p0 = (ray[0][0] + 0.08 * (ray[1][0] - ray[0][0]), ray[0][1] + 0.08 * (ray[1][1] - ray[0][1]))
        tr += [v.row_trees(rng, [p0, ray[1]], 2.6, o, 0.85) for o in (-2.3, 2.3)]
    tr += [v.row_trees(rng, ring, 2.6, o, 0.85) for o in (-1.9, 1.9)]
    tr += [v.row_trees(rng, RIV, 2.5, o, 0.9) for o in (-17.0, 17.0)]
    tr.append(v.park_trees(rng, bois, 0.85))
    tr.append(v.park_trees(rng, (mars & (v.seg(T, (300, 625)) > 4.6)) | (tuil & (((X + Y) % 9.0) < 5.5)) | lux | troc
                           | (inval & (v.seg((426, 500), (428, 548)) > 3.8)) | (island & (X > 446)), 0.75, step=2.4, size=(0.8, 1.15)))
    trees = np.concatenate(tr)
    ti, tj = np.clip((trees[:, 0] * 2).astype(int), 0, v.NX - 1), np.clip((trees[:, 1] * 2).astype(int), 0, v.NY - 1)
    trees = trees[~water[ti, tj] & ~bridge[ti, tj] & ~bld[ti, tj]]
    # repères, en volumes stylisés
    v.lattice_tower(bx, zs, P, T[0], T[1], 41.0, 7.8, ('E1', 'E2', 'E3'))
    cream = v.faces(P, 'PW1', 'PW2', 'PW3', top='Z1', alt='PWW', mode=3)
    stone = v.faces(P, 'PW1', 'PW2', 'PW3', top='PW1')
    for dx in (-4.2, 1.7):                                            # l'arc au centre de l'étoile : deux piles, un linteau
        sbox(E[0] + dx, E[0] + dx + 2.5, E[1] - 2.3, E[1] + 2.3, 0, 6.0, stone)
    sbox(E[0] - 4.2, E[0] + 4.2, E[1] - 2.3, E[1] + 2.3, 6.0, 9.2, stone)
    sbox(E[0] - 3.4, E[0] + 3.4, E[1] - 1.7, E[1] + 1.7, 9.2, 9.9, stone)
    sbox(DOME[0] - 5, DOME[0] + 5, DOME[1] - 3, DOME[1] + 5, 0, 3.0, cream)          # un hôtel à dôme doré
    gold = (pk(P['D1']), (pk(P['D1']), pk(P['D1'], P['D2'], 1), pk(P['D2'])))
    prisms = [(DOME[0], DOME[1], 3.0, 3.0, 5.6, pk(P['PW1']), (pk(P['PW1']), pk(P['PW2']), pk(P['PW3']))),
              (DOME[0], DOME[1], 2.7, 5.6, 7.8) + gold, (DOME[0], DOME[1], 1.9, 7.8, 9.4) + gold, (DOME[0], DOME[1], 0.6, 9.4, 12.0) + gold]
    zs[int(DOME[0]) - 3:int(DOME[0]) + 3, int(DOME[1]) - 3:int(DOME[1]) + 3] = 9.5
    dark = v.faces(P, 'M1', 'M2', 'M3', top='M2', alt='MW', mode=3)
    sbox(467.6, 472.4, 658.2, 661.8, 0, 26.0, dark)                      # une tour sombre isolée
    nd = v.faces(P, 'PW1', 'PW2', 'PW3', top='Z2')
    sbox(424, 441, 470.2, 474.6, 0, 4.8, nd)                             # cathédrale sur l'île : nef, transept, deux tours, flèche
    sbox(430.5, 433.5, 468.0, 476.8, 0, 4.8, nd)
    sbox(421.2, 424, 469.2, 471.8, 0, 8.6, stone)
    sbox(421.2, 424, 473.0, 475.6, 0, 8.6, stone)
    sbox(431.6, 432.4, 472.0, 472.8, 4.8, 12.0, v.faces(P, 'Z3', 'Z3', 'Z4'))
    return {
        'water': water, 'wdepth': wdepth, 'park': park, 'bld': bld, 'H': H, 'kind': kind, 'roof': roof, 'ph': ph,
        'ground': {'street': ('PS1', 'PS2'), 'walk': 'PSW', 'water': ('SE1', 'SE2'), 'wscale': 9.0, 'edge_lit': 'Z1', 'edge_dark': 'Z4'},
        'paved': [(court, 'CY1', 'CY2'), (quay | plaza | (island & ~bld), 'Q1', 'Q2')],
        'over': [(bridge, 'Q1')],
        'lines': [(park & (hb < 0.06) & ~bois, 'S1')],
        'raised': [(v.cells_all(bridge), 1.0), (v.cells_all(quay), 0.5)],
        'roofs': [('Z2', 'Z1'), ('Z3', 'Z2')],
        'specks': [('Z2', 'CH', 0.025), ('Z1', 'CH', 0.025), ('Z3', 'CH', 0.025)],
        'kinds': [('PW1', 'PW2', 'PW3', 'PWW'), ('Q1', 'Q2', 'PW3', None)],
        'trees': trees, 'boxes': bx, 'prisms': prisms, 'zshadow': zs, 'strokes': 9000,
        'clouds': (34.0, 42.0, 120, 3.2, 5.4), 'cloud_gap': 68,
        'fog': (250.0, 40.0, 100.0), 'wall_k': 2.3,
        'camera': {'start': (394.0, 196.0), 'yaw': (4.0, -7.0), 'speed': 27.0, 'z': (80.0, 68.0), 'pitch': (-29.0, -24.0)},
    }


# =================================================================== NEW YORK
NY_COLS = {
    'NS1': '#52555F', 'NS2': '#5E616B', 'NSW': '#8F9198', 'PIER': '#A39C90',
    'RT1': '#5E6169', 'RT2': '#70737B', 'RB1': '#7B6658', 'RB2': '#8D786A', 'RL1': '#B9A78E', 'RL2': '#CBBBA4',
    'RG1': '#A6A9AF', 'RG2': '#BABDC2', 'RE1': '#D9DBDE', 'RE2': '#3B3D46', 'TANK': '#7A5236', 'AC': '#E4E5E2',
    'BR1': '#B26A4E', 'BR2': '#93523C', 'BR3': '#6A3A2D', 'BRW': '#3F2B28',
    'ST1': '#D8C7A6', 'ST2': '#B9A684', 'ST3': '#85755D', 'STW': '#5A5145',
    'GS1': '#C3C6CC', 'GS2': '#A0A4AC', 'GS3': '#70747E', 'GSW': '#4B4F5A',
    'GL1': '#8EC3E8', 'GL2': '#5C97CC', 'GL3': '#35669F', 'GLW': '#274C7C',
    'TAXI': '#F3C22E', 'SV1': '#E3E8EE', 'SV2': '#B4BECB', 'SV3': '#7D8898',
}


def newyork(v, seed, P):
    rng = np.random.default_rng(seed)
    X, Y, hi, r01, pk = v.XX, v.YY, v.hi, v.r01, v.pk
    bx, zs, sbox = _tools(v)
    hb, hb2 = _blocks(v, 31), _blocks(v, 32)
    s = np.clip((Y - 30.0) / 190.0, 0, 1)
    s = s * s * (3 - 2 * s)
    xw = 365.0 + (1 - s) * 72.0 + 5.0 * np.sin(Y / 80.0)
    xe = 537.0 - (1 - s) * 70.0 + 6.0 * np.sin(Y / 110.0 + 1.0)
    island = (X > xw) & (X < xe) & (Y > 30)
    xnj = 240.0 + 8.0 * np.sin(Y / 95.0)
    xbk = 640.0 + 10.0 * np.sin(Y / 130.0 + 2.0) - 30.0 * np.clip((120 - Y) / 120.0, 0, 1)
    nj, bk = X < xnj, X > xbk
    pier = (X > xw - 13.0 - 9.0 * r01(hi(np.floor(Y / 14.0), np.floor(Y / 14.0), 2))) & (X <= xw) & ((Y % 14.0) < 4.6) & (Y > 120) & (Y < 520)
    bridges = ((np.abs(Y - 330) < 2.8) | (np.abs(Y - 430) < 2.8)) & (X > xe - 12) & (X < xbk + 12)
    water = ~(island | nj | bk | pier)
    wdepth = np.where(X < 450, np.minimum(X - xnj, xw - X), np.minimum(X - xe, xbk - X))
    wdepth = np.where(Y < 30, 12.0, np.clip(wdepth, 0, 40)).astype(np.float32)
    # quadrillage : avenues dans le sens de l'île, rues en travers, une diagonale
    fu = (X - 369.0) % 24.0
    fv = (Y - 40.0) % 10.0
    bi, bj = np.floor((X - 369.0) / 24.0), np.floor((Y - 40.0) / 10.0)
    avenue = fu < 4.0
    street = (fv < 1.6) | (((Y - 40.0) % 100.0) < 3.2) | (v.seg((520, 60), (385, 900)) < 1.7)
    park = (X > 397) & (X < 489) & (Y > 521.6) & (Y < 960) & island
    # parcelles : 4 par îlot en largeur, 2 dos à dos ; dans les quartiers de tours, des demi-îlots
    fu2, fv2 = fu - 4.0, fv - 1.6
    ph_low = hi(bi * 4 + np.floor(fu2 / 5.0), bj * 2 + np.floor(fv2 / 4.2), 7)
    F = (np.exp(-(((X - 450) / 90.0) ** 2 + ((Y - 400) / 95.0) ** 2))
         + 0.95 * np.exp(-(((X - 450) / 60.0) ** 2 + ((Y - 150) / 75.0) ** 2))).astype(np.float32)
    ph_t = hi(bi * 2 + np.floor(fu2 / 10.0), bj, 9)
    tower = (r01(ph_t) < 0.8 * F ** 1.1) & island
    Ht = 9.0 + 40.0 * F * (0.3 + 0.7 * r01(ph_t, 12))
    inset = np.minimum(np.minimum(fu2 % 10.0, 10.0 - fu2 % 10.0), np.minimum(fv2, 8.4 - fv2))
    stepped = r01(ph_t, 4) < 0.6
    tier = np.where(stepped & (inset < 1.1), 0.5, np.where(stepped & (inset < 2.3), 0.78, 1.0))
    H = np.where(tower, Ht * tier, 1.6 + 2.8 * r01(ph_low) + 5.0 * F * r01(ph_low, 12)).astype(np.float32)
    ph = np.where(tower, ph_t, ph_low)
    # rives d'en face : tissu bas, quelques tours au bord de l'eau
    u, w_, did = v.districts(rng, 170.0, 6)
    far = nj | bk
    street_f = ((u % 14.0) < 1.5) | ((w_ % 9.0) < 1.5)
    ph_f = hi(np.floor(u / 3.5), np.floor(w_ / 4.5), 11)
    Hf = 1.3 + 1.8 * r01(ph_f) + np.where((r01(ph_f, 12) < 0.10) & ((xnj - X < 26) | (X - xbk < 26)), 6 + 12 * r01(ph_f, 4), 0)
    H = np.where(far, Hf, H).astype(np.float32)
    ph = np.where(far, ph_f, ph)
    bld = (island & ~avenue & ~street & ~park) | (far & ~street_f)
    kind = np.where(tower, np.array([0, 1, 2, 2, 1, 3, 0, 1], np.uint8)[(r01(ph, 16) * 8).astype(int)],
                    np.array([0, 0, 0, 1, 1, 2, 0, 2], np.uint8)[(r01(ph, 16) * 8).astype(int)]).astype(np.uint8)
    kind[far & (Hf < 5)] = np.array([0, 1, 2, 0], np.uint8)[(r01(ph_f, 16) * 4).astype(int)][far & (Hf < 5)]
    kind[far & (Hf >= 5)] = np.array([2, 3, 1, 2], np.uint8)[(r01(ph_f, 16) * 4).astype(int)][far & (Hf >= 5)]
    kind[pier | bridges] = 5
    roof = np.where(tower, 3, (r01(ph, 20) * 3).astype(int)).astype(np.uint8)
    # le grand parc : réservoir, lac, pelouse, allées
    resv = ((X - 443) / 30.0) ** 2 + ((Y - 790) / 42.0) ** 2 < 1
    lake = ((X - 430) / 18.0) ** 2 + ((Y - 606) / 11.0) ** 2 + 0.6 * (v.noise(14, rng) - 0.5) < 1
    lawn = ((X - 445) / 24.0) ** 2 + ((Y - 700) / 22.0) ** 2 < 1
    pwater = (resv | lake) & park
    water = water | pwater
    wdepth = np.where(pwater, 6.0, wdepth).astype(np.float32)
    paths = (np.abs(v.noise(20, rng) - 0.5) < 0.012) & park & ~pwater
    park_only = park & ~pwater
    trees = v.park_trees(rng, park_only & ~lawn & ~v.dilate(paths, 1), 0.78, step=2.5)
    # tours repères, en volumes : une à gradins et mât, une à couronne claire, deux aiguilles de verre, une effilée
    tan = v.faces(P, 'ST1', 'ST2', 'ST3', top='RL2', alt='STW', mode=3)
    grey = v.faces(P, 'GS1', 'GS2', 'GS3', top='RG2', alt='GSW', mode=3)
    glass = v.faces(P, 'GL1', 'GL2', 'GL3', top='GL1', alt='GLW', mode=3)
    silver = v.faces(P, 'SV1', 'SV2', 'SV3', top='SV1')
    clear = np.zeros(X.shape, bool)

    def tower_at(cx, cy, tiers, f, mast=None):
        z0 = 0.0
        for hw_, z1 in tiers:
            sbox(cx - hw_, cx + hw_, cy - hw_, cy + hw_, z0, z1, f)
            z0 = z1
        if mast:
            sbox(cx - 0.3, cx + 0.3, cy - 0.3, cy + 0.3, z0, mast, silver)
        clear[int((cx - 7) * 2):int((cx + 7) * 2), int((cy - 7) * 2):int((cy + 7) * 2)] = True

    tower_at(447, 405, [(5.0, 22), (3.6, 34), (2.4, 42), (1.2, 47)], tan, 56)
    tower_at(497, 444, [(3.0, 36)], grey)
    z0 = 36.0
    for hw_ in (2.6, 2.1, 1.6, 1.1, 0.6):
        sbox(497 - hw_, 497 + hw_, 444 - hw_, 444 + hw_, z0, z0 + 1.7, silver)
        z0 += 1.7
    sbox(496.75, 497.25, 443.75, 444.25, z0, 53, silver)
    tower_at(427, 509, [(1.7, 55)], glass)
    tower_at(474, 512, [(1.5, 48)], glass)
    tower_at(428, 160, [(4.4, 10), (4.0, 20), (3.5, 30), (3.0, 38), (2.4, 46)], glass, 57)
    pyl = v.faces(P, 'ST1', 'ST2', 'ST3', top='ST1')
    cab = v.faces(P, 'SV2', 'SV2', 'SV3', top='SV1')
    for yb in (330, 430):                                              # deux ponts suspendus : pylônes de pierre, câbles en chaînette
        xa, x1, x2, xb = 540.0, 568.0, 614.0, 642.0
        for xp in (x1, x2):
            sbox(xp - 1.4, xp + 1.4, yb - 2.8, yb + 2.8, 0, 17, pyl)
        for side in (-2.3, 2.3):
            for xs in np.arange(xa, xb, 1.5):
                if xs < x1:
                    zc = 4.2 + (17 - 4.2) * ((xs - xa) / (x1 - xa)) ** 1.6
                elif xs > x2:
                    zc = 4.2 + (17 - 4.2) * ((xb - xs) / (xb - x2)) ** 1.6
                else:
                    tt = (xs - (x1 + x2) / 2) / ((x2 - x1) / 2)
                    zc = 5.6 + (17 - 5.6) * tt * tt
                bx.add(xs, xs + 1.5, yb + side - 0.3, yb + side + 0.3, zc - 0.55, zc, *cab)
                if int(xs * 2) % 6 == 0 and zc > 5.5:
                    bx.add(xs + 0.5, xs + 0.8, yb + side - 0.15, yb + side + 0.15, 3.6, zc - 0.55, *cab)
    bld &= ~clear
    cars = (avenue | street) & island & ~bld
    return {
        'water': water, 'wdepth': wdepth, 'park': park_only, 'bld': bld, 'H': H, 'kind': kind, 'roof': roof, 'ph': ph,
        'ground': {'street': ('NS1', 'NS2'), 'walk': 'NSW', 'water': ('W3', 'W2'), 'wscale': 30.0, 'edge_lit': 'RE1', 'edge_dark': 'RE2'},
        'paved': [(pier | (clear & island), 'PIER', 'NSW'), (lawn & park_only, 'G2', 'G1')],
        'over': [(bridges, 'PIER')],
        'lines': [(paths, 'S1'), (cars & (hb < 0.022), 'TAXI'), (cars & (hb2 < 0.02), 'AC')],
        'raised': [(v.cells_all(bridges), 3.6), (v.cells_all(pier), 0.4)],
        'roofs': [('RT1', 'RT2'), ('RB1', 'RB2'), ('RL1', 'RL2'), ('RG1', 'RG2')],
        'specks': [('RT1', 'TANK', 0.03), ('RB1', 'AC', 0.03), ('RL1', 'TANK', 0.02), ('RG1', 'AC', 0.04), ('RT1', 'AC', 0.02)],
        'kinds': [('BR1', 'BR2', 'BR3', 'BRW'), ('ST1', 'ST2', 'ST3', 'STW'), ('GS1', 'GS2', 'GS3', 'GSW'),
                  ('GL1', 'GL2', 'GL3', 'GLW'), ('GL2', 'GL3', 'GLW', 'GL1'), ('PIER', 'NSW', 'NS2', None)],
        'trees': trees, 'boxes': bx, 'prisms': [], 'zshadow': zs, 'strokes': 26000,
        'clouds': (64.0, 70.0, 90, 3.6, 6.0), 'cloud_gap': 80,
        'camera': {'start': (466.0, 30.0), 'yaw': (-5.0, 6.0), 'speed': 30.0, 'z': (108.0, 96.0), 'pitch': (-32.0, -26.0)},
        'fog': (275.0, 40.0, 110.0), 'win_shift': 2,
    }


# =================================================================== TOKYO
TOKYO_COLS = {
    'TS1': '#A3A7AE', 'TS2': '#959AA2', 'TSW': '#C4C6CA', 'LOT': '#B4B7B5',
    'A1': '#E7E8E4', 'A2': '#D3D5D3', 'B1': '#9FB4CC', 'B2': '#8AA1BC', 'D1': '#3F6394', 'D2': '#5277A8',
    'F1': '#9A6E52', 'F2': '#AD8166', 'H1': '#9DBF9A', 'H2': '#8BB08A', 'I1': '#868A93', 'I2': '#969AA2',
    'J1': '#A75D4B', 'J2': '#B96F5B', 'RE1': '#F4F4F0', 'RE2': '#3F434E',
    'TW1': '#EFEBE0', 'TW2': '#D5D0C3', 'TW3': '#A29D93', 'TWW': '#69717F',
    'GS1': '#C3C6CC', 'GS2': '#A0A4AC', 'GS3': '#70747E', 'GSW': '#4B4F5A',
    'GL1': '#8EC3E8', 'GL2': '#5C97CC', 'GL3': '#35669F', 'GLW': '#274C7C',
    'RA1': '#C9AE8E', 'RA2': '#5F4B40', 'EX1': '#7F93B3', 'EX2': '#E9EAEC',
    'O1': '#F0603A', 'O2': '#C9432A', 'O3': '#8E2C1F', 'WH1': '#FAFAF6', 'WH2': '#D9DCE2', 'WH3': '#A3A9B6',
    'TR1': '#E6EAEE', 'TR2': '#3FA35B', 'TR3': '#E08A2E', 'TR4': '#2F6FD0',
}


def tokyo(v, seed, P):
    """Vue vers le nord : la baie et ses terre-pleins au premier plan, un faisceau de voies sur viaduc qui monte vers
    la gare, la tour rouge et blanche, un fleuve à droite, le quartier de tours au fond. Plan inventé."""
    rng = np.random.default_rng(seed)
    X, Y, hi, r01, pk = v.XX, v.YY, v.hi, v.r01, v.pk
    bx, zs, sbox = _tools(v)
    hb = _blocks(v, 31)
    # ruelles : trame très déformée, angle par petit quartier ; petites parcelles
    u, w_, did = v.districts(rng, 85.0, 16)
    u = u + 14.0 * (v.noise(28, rng) - 0.5)
    w_ = w_ + 14.0 * (v.noise(28, rng) - 0.5)
    lane = ((u % 9.0) < 1.0) | ((w_ % 7.6) < 1.0)
    ph = hi(np.floor(u / 3.0) + (did % 997).astype(np.int64) * 7919, np.floor(w_ / 3.8), 5)
    pb = hi(np.floor(u / 9.0) + (did % 997).astype(np.int64) * 7919, np.floor(w_ / 7.6), 13)
    # la baie au sud, ses terre-pleins rectangulaires ; un fleuve qui s'y jette
    shore = 128.0 + 9.0 * np.sin(X / 55.0) + 6.0 * np.sin(X / 23.0 + 1.0)
    RIV = [(606, 60), (600, 170), (588, 300), (612, 450), (598, 640), (620, 900), (600, 1170)]
    dr = v.poly(RIV)
    river = dr < 10.0
    fill = (((X > 470) & (X < 522) & (Y > 58) & (Y < 112)) | ((X > 380) & (X < 440) & (Y > 80) & (Y < 122))
            | ((X > 640) & (X < 700) & (Y > 70) & (Y < 118)) | ((X > 250) & (X < 330) & (Y > 60) & (Y < 110)))
    pier = (Y > shore - 16) & (Y <= shore) & ((X % 11.0) < 3.4) & ~river & (np.abs(X - 603) > 16)
    bay = (Y < shore) & ~fill & ~pier
    pl, pr_ = v.along(RIV, 62.0, 14.0), v.along(RIV, 62.0, -14.0)
    bridge = np.zeros(X.shape, bool)
    for a, b in zip(pl, pr_):
        if a[1] > 150:
            bridge |= v.seg(a, b) < 1.7
    bridge &= dr < 12.0
    # voies ferrées : un grand faisceau sur viaduc (du port à la gare), une boucle, une traversante
    TRUNK = [(531, 112), (531, 380), (482, 520), (470, 720), (470, 1170)]
    d_tr = v.poly(TRUNK)
    LC, LR = (620.0, 540.0), 200.0
    d_loop = np.abs(np.hypot(X - LC[0], Y - LC[1]) - LR)
    L2 = [(-20, 585), (200, 575), (420, 548), (600, 520), (800, 545), (920, 530)]
    d_l2 = v.poly(L2)
    station = (np.abs(X - 471) < 9.0) & (np.abs(Y - 610) < 30)
    rail = (d_tr < 4.4) | (d_loop < 2.4) | (d_l2 < 2.2) | station
    rails = ((np.abs(d_tr - 0.9) < 0.3) | (np.abs(d_tr - 2.6) < 0.3) | (np.abs(d_loop - 1.0) < 0.3) | (np.abs(d_l2 - 1.0) < 0.3)
             | (station & ((X % 3.0) < 1.0)))
    EXP = [(700, -20), (655, 200), (622, 330), (640, 470), (600, 600), (520, 700), (380, 760), (250, 1000), (270, 1170)]
    d_exp = v.poly(EXP)
    expw = d_exp < 2.1
    roads = [[(-20, 250), (220, 300), (470, 290), (700, 250), (920, 280)], [(120, 100), (180, 300), (150, 600), (220, 900), (200, 1170)],
             [(-20, 760), (250, 720), (500, 760), (760, 720), (920, 760)], [(720, 100), (720, 300), (690, 560), (740, 860), (720, 1170)],
             [(330, 110), (350, 250), (420, 450), (400, 700), (440, 1170)], [(-20, 470), (200, 450), (360, 480)]]
    d_road = np.minimum.reduce([v.poly(r) for r in roads])
    # parcs : un jardin entouré de douves, un bois sombre, un jardin à étang, le pied de la tour
    rc = np.hypot(X - 640, Y - 560)
    palace, moat = rc < 44, (rc >= 44) & (rc < 51)
    wood = ((X - 440) / 30.0) ** 2 + ((Y - 420) / 42.0) ** 2 + 0.5 * (v.noise(20, rng) - 0.5) < 1
    garden = ((X - 545) / 30.0) ** 2 + ((Y - 250) / 20.0) ** 2 < 1
    pond = ((X - 549) / 11.0) ** 2 + ((Y - 249) / 5.5) ** 2 + 0.6 * (v.noise(10, rng) - 0.5) < 1
    TT = (490.0, 352.0)
    tpark = np.hypot(X - TT[0], Y - TT[1]) < 14
    park = (palace | wood | garden | tpark) & ~rail
    water = (bay | river | moat | (pond & garden)) & ~bridge & ~fill
    wdepth = np.where(bay, np.clip(shore - Y, 0, 30), np.where(river, 10.0 - dr, 4.0)).astype(np.float32)
    sky = (X > 352) & (X < 412) & (Y > 498) & (Y < 612)
    sky_st = sky & (((X - 352) % 20.0 < 2.6) | ((Y - 498) % 19.0 < 2.6))
    empty = (r01(ph, 12) < 0.06) & ~fill
    port = fill | pier
    bld = ~(lane | (d_road < 2.0) | rail | water | park | bridge | sky | empty | expw) & (Y > shore + 2.5)
    shed = fill & (((X % 13.0) > 2.5) & ((Y % 15.0) > 3.0))                                     # entrepôts des terre-pleins
    bld |= shed
    near = (d_road < 6.5) | (np.hypot(X - 471, Y - 610) < 60) | (d_loop < 5.5) | ((d_tr < 12) & (d_tr > 4.4))
    H = (0.9 + 1.5 * r01(ph, 4) ** 2 + np.where(near & (r01(ph, 16) < 0.55), 2.5 + 5.5 * r01(ph, 8), 0)).astype(np.float32)
    H[shed] = 1.4
    phs = hi(np.floor(X / 13.0), np.floor(Y / 15.0), 17)
    ph = np.where(shed, phs, ph)
    kind = np.where(H > 3.2, np.array([0, 1, 1, 0, 1, 0, 1, 2], np.uint8)[(r01(ph, 20) * 8).astype(int)], 0).astype(np.uint8)
    kind[rail | expw | bridge | pier] = 3
    roof = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 5, 6, 2, 1, 3, 0, 4], np.uint8)[(r01(ph, 6) * 16).astype(int)]
    roof_far = np.array([0, 1, 2, 3, 4, 0, 1, 6, 0, 2, 1, 3, 5, 0, 4, 1], np.uint8)[(r01(pb) * 16).astype(int)]   # au loin : un ton par îlot
    roof[shed] = np.array([1, 5, 0, 2], np.uint8)[(r01(phs) * 4).astype(int)][shed]
    roof_far = np.where(shed, roof, roof_far)
    # arbres
    tr = [v.park_trees(rng, wood, 0.92, step=2.3), v.park_trees(rng, palace & (rc > 14) & (((X + Y) % 23) > 4), 0.8, step=2.5),
          v.park_trees(rng, garden & ~pond & (v.noise(12, rng) > 0.45), 0.8, step=2.5),
          v.park_trees(rng, tpark & (np.hypot(X - TT[0], Y - TT[1]) > 9), 0.8, step=2.4, size=(0.8, 1.1)),
          v.park_trees(rng, empty & ~lane & ~rail & ~water & ~park & (d_road > 2.5) & ~sky & (Y > shore + 3) & (r01(ph, 2) < 0.5), 0.35, step=2.2, size=(0.6, 0.85))]
    trees = np.concatenate(tr)
    # repères : tour rouge et blanche en treillis, tours du quartier d'affaires dont une à deux sommets, trains
    v.lattice_tower(bx, zs, P, TT[0], TT[1], 41.0, 7.0, ('O1', 'O2', 'O3'), bands=('WH1', 'WH2', 'WH3'))
    grey = v.faces(P, 'GS1', 'GS2', 'GS3', top='I2', alt='GSW', mode=3)
    white = v.faces(P, 'TW1', 'TW2', 'TW3', top='A2', alt='TWW', mode=3)
    glass = v.faces(P, 'GL1', 'GL2', 'GL3', top='B1', alt='GLW', mode=3)
    tr2 = np.random.default_rng(seed + 9)
    for i in range(3):
        for j in range(6):
            cx, cy = 364.0 + 20.0 * i, 509.5 + 19.0 * j
            if (i, j) == (2, 0):
                sbox(cx - 5.2, cx + 5.2, cy - 3.4, cy + 3.4, 0, 21, grey)             # la tour à deux sommets
                sbox(cx - 4.6, cx - 1.4, cy - 2.2, cy + 2.2, 21, 34, grey)
                sbox(cx + 1.4, cx + 4.6, cy - 2.2, cy + 2.2, 21, 34, grey)
                continue
            if tr2.random() < 0.18:
                continue
            hwx, hwy = tr2.uniform(2.6, 4.6), tr2.uniform(2.6, 4.6)
            hh = tr2.uniform(16, 31)
            f = (grey, white, glass)[int(tr2.integers(0, 3))]
            sbox(cx - hwx, cx + hwx, cy - hwy, cy + hwy, 0, hh, f)
            if tr2.random() < 0.5:
                sbox(cx - hwx * 0.5, cx + hwx * 0.5, cy - hwy * 0.5, cy + hwy * 0.5, hh, hh + 2.5, f)
    sbox(TT[0] - 12, TT[0] - 7, TT[1] - 6, TT[1] + 0, 0, 2.4, v.faces(P, 'TW2', 'TW2', 'TW3', top='I1'))   # un temple à toit sombre
    sbox(462, 480, 584, 636, 1.2, 2.6, v.faces(P, 'GS1', 'GS2', 'GS3', top='A2'))                          # la halle de la gare

    def train(x, y0, cars, stripe, body='TR1'):
        """Rame sur le faisceau nord-sud : voitures de 4 unités, un liseré de couleur sur le toit."""
        for k in range(cars):
            ya = y0 + k * 4.5
            sbox(x - 0.75, x + 0.75, ya, ya + 4.1, 1.3, 2.25, v.faces(P, body, stripe, 'GS3', top=body))
            bx.add(x - 0.28, x + 0.28, ya + 0.2, ya + 3.9, 2.25, 2.32, *v.faces(P, stripe, stripe, stripe))

    train(530.1, 168, 8, 'TR2')
    train(533.6, 226, 8, 'TR3')
    train(528.4, 286, 7, 'TR4')
    train(533.6, 330, 6, 'TR2')
    return {
        'water': water, 'wdepth': wdepth, 'park': park, 'bld': bld, 'H': H, 'kind': kind, 'roof': roof, 'roof_far': roof_far, 'ph': ph,
        'ground': {'street': ('TS1', 'TS2'), 'walk': 'TSW', 'water': ('W3', 'W2'), 'wscale': 26.0, 'edge_lit': 'RE1', 'edge_dark': 'RE2'},
        'paved': [(empty & ~park & ~water, 'LOT', 'TSW'), (sky & ~sky_st, 'TSW', 'LOT'), (tpark & (np.hypot(X - TT[0], Y - TT[1]) < 9), 'TSW', 'LOT'),
                  (port & ~bld, 'LOT', 'TSW')],
        'over': [(rail, 'RA1'), (rails, 'RA2'), (expw, 'EX1'), (expw & (d_exp < 0.4) & (hb < 0.5), 'EX2'), (bridge, 'TSW')],
        'lines': [(palace & (rc < 14), 'S1'), ((d_road < 0.35) & (hb < 0.5), 'EX2')],
        'raised': [(v.cells_all(v.dilate(expw, 1)), 2.6), (v.cells_all(rail), 1.2), (v.cells_all(bridge), 0.6), (v.cells_all(port), 0.35)],
        'roofs': [('A1', 'A2'), ('B1', 'B2'), ('D1', 'D2'), ('F1', 'F2'), ('H1', 'H2'), ('I1', 'I2'), ('J1', 'J2')],
        'specks': [('A1', 'B1', 0.03), ('I1', 'A1', 0.04), ('B1', 'A1', 0.03)],
        'kinds': [('TW1', 'TW2', 'TW3', 'TWW'), ('GS1', 'GS2', 'GS3', 'GSW'), ('GL1', 'GL2', 'GL3', 'GLW'), ('EX1', 'TS1', 'TS2', None)],
        'trees': trees, 'boxes': bx, 'prisms': [], 'zshadow': zs, 'strokes': 30000,
        'clouds': (36.0, 44.0, 110, 3.2, 5.4), 'cloud_gap': 70,
        'fog': (250.0, 40.0, 100.0),
        'camera': {'start': (556.0, 34.0), 'yaw': (-2.0, -13.0), 'speed': 27.0, 'z': (84.0, 72.0), 'pitch': (-29.0, -24.0)},
    }


PLANS = {'paris': (PARIS_COLS, paris), 'newyork': (NY_COLS, newyork), 'tokyo': (TOKYO_COLS, tokyo)}
