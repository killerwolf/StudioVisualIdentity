#!/usr/bin/env python3
"""
« Comment naît un atoll ? » — Survol pixel, famille explicatif.

Monde inventé (un seul sujet centré, pas d'archipel) : un volcan en terrasses entouré d'un récif. Le niveau de la mer
reste fixe ; le volcan s'enfonce (paramètre s), le récif garde son anneau à la surface et s'épaissit de calcaire.
Trois étapes : récif frangeant (s = 0), récif-barrière avec lagon (s ≈ 0,6), atoll (s = 1). Une bande sud du monde est
« coupé » comme une maquette : la coupe montre le basalte du volcan, le calcaire corallien et l'eau, et à la fin le
volcan enfoui sous l'anneau (forages d'Enewetak, 1952). Une frégate (personnage original) vole avec son ombre.

Usage (depuis la racine du dépôt) :
  .venv/bin/python <src>/video.py --stills 0.5,5,9.5,16 --dir /tmp/x
  .venv/bin/python <src>/video.py --dive --dir /tmp/x        # série du piqué 90/70/50/30/15° (C1)
  .venv/bin/python <src>/video.py --out <cache>/video.mp4
"""
import math, sys, os
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import survol as S  # noqa: E402

DIR = Path(__file__).resolve().parents[1].name
CACHE = os.environ.get('SURVOL_CACHE', f'/private/tmp/survol-pixel/{DIR}')
SEED = 1842
DUR = 18.6
G = 360
C0 = G / 2
P_PEAK, DEPTH, DH = 44.0, 30.0, 3.5
PIT, CUTW, CUT_D = 40.0, 100, 50   # socle, demi-largeur et profondeur de la tranchée coupée (bande sud)

BIOME = {'SAND': '#EBDFA0', 'ROCK': '#8A8178', 'CORAL': '#E58A7A', 'BASALT': '#4E4A4C', 'LIMESTONE': '#E3D3A8'}
pal = S.Palette(BIOME)
pal.set_lut('shadow', {
    'OCEAN': 'SH_WATER', 'OCEAN_MID': 'SH_WATER', 'SHALLOW': 'OCEAN_MID', 'LAGOON': 'SHALLOW', 'FOAM': 'LAGOON',
    'CORAL': 'ROCK', 'SAND': 'ROCK', 'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_D', 'GRASS_D': 'FOREST',
    'ROCK': 'BASALT', 'LIMESTONE': 'ROCK', 'BASALT': 'INK', 'CLOUD': 'HATCH', 'HATCH': 'MUTED', 'SKY_LO': 'SKY_MID',
    'SKY_MID': 'SKY_HI', 'SKY_HI': 'OCEAN_MID', 'HAZE': 'SKY_MID', 'WATER_FAR': 'OCEAN_MID', 'LAND_FAR': 'GRASS_D',
    'MUTED': 'INK', 'CREAM': 'HATCH', 'SH_WATER': 'INK'})
pal.set_lut('haze1', {
    'OCEAN': 'WATER_FAR', 'OCEAN_MID': 'WATER_FAR', 'SHALLOW': 'WATER_FAR', 'LAGOON': 'SKY_LO', 'FOAM': 'WATER_FAR',
    'SH_WATER': 'OCEAN_MID', 'GRASS_L': 'LAND_FAR', 'GRASS_M': 'LAND_FAR', 'GRASS_D': 'LAND_FAR', 'FOREST': 'LAND_FAR',
    'SAND': 'LAND_FAR', 'ROCK': 'LAND_FAR', 'CORAL': 'LAND_FAR'})
pal.set_lut('speckle', {'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_L', 'GRASS_D': 'GRASS_M', 'SAND': 'LIMESTONE',
                        'ROCK': 'BASALT', 'CORAL': 'SAND', 'LIMESTONE': 'SAND', 'FOREST': 'GRASS_D'})
pal.set_lut('haze2', {n: 'HAZE' for n in pal.names if n not in ('CLOUD', 'HATCH', 'CREAM', 'INK')})

# ------------------------------------------------------------------ champs fixes du monde
_F = {}


def fields():
    if _F:
        return _F
    n1 = S.noise_field(G, 48.0, SEED, CACHE, 3)
    n2 = S.noise_field(G, 14.0, SEED + 7, CACHE, 2)
    yy, xx = np.mgrid[0:G, 0:G].astype(np.float32) + 0.5
    dx, dy = xx - C0, (yy - C0) * 1.06
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    # rayon de la côte initiale, irrégulier (anneau non circulaire)
    r0 = 60.0 * (1 + 0.06 * np.sin(3 * th + 0.7) + 0.04 * np.sin(5 * th + 2.1)) + 3.0 * n1
    u = r / r0
    cone = np.where(u < 1, P_PEAK * np.clip(1 - u, 0, None) ** 1.25, -(u - 1) * P_PEAK * 1.05)
    cone += 2.2 * n2 * np.clip(1 - u, 0, 1) * 2
    crater = np.clip(9 - r, 0, None) * 1.3
    B0 = np.maximum(cone - crater, -DEPTH)
    band = r - r0                                        # position dans l'anneau de récif
    forest = n2 > 0.18
    motu = (n1 > 0.05) & (np.abs(np.sin(4 * th + 1.3)) > 0.35)
    _F.update(r=r, th=th, r0=r0, B0=B0, band=band, forest=forest, motu=motu, n1=n1, n2=n2,
              cut=(xx > C0 - CUTW) & (xx < C0 + CUTW) & (yy < C0) & (yy > C0 - CUT_D))
    rng = np.random.default_rng(SEED)
    _F['surf'] = rng.random((G, G)) < 0.45
    _F['rag'] = S.ragged((G, G), SEED + 11, 1.0)                 # seuils crénelés (hauts-fonds, plage)
    _F['shelf'] = 0.55 + 0.8 * (S.noise_field(G, 22.0, SEED + 13, CACHE, 2) + 1) / 2   # pente du front externe, irrégulière
    _F['patch'] = S.noise_field(G, 7.0, SEED + 17, CACHE, 1)        # pâtés coralliens du lagon
    tr = S.scatter_trees(np.ones((G, G), bool), np.zeros((G, G), np.float32), SEED + 19, density=0.55,
                         r=(0.75, 1.25), cluster=(n2 + 0.05) * 2.2)
    _F['trees'] = tr
    _F['tiles'] = [S.foam_tile(pal, 64, SEED + 3, 'OCEAN', phase=k) for k in (0, 1)]
    _F['tiles_mid'] = [S.foam_tile(pal, 64, SEED + 3, 'OCEAN_MID', phase=k) for k in (0, 1)]
    return _F


def dep_amp(d):
    """amplitude du crénelage selon la profondeur : fort sur les hauts-fonds, nul au large"""
    return np.where(d < 18, 3.0, 0.0)


def build_world(s, u_cut, t):
    """s : enfoncement 0 → 1 ; u_cut : ouverture de la coupe 0 → 1."""
    f = fields()
    band, B0 = f['band'], f['B0']
    Bs = B0 - s * (P_PEAK + 5.0)                         # basalte, enfoncé
    # récif : anneau à la surface (crête −0,3) de band −1 à +6, front externe raide ; lagon dont le fond (calcaire)
    # s'abaisse lentement ; partout ailleurs le calcaire coiffe le basalte.
    crest = (band > -1.0) & (band < 6.0)
    lag_floor = -(0.6 + 7.0 * s)
    outer = -0.3 - np.clip(band - 6.0, 0, None) * f['shelf']
    Hc = np.where(crest, -0.3, np.where(band >= 6.0, np.maximum(outer, -DEPTH), lag_floor))
    Hc = np.where(band < -1.0, np.maximum(Bs, lag_floor) if s > 0 else Bs, Hc)
    Hc = np.maximum(Hc, Bs)
    # pâtés coralliens dans le lagon (seulement quand il existe) : têtes de corail sous 1 m d'eau
    patch = (band < -3.0) & (f['patch'] > 0.45) & (Hc < -1.0) & (s > 0.25)
    Hc = np.where(patch, -0.9, Hc)
    # motu (îlots de sable sur l'anneau) quand l'île centrale a disparu
    motu = crest & f['motu'] & (s > 0.55) & (band > 0.5) & (band < 4.5)
    Hc = np.where(motu, 0.6, Hc)
    land = Hc > 0
    L = np.floor(np.maximum(Hc, 0) / DH).astype(np.int32)
    top = np.where(land, 0.45 + L * DH, 0.0).astype(np.float32)
    top = np.where(motu, 0.6, top)
    # couleurs du dessus
    col = np.full((G, G), pal['OCEAN'], np.uint8)
    dep = -Hc + f['rag'] * np.clip(dep_amp(-Hc), 0, 3.0)        # seuils crénelés, quelques cellules isolées
    col[dep < 14] = pal['OCEAN_MID']
    col[dep < 6] = pal['SHALLOW']
    col[dep < 1.6] = pal['LAGOON']
    col[patch & (f['rag'] > 0.3)] = pal['CORAL']
    reef_core = crest & (band > 0.0) & (band < 3.5) & ~land
    col[reef_core] = pal['CORAL']
    surf = (band > 5.2) & (band < 7.0) & f['surf'] & ~land
    col[surf] = pal['FOAM']
    ph = int(math.floor(t * 2)) % 2                        # écume : 2 Hz (≤ 3 Hz, C13)
    tile = f['tiles'][ph]
    tm = f['tiles_mid'][ph]
    ty, tx = np.mgrid[0:G, 0:G]
    deep = col == pal['OCEAN']
    col[deep] = tile[ty[deep] % 64, tx[deep] % 64]
    mid = col == pal['OCEAN_MID']
    col[mid] = tm[ty[mid] % 64, tx[mid] % 64]
    g = land & (L >= 1)
    col[land & (L == 0)] = pal['SAND']
    col[g & (L % 2 == 1)] = pal['GRASS_L']
    col[g & (L % 2 == 0)] = pal['GRASS_M']
    col[g & f['forest'] & (L <= 7)] = pal['FOREST']
    col[land & (L >= 9)] = pal['ROCK']
    col[motu] = pal['SAND']
    # courbes de niveau : pied de chaque marche (cellule plus basse qu'une voisine) en trait sombre de 1 cellule
    Lm = np.where(land, L, -1)
    higher = np.zeros_like(land)
    for sh in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        higher |= np.roll(Lm, sh, (0, 1)) > Lm
    foot = land & higher & (L >= 1)
    col[foot & (L < 9)] = pal['GRASS_D']
    col[foot & (L >= 9)] = pal['BASALT']
    col[land & higher & (L == 0)] = pal['ROCK']
    fl = np.full((G, G), pal['GRASS_D'], np.uint8)
    fd = np.full((G, G), pal['FOREST'], np.uint8)
    fl[L >= 9] = pal['ROCK']
    fd[L >= 9] = pal['BASALT']
    fl[(L == 0) | motu] = pal['ROCK']
    fd[(L == 0) | motu] = pal['ROCK']
    # coupe (maquette) : la bande sud descend comme un ascenseur jusqu'au socle
    cut = f['cut'] if u_cut > 0 else None
    top_before = top.copy()
    if cut is not None:
        drop = u_cut * (P_PEAK + PIT + 2)
        top = np.where(cut, np.maximum(top - drop, -PIT), top)
        if u_cut >= 1:
            # socle de la maquette : roche hachurée (une rangée sombre sur trois), jamais l'encre du texte
            yy_ = np.arange(G)[:, None] % 3 == 0
            col = np.where(cut, np.where(yy_, pal['BASALT'], pal['ROCK']), col)

    def section(hx, hy, hz, xi, yi, along, tt):
        b = Bs[yi, xi]
        h = Hc[yi, xi]
        out = np.full(len(hz), pal['LAGOON'], np.uint8)    # tranche d'eau : lagon hachuré une ligne sur deux
        out[(np.floor(hz / 1.2) % 2) == 0] = pal['SHALLOW']
        lim = hz < h
        out[lim] = pal['LIMESTONE']
        # strates du calcaire : un trait tous les 5 unités
        strata = lim & ((np.floor(hz / 5.0) % 2) == 0) & ((np.floor(along) % 9) < 6)
        out[strata & (np.abs(hz - np.round(hz / 5) * 5) < 0.6)] = pal['SAND']
        bas = hz < b
        out[bas] = pal['BASALT']
        out[bas & ((along % 7.0) < 0.8)] = pal['ROCK']      # joints verticaux du basalte (lecture « roche »)
        out[(hz >= 0) & (hz < top[yi, xi] + 0.01) & (h > 0)] = pal['BASALT']
        # niveau de la mer : tireté clair fixe sur toute la coupe (le repère du mécanisme)
        out[(hz > -2.3) & (hz <= 0.0) & ((np.floor(along / 3.0) % 2) == 0)] = pal['FOAM']
        return out

    return S.World(top, col, fl, fd, cut=cut, section=section, outside=pal['OCEAN'], zmin=-PIT - 0.5,
                   outside_tile=tile, cut_top0=top_before), Bs


# ------------------------------------------------------------------ objets dessinés en code (originaux)
FRIGATE = [
    ["KK...........................KK",
     ".KKK.......................KKK.",
     "..KKKKK.......KMK.......KKKKK..",
     "....KKKKKK....KRK....KKKKKK....",
     "......KKKKKKKKKRKKKKKKKKK......",
     "..........KKKKKKKKKKK..........",
     "..............KKK..............",
     ".............KK.KK.............",
     "............KK...KK............",
     "...........K.......K..........."],
    ["...............................",
     "...............................",
     "KKKKKKK.......KMK.......KKKKKKK",
     "..KKKKKKKK....KRK....KKKKKKKK..",
     "......KKKKKKKKKRKKKKKKKKK......",
     "..........KKKKKKKKKKK..........",
     "..............KKK..............",
     ".............KK.KK.............",
     "............KK...KK............",
     "...........K.......K..........."]]
PALM = ["...G.G.G...",
        ".GGGGGGGGG.",
        "GGDGGGGGDGG",
        "G..DGGGD..G",
        ".....TG....",
        ".....T.....",
        "....T......",
        "....T......",
        "....T......",
        "...TT......"]

bird = S.Billboard([S.sprite_from_ascii(fr, {'K': 'INK', 'M': 'MUTED', 'R': 'RED'}, pal) for fr in FRIGATE], d1=330)
palm = S.Billboard([S.sprite_from_ascii(PALM, {'G': 'GRASS_M', 'D': 'GRASS_D', 'T': 'ROCK'}, pal)], d1=170)

DRIFT = (2.6, 0.9)
CLOUD_Z = 90.0


def _clouds():
    """24 tas de coton à une seule altitude (CLOUD_Z = 90 : au-dessus de la caméra des plans rasants, ombre décalée
    de ≈ 60 cellules comme dans la source), répartis dans le champ du survol, hors de l'anneau (rayon ≥ 88) pour
    ne jamais le masquer, jamais traversés par la caméra (≥ 45 unités + rayon sur tout le short). Plus hauts que la
    caméra des plans rasants, ils restent dans le ciel et ne passent jamais devant la coupe ; tailles de la source (≈ 100–250 cellules en plongeante)."""
    rng = np.random.default_rng(SEED + 23)
    ts = np.arange(0.0, DUR + 0.01, 0.2)
    cams = np.array([S.Cam(cam_path.at(float(t)), 416.0).pos for t in ts])
    out = []
    tries = 0
    while len(out) < 24 and tries < 5000:
        tries += 1
        x, y = C0 + rng.uniform(-170, 150), C0 + rng.uniform(-300, 230)
        R_ = float(rng.uniform(9.0, 13.0))
        if math.hypot(x - C0, (y - C0) * 1.06) < 88 or any(math.hypot(x - c.x, y - c.y) < 34 for c in out):
            continue
        P = np.stack([x + DRIFT[0] * ts, y + DRIFT[1] * ts, np.full_like(ts, CLOUD_Z)], 1)
        if np.linalg.norm(P - cams, axis=1).min() < 45 + R_:
            continue
        out.append(S.Cloud(x, y, CLOUD_Z, R_, int(rng.integers(2, 5)), SEED + 100 + len(out)))
    return out

# ------------------------------------------------------------------ caméra (une seule pour tout le short)
cam_path = S.CameraPath([
    (0.0, dict(tx=C0 - 4, ty=C0 - 8, tz=0, dist=385, yaw=-18, pitch=70, roll=0), 'linear'),
    (3.2, dict(tx=C0 + 1, ty=C0 - 1, tz=0, dist=330, yaw=-32, pitch=68, roll=0), 'linear'),
    (3.8, dict(tx=C0 + 2, ty=C0 - 4, tz=8, dist=250, yaw=-45, pitch=16, roll=0), 'inOutSine'),   # le piqué
    (7.4, dict(tx=C0 - 2, ty=C0 + 2, tz=8, dist=228, yaw=-36, pitch=14, roll=-3), 'inOutSine'),
    (11.3, dict(tx=C0, ty=C0, tz=4, dist=222, yaw=-50, pitch=15, roll=2), 'inOutSine'),
    (12.1, dict(tx=C0 + 6, ty=C0 + 4, tz=-8, dist=250, yaw=-10, pitch=32, roll=0), 'inOutSine'),  # la remontée
    (14.9, dict(tx=C0 + 4, ty=C0 + 4, tz=-8, dist=245, yaw=-4, pitch=30, roll=0), 'linear'),
    (15.5, dict(tx=C0 + 2, ty=C0 + 10, tz=-4, dist=212, yaw=0, pitch=17, roll=0), 'inOutSine'),   # rasante finale
    (18.6, dict(tx=C0, ty=C0 + 34, tz=-4, dist=206, yaw=5, pitch=15, roll=0), 'linear'),          # la caméra avance
])


CLOUDS = _clouds()


def sink(t):
    if t < 2.9:
        return 1.0
    if t < 3.9:
        return 1.0 - S.ease('inOutCubic', (t - 2.9) / 1.0)       # retour en arrière : le volcan revient
    if t < 7.6:
        return 0.0
    if t < 11.2:
        return 0.6 * S.ease('inOutSine', (t - 7.6) / 3.6)
    if t < 12.6:
        return 0.6 + 0.4 * S.ease('inOutSine', (t - 11.2) / 1.4)
    return 1.0


def cut_open(t):
    return S.ease('inOutCubic', (t - 4.0) / 0.8)


R = S.Renderer(pal, focal=416.0, haze_d=(560.0, 1500.0))

# cartouches : (t0, t1, lignes, taille, x, y, ancre, options)
CARDS = [
    (0.15, 3.3, ['UN ANNEAU', 'EN PLEINE MER ?'], 20, S.CX_SAFE, 62, 'ct', {}),
    (3.35, 7.4, ['1. UN VOLCAN', 'BORDÉ DE CORAIL'], 15, S.CX_SAFE, 62, 'ct', {}),
    (3.4, 4.6, ['il y a des millions', "d'années"], 15, S.CX_SAFE, 131, 'ct', {}),
    (4.6, 7.4, ['marches : convention de dessin'], 10, S.CX_SAFE, 131, 'ct', {}),
    (7.5, 11.5, ["2. IL S'ENFONCE,", 'LE CORAIL MONTE'], 15, S.CX_SAFE, 62, 'ct', {}),
    (7.6, 11.5, ['pendant des millions', "d'années"], 15, S.CX_SAFE, 131, 'ct', {}),
    (12.2, 14.9, ['3. UN VOLCAN', "SOUS L'ANNEAU"], 15, S.CX_SAFE, 62, 'ct', {}),
    (15.0, 18.6, ['DARWIN, 1842'], 20, S.CX_SAFE, 62, 'ct', {'inverted': True, 'colors': 'GOLD'}),
    (15.3, 18.6, ['basalte trouvé', 'dessous en 1952'], 15, S.CX_SAFE, 112, 'ct', {}),
]
PINS = [  # étiquettes au sol (C9) : (t0, t1, lignes, point monde, position du cartouche)
    (5.0, 7.3, ['basalte'], lambda: (C0 + 10, C0 - 0.3, -10.0), (40, 330)),
    (8.4, 11.3, ['calcaire'], lambda: (C0 + 62, C0 - 0.3, -6.0), (40, 330)),
    (8.4, 11.3, ['lagon'], lambda: (C0 + 30, C0 + 30, 0.0), (160, 212)),
    (12.4, 18.6, ['basalte'], lambda: (C0 - 4, C0 - 0.3, -16.0), (18, 250)),
    (12.4, 18.6, ['calcaire'], lambda: (C0 + 45, C0 - 0.3, -14.0), (18, 294)),
    (12.4, 18.6, ['niveau de la mer'], lambda: (C0 + 36, C0 - 0.3, -1.0), (18, 338)),
]


def frame_idx(t, cam_override=None, s_override=None, u_override=None):
    s = sink(t) if s_override is None else s_override
    u = cut_open(t) if u_override is None else u_override
    w, Bs = build_world(s, u, t)
    p = cam_path.at(t) if cam_override is None else cam_override
    cam = S.Cam(p, R.focal)
    shadows = S.cloud_shadow_disks(CLOUDS, R.sun, t, DRIFT)
    idx, depth, _ = R.ground(w, cam, t, shadows)
    # arbres en grappes sur les terrasses vertes du volcan (pied posé sur le dessus de la cellule)
    tr = fields()['trees']
    txi = np.clip(tr[:, 0].astype(int), 0, G - 1)
    tyi = np.clip(tr[:, 1].astype(int), 0, G - 1)
    tz = w.top[tyi, txi]
    on = (tz > 0.45 + DH * 0.9) & (tz < 0.45 + DH * 8.5) & ~(w.cut[tyi, txi])
    if on.any():
        T = tr[on].copy()
        T[:, 2] = tz[on]
        S.draw_trees(idx, depth, cam, pal, T, R.sun)
    # palmiers des motu (atoll)
    if s > 0.7:
        f = fields()
        for k, a in enumerate(np.linspace(0.4, 2 * math.pi + 0.4, 14, endpoint=False)):
            rr = float(np.interp(a, [-math.pi, math.pi], [60, 60])) + 2.5
            x, y = C0 + rr * math.cos(a), C0 + rr * math.sin(a) / 1.06
            xi, yi = int(x), int(y)
            if 0 <= xi < G and 0 <= yi < G and w.top[yi, xi] > 0.5:
                palm.draw(idx, depth, cam, pal, x, y, w.top[yi, xi], w.top[yi, xi], sun=R.sun)
    # frégate (vol, ombre décalée selon l'altitude)
    if t < 3.4 or t > 12.4:
        tb = t if t < 3.4 else t - 12.4
        x = C0 - 70 + 40 * tb
        y = C0 - 85 + 30 * tb
        bird.draw(idx, depth, cam, pal, x, y, 34.0, 0.0, frame=int(t * 3) % 2, sun=R.sun)
    S.draw_clouds(idx, depth, cam, pal, CLOUDS, t, DRIFT)
    if cam_override is None:
        for (t0, t1, lines, size, x, y, anc, opt) in CARDS:
            if t0 <= t < t1:
                prog = 1.0 if t0 < 0.5 else min(1.0, (t - t0) * 30 / 4)
                S.cartouche(idx, pal, lines, x, y, size=size, anchor=anc, progress=prog, **opt)
        for (t0, t1, lines, P, (bx, by)) in PINS:
            if t0 <= t < t1:
                gx, gy, gz = cam.project(np.array(P()))
                if gz > 1:
                    S.pinned_card(idx, pal, lines, bx, by, gx, gy)
    return idx


def check(t):
    w, _ = build_world(sink(t), cut_open(t), t)
    return S.Cam(cam_path.at(t), R.focal), w


def build():
    fields()
    return S.Short(pal, DUR, frame_idx, check)


def dive(outdir):
    """Série du piqué (C1) : même monde, même moteur, tangage 90/70/50/30/15°."""
    from PIL import Image
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for pitch in (90, 70, 50, 30, 15):
        p = dict(tx=C0 + 2, ty=C0 - 4, tz=8, dist=250 + (pitch - 15) * 1.3, yaw=-45, pitch=pitch, roll=0)
        ind = frame_idx(6.0, cam_override=p)
        Image.fromarray(S.upscale(S.to_rgb(ind, pal))).save(Path(outdir) / f'dive_{pitch:02d}deg.jpg', quality=90)
        print(pitch, len(np.unique(ind)), 'couleurs')


if __name__ == '__main__':
    if '--dive' in sys.argv:
        dive(sys.argv[sys.argv.index('--dir') + 1])
    else:
        S.main(build, f'{CACHE}/video.mp4')
