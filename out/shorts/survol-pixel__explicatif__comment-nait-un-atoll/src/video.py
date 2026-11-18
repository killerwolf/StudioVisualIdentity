#!/usr/bin/env python3
"""
« Comment naît un atoll ? » — Survol pixel, famille explicatif.

Monde inventé, un seul sujet centré : un volcan en terrasses entouré d'un récif. Le niveau de la mer reste fixe ; le
volcan s'enfonce (paramètre s), le récif garde son anneau à la surface et s'épaissit de calcaire. Trois étapes : récif
frangeant (s = 0), récif-barrière avec lagon (s ≈ 0,6), atoll (s = 1). Une bande sud du monde est « coupée » comme une
maquette : la coupe montre le basalte du volcan, le calcaire corallien et l'eau, et à la fin le volcan enfoui sous
l'anneau (forages d'Enewetak, 1952). Une frégate (personnage original) vole avec son ombre.

Passe A+B+C : le monde est 3 fois plus large (1 080 unités) et rempli d'éléments propres au sujet, jamais d'archipel
vert : d'autres atolls au loin (anneaux de sable et de corail), monts sous-marins et hauts-fonds, bancs de sable,
houle à bandes de profondeur, nuages jusqu'à l'horizon avec leurs ombres ; au-delà, une mer texturée. Carte de couleurs
4 fois plus fine sur la fenêtre du sujet (recalculée seulement quand s ou la coupe changent), brume en 6 paliers vers
un bleu très pâle ; caméra qui vole ; un seul cartouche à la fois.

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
G = 1080                         # monde 3 fois plus large que la passe précédente (360)
C0 = G / 2
FW = 320                         # fenêtre du sujet (unités), carte de couleurs fine
FK = 4
FX0 = int(C0 - FW / 2)
P_PEAK, DEPTH, DH = 44.0, 30.0, 3.5
PIT, CUTW, CUT_D = 40.0, 100, 60   # socle, demi-largeur et profondeur de la tranchée coupée (bande sud)

BIOME = {'SAND': '#EBDFA0', 'ROCK': '#8A8178', 'CORAL': '#E58A7A', 'BASALT': '#4E4A4C', 'LIMESTONE': '#E3D3A8'}
pal = S.Palette(BIOME)
pal.set_lut('shadow', {
    'OCEAN': 'SH_WATER', 'OCEAN_MID': 'SH_WATER', 'SHALLOW': 'OCEAN_MID', 'LAGOON': 'SHALLOW', 'FOAM': 'LAGOON',
    'CORAL': 'ROCK', 'SAND': 'ROCK', 'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_D', 'GRASS_D': 'FOREST',
    'ROCK': 'BASALT', 'LIMESTONE': 'ROCK', 'BASALT': 'INK', 'CLOUD': 'HATCH', 'HATCH': 'MUTED', 'SKY_LO': 'SKY_MID',
    'SKY_MID': 'SKY_HI', 'SKY_HI': 'OCEAN_MID', 'HAZE': 'SKY_MID', 'WATER_FAR': 'OCEAN_MID', 'LAND_FAR': 'GRASS_D',
    'MUTED': 'INK', 'CREAM': 'HATCH', 'SH_WATER': 'INK'})
pal.set_haze({
    'OCEAN': ['OCEAN', 'OCEAN_MID', 'HZ_W1', 'WATER_FAR', 'HZ_W3', 'HAZE'],
    'OCEAN_MID': ['OCEAN_MID', 'HZ_W1', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SH_WATER': ['OCEAN', 'OCEAN_MID', 'HZ_W1', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SHALLOW': ['HZ_W1', 'WATER_FAR', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'LAGOON': ['SHALLOW', 'WATER_FAR', 'HZ_W2', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'FOAM': ['FOAM', 'HZ_W1', 'WATER_FAR', 'HZ_W2', 'HZ_W3', 'HAZE'],
    'SAND': ['SAND', 'LIMESTONE', 'HZ_G4', 'HZ_W3', 'HZ_W3', 'HAZE'],
    'CORAL': ['CORAL', 'SAND', 'HZ_G4', 'HZ_W3', 'HZ_W3', 'HAZE'],
    'LIMESTONE': ['LIMESTONE', 'LIMESTONE', 'HZ_G4', 'HZ_W3', 'HZ_W3', 'HAZE'],
    'ROCK': ['HZ_R1', 'HZ_R1', 'HZ_G3', 'HZ_G4', 'HZ_W3', 'HAZE'],
    'BASALT': ['MUTED', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HZ_W3', 'HAZE'],
    'GRASS_L': ['GRASS_M', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRASS_M': ['HZ_G1', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'GRASS_D': ['HZ_G1', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'FOREST': ['GRASS_D', 'HZ_G1', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'INK': ['FOREST', 'GRASS_D', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
    'MUTED': ['MUTED', 'HZ_G2', 'HZ_G2', 'HZ_G3', 'HZ_G4', 'HAZE'],
})
pal.set_lut('speckle', {'GRASS_L': 'GRASS_M', 'GRASS_M': 'GRASS_L', 'GRASS_D': 'FOREST', 'SAND': 'LIMESTONE',
                        'ROCK': 'BASALT', 'CORAL': 'SAND', 'LIMESTONE': 'SAND', 'FOREST': 'GRASS_D',
                        'BASALT': 'ROCK'})

# ------------------------------------------------------------------ champs fixes du monde
_F = {}


def _others():
    """Autres atolls au loin (anneaux de sable et de corail, sans île verte) et monts sous-marins / bancs : (x, y, r, type)."""
    return [(C0 - 300, C0 + 330, 34, 'atoll'), (C0 + 340, C0 + 400, 26, 'atoll'), (C0 - 430, C0 - 40, 30, 'atoll'),
            (C0 + 400, C0 - 300, 22, 'atoll'), (C0 + 120, C0 + 470, 18, 'atoll'),
            (C0 + 210, C0 + 170, 30, 'mont'), (C0 - 200, C0 - 280, 38, 'mont'), (C0 - 160, C0 + 160, 22, 'mont'),
            (C0 + 260, C0 - 120, 26, 'banc'), (C0 - 330, C0 + 90, 30, 'banc'), (C0 + 40, C0 - 380, 34, 'banc')]


def static():
    """Mer extérieure (fixe) et champs fins de la fenêtre du sujet, calculés une fois."""
    if _F:
        return _F
    yy, xx = np.mgrid[0:G, 0:G].astype(np.float32) + 0.5
    # profondeur de la mer extérieure : houle à grandes bandes, autres atolls, monts, bancs
    depth = 30 + 10 * S.vnoise(xx, yy, 140.0, SEED + 3, 2)
    land = np.zeros((G, G), bool)
    reefc = np.zeros((G, G), bool)
    rag = S.ragged((G, G), SEED + 11, 1.0)
    for (ox, oy, orr, kind) in _others():
        rr = np.hypot(xx - ox, (yy - oy) * 1.08) + 3 * S.vnoise(xx, yy, 9.0, SEED + int(ox), 1)
        if kind == 'atoll':
            band = rr - orr
            depth = np.where(np.abs(band) < 4, 0.4, depth)                       # anneau de corail affleurant
            depth = np.minimum(depth, np.where(band < -4, 4.0, 30))              # lagon peu profond
            depth = np.minimum(depth, 1.5 + np.clip(band - 4, 0, None) * 0.9)    # pente externe
            land |= (np.abs(band - 0.5) < 1.6) & (S.vnoise(xx, yy, 6.0, SEED + int(oy), 1) > 0.15)
            reefc |= np.abs(band) < 4
        elif kind == 'mont':
            depth = np.minimum(depth, 3.0 + (rr / orr) ** 2 * 18)
        else:
            u = np.hypot((xx - ox) / (orr * 1.6), (yy - oy) / (orr * 0.6))
            depth = np.minimum(depth, 0.9 + u ** 2 * 14)
            land |= u < 0.25
    # les îlots lointains restent à plat (couleur seule) : la boîte du relief se limite à la fenêtre du sujet et la mer
    # extérieure se calcule en forme close (plan z = 0), sans marche de rayon
    top = np.zeros((G, G), np.float32)
    dep = depth + rag * 3.0 * (depth < 18)
    cols = []
    for ph in (0, 1):
        col = np.full((G, G), pal['OCEAN'], np.uint8)
        col[dep < 26] = pal['OCEAN_MID']
        col[dep < 9] = pal['SHALLOW']
        col[dep < 2.6] = pal['LAGOON']
        col[reefc & (dep < 1.0)] = pal['CORAL']
        foam = (S.hash01(xx.astype(np.int64), yy.astype(np.int64), 40 + ph) < 0.014) & (dep > 9)
        col[foam] = pal['FOAM']
        col[land] = pal['SAND']
        cols.append(col)
    _F.update(top_out=top, col_out=cols, land_out=land)
    # profondeur extérieure lue aussi dans la fenêtre (houle à grandes bandes) : pas de bord droit à la frontière
    sl = slice(FX0, FX0 + FW)
    _F['depth_win'] = np.repeat(np.repeat(depth[sl, sl], FK, 0), FK, 1)
    # champs fins de la fenêtre (FK cases par cellule)
    n = FW * FK
    fy, fx = np.mgrid[0:n, 0:n].astype(np.float32)
    X = FX0 + (fx + 0.5) / FK
    Y = FX0 + (fy + 0.5) / FK
    _F['fine'] = fine_fields(X, Y, rag_seed=SEED + 12, foam=True)
    c = slice(FK // 2, None, FK)
    _F['coarse'] = fine_fields(X[c, c], Y[c, c], rag_seed=SEED + 11, foam=False)
    _F['fxy'] = (fx, fy)
    tr = S.scatter_trees(np.ones((FW, FW), bool), np.zeros((FW, FW), np.float32), SEED + 19, density=0.55,
                         r=(0.75, 1.25), cluster=(_F['coarse']['n2'] + 0.05) * 2.2)
    tr[:, 0] += FX0
    tr[:, 1] += FX0
    _F['trees'] = tr
    _F['tile'] = outside_tile()
    return _F


def fine_fields(X, Y, rag_seed, foam):
    dx, dy = X - C0, (Y - C0) * 1.06
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    n1 = S.vnoise(X, Y, 48.0, SEED, 3)
    n2 = S.vnoise(X, Y, 14.0, SEED + 7, 2)
    r0 = 60.0 * (1 + 0.06 * np.sin(3 * th + 0.7) + 0.04 * np.sin(5 * th + 2.1)) + 3.0 * n1
    u = r / r0
    cone = np.where(u < 1, P_PEAK * np.clip(1 - u, 0, None) ** 1.25, -(u - 1) * P_PEAK * 1.05)
    cone += 2.2 * n2 * np.clip(1 - u, 0, 1) * 2
    crater = np.clip(9 - r, 0, None) * 1.3
    B0 = np.maximum(cone - crater, -DEPTH)
    out = dict(r=r, th=th, n1=n1, n2=n2, r0=r0, B0=B0, band=r - r0,
               motu=(n1 > 0.05) & (np.abs(np.sin(4 * th + 1.3)) > 0.35),
               cut=(X > C0 - CUTW) & (X < C0 + CUTW) & (Y < C0) & (Y > C0 - CUT_D),
               rag=S.ragged(X.shape, rag_seed, 1.0),
               shelf=0.55 + 0.8 * (S.vnoise(X, Y, 22.0, SEED + 13, 2) + 1) / 2,
               patch=S.vnoise(X, Y, 7.0, SEED + 17, 1),
               surf=S.hash01(np.floor(X * 2).astype(np.int64), np.floor(Y * 2).astype(np.int64), 21) < 0.45,
               tex=S.vnoise(X, Y, 2.5, SEED + 31, 2), Y=Y)
    if foam:
        out['foam'] = [(S.hash01(np.floor(X * FK / 3).astype(np.int64), np.floor(Y * FK).astype(np.int64), 50 + ph) < 0.02)
                       for ph in (0, 1)]
    return out


def heights(f, s):
    band, B0 = f['band'], f['B0']
    Bs = B0 - s * (P_PEAK + 5.0)
    crest = (band > -1.0) & (band < 6.0)
    lag_floor = -(0.6 + 7.0 * s)
    outer = -0.3 - np.clip(band - 6.0, 0, None) * f['shelf']
    Hc = np.where(crest, -0.3, np.where(band >= 6.0, np.maximum(outer, -DEPTH), lag_floor))
    Hc = np.where(band < -1.0, np.maximum(Bs, lag_floor) if s > 0 else Bs, Hc)
    Hc = np.maximum(Hc, Bs)
    patch = (band < -3.0) & (f['patch'] > 0.45) & (Hc < -1.0) & (s > 0.25)
    Hc = np.where(patch, -0.9, Hc)
    motu = crest & f['motu'] & (s > 0.55) & (band > 0.5) & (band < 4.5)
    Hc = np.where(motu, 0.6, Hc)
    return Hc, Bs, crest, patch, motu


_MEMO = {}


def build_world(s, u_cut, t):
    """s : enfoncement 0 → 1 ; u_cut : ouverture de la coupe 0 → 1. Mémoïsé : le monde ne change qu'avec s, la coupe et
    la phase d'écume (2 Hz)."""
    ph = int(math.floor(t * 2)) % 2
    key = (round(s, 4), round(u_cut, 4), ph)
    if key in _MEMO:
        return _MEMO[key]
    F = static()
    fc, ff = F['coarse'], F['fine']
    # --- hauteurs (1 cellule = 1 unité) dans la fenêtre
    Hc, Bs, crest, patch, motu = heights(fc, s)
    land = Hc > 0
    L = np.floor(np.maximum(Hc, 0) / DH).astype(np.int32)
    topc = np.where(land, 0.45 + L * DH, 0.0).astype(np.float32)
    topc = np.where(motu, 0.6, topc)
    fl = np.full((FW, FW), pal['GRASS_D'], np.uint8)
    fd = np.full((FW, FW), pal['FOREST'], np.uint8)
    fl[L >= 9] = pal['ROCK']
    fd[L >= 9] = pal['BASALT']
    fl[(L == 0) | motu] = pal['ROCK']
    fd[(L == 0) | motu] = pal['ROCK']
    # --- couleurs fines (FK cases par cellule)
    Hf, _, crest_f, patch_f, motu_f = heights(ff, s)
    up = lambda a: np.repeat(np.repeat(a, FK, 0), FK, 1)
    topf = up(topc)
    landf = topf > 0
    Lf = up(L)
    dep = np.minimum(-Hf, F['depth_win']) + ff['rag'] * np.where(-Hf < 18, 3.0, 0.0)
    col = np.full(topf.shape, pal['OCEAN'], np.uint8)
    col[(dep < 14) | (F['depth_win'] < 26)] = pal['OCEAN_MID']
    col[dep < 6] = pal['SHALLOW']
    col[dep < 1.6] = pal['LAGOON']
    col[patch_f & (ff['rag'] > 0.3)] = pal['CORAL']
    band = ff['band']
    col[crest_f & (band > 0.0) & (band < 3.5) & ~landf] = pal['CORAL']
    col[(band > 5.2) & (band < 7.0) & ff['surf'] & ~landf] = pal['FOAM']
    col[ff['foam'][ph] & (dep > 6) & ~landf] = pal['FOAM']
    # terre : marches par la géométrie (L), textures fines
    tex = ff['tex']
    g = landf & (Lf >= 1)
    col[landf] = pal['SAND']
    col[g] = np.where((Lf[g] % 2 == 1) ^ (tex[g] > 0.45), pal['GRASS_L'], pal['GRASS_M'])
    fo = g & (ff['n2'] > 0.18) & (Lf <= 7)
    col[fo] = pal['FOREST']
    col[fo & (tex > 0.1)] = pal['GRASS_D']                       # houppiers (même teinte que les arbres dessinés)
    rk = landf & (Lf >= 9)
    col[rk] = np.where(np.sin(topf[rk] * 1.7 + 3 * tex[rk]) > 0.6, pal['BASALT'], pal['ROCK'])
    col[motu_f & landf] = pal['SAND']
    # bord fin des marches : 2 cases fines contre la marche voisine plus haute
    hi = np.zeros(topf.shape, bool)
    for sh in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        hi |= np.roll(topf, sh, (0, 1)) > topf + 0.1
    foot = landf & hi
    col[foot & (Lf >= 1) & (Lf < 9)] = pal['GRASS_D']
    col[foot & (Lf >= 9)] = pal['BASALT']
    col[foot & (Lf == 0)] = pal['ROCK']
    # --- coupe
    cutc = fc['cut'] if u_cut > 0 else None
    top_before = topc.copy()
    if cutc is not None:
        drop = u_cut * (P_PEAK + PIT + 2)
        topc = np.where(cutc, np.maximum(topc - drop, -PIT), topc)
        if u_cut >= 1:
            # socle de la maquette : dalles de 2 unités, une sur trois sombre (hachage fixe) ; les rayures d'une unité
            # scintillaient en rasante (A-B-A 14 % sur la moitié basse de l'image à 17 s)
            fx_, fy_ = F['fxy']
            dal = S.hash01((fx_ // (2 * FK)).astype(np.int64), (fy_ // (2 * FK)).astype(np.int64), 77) < 0.33
            col = np.where(ff['cut'], np.where(dal, pal['BASALT'], pal['ROCK']), col)
    # --- assemblage dans le grand monde
    sl = slice(FX0, FX0 + FW)
    top = F['top_out'].copy()
    top[sl, sl] = topc
    colc = F['col_out'][ph].copy()
    flb = np.full((G, G), pal['ROCK'], np.uint8)
    fdb = np.full((G, G), pal['ROCK'], np.uint8)
    flb[sl, sl] = fl
    fdb[sl, sl] = fd
    cut = np.zeros((G, G), bool)
    ctop0 = None
    if cutc is not None:
        cut[sl, sl] = cutc
        ctop0 = F['top_out'].copy()
        ctop0[sl, sl] = top_before
    shade = np.zeros((G, G), bool)
    shade[sl, sl] = S.relief_shade(topc, R.sun, reach=40, slope=1.0 / math.hypot(*R.sun)) & ~(cutc if cutc is not None else False)

    def section(hx, hy, hz, xi, yi, along, tt):
        xi_, yi_ = np.clip(xi - FX0, 0, FW - 1), np.clip(yi - FX0, 0, FW - 1)
        b = Bs[yi_, xi_]
        h = Hc[yi_, xi_]
        out = np.full(len(hz), pal['LAGOON'], np.uint8)
        out[(np.floor(hz / 1.2) % 2) == 0] = pal['SHALLOW']
        lim = hz < h
        out[lim] = pal['LIMESTONE']
        strata = lim & ((np.floor(hz / 5.0) % 2) == 0) & ((np.floor(along) % 9) < 6)
        out[strata & (np.abs(hz - np.round(hz / 5) * 5) < 0.6)] = pal['SAND']
        bas = hz < b
        out[bas] = pal['BASALT']
        out[bas & ((along % 7.0) < 0.8)] = pal['ROCK']
        out[(hz >= 0) & (hz < topc[yi_, xi_] + 0.01) & (h > 0)] = pal['BASALT']
        out[(hz > -2.3) & (hz <= 0.0) & ((np.floor(along / 3.0) % 2) == 0)] = pal['FOAM']
        return out

    w = S.World(top, colc, flb, fdb, cut=cut if cutc is not None else None, section=section, outside=pal['OCEAN'],
                zmin=-PIT - 0.5, outside_tile=F['tile'][ph], cut_top0=ctop0, fine=(FX0, FX0, FK, col), shade=shade)
    if len(_MEMO) > 6:
        _MEMO.clear()
    _MEMO[key] = (w, Bs)
    return w, Bs


def outside_tile():
    """Mer au-delà du monde (toujours brumée) : houle à bandes de profondeur et écume semée, sur une tuile de 256."""
    n = 256
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    v = S.vnoise(xx, yy, 32.0, SEED + 91, 2)
    out = []
    for ph in (0, 1):
        t = np.full((n, n), pal['OCEAN'], np.uint8)
        t[v > 0.25] = pal['OCEAN_MID']
        t[S.hash01(xx.astype(np.int64), yy.astype(np.int64), 60 + ph) < 0.012] = pal['FOAM']
        out.append(t)
    return out


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

# ------------------------------------------------------------------ caméra (une seule pour tout le short) : elle vole
# approche au-dessus de la mer vers l'anneau, virage et retour en arrière (le volcan revient), plan de coupe lent qui
# glisse le long de la tranchée pendant l'enfoncement, puis départ au-dessus de l'anneau vers les autres atolls.
cam_path = S.CameraPath([
    (0.0, dict(tx=C0 + 22, ty=C0 - 40, tz=0, dist=245, yaw=-28, pitch=40, roll=-9), 'linear'),
    (2.9, dict(tx=C0 + 4, ty=C0 - 6, tz=0, dist=200, yaw=-18, pitch=37, roll=-4), 'linear'),
    (3.9, dict(tx=C0 + 6, ty=C0 - 10, tz=-6, dist=240, yaw=-12, pitch=27, roll=6), 'linear'),
    (7.6, dict(tx=C0 - 8, ty=C0 - 6, tz=-8, dist=226, yaw=-4, pitch=25, roll=4), 'linear'),
    (11.2, dict(tx=C0 + 10, ty=C0 - 6, tz=-8, dist=222, yaw=8, pitch=25, roll=-3), 'linear'),
    (13.4, dict(tx=C0 + 16, ty=C0 - 8, tz=-6, dist=226, yaw=12, pitch=26, roll=-5), 'linear'),
    (15.0, dict(tx=C0 + 10, ty=C0 + 14, tz=0, dist=230, yaw=2, pitch=35, roll=-9), 'linear'),
    (18.6, dict(tx=C0 - 30, ty=C0 + 120, tz=0, dist=240, yaw=-22, pitch=38, roll=-12), 'linear'),
], smooth=True)


def _clouds():
    """Tas de coton à une seule altitude (CLOUD_Z = 90 : au-dessus de la caméra des plans rasants), dans tout le monde
    jusqu'à l'horizon, hors de l'anneau (rayon ≥ 88) et jamais traversés par la caméra (≥ 45 unités + rayon)."""
    rng = np.random.default_rng(SEED + 23)
    ts = np.arange(0.0, DUR + 0.01, 0.2)
    cams = np.array([S.Cam(cam_path.at(float(t)), 416.0).pos for t in ts])
    out = []
    tries = 0
    while len(out) < 70 and tries < 9000:
        tries += 1
        x, y = C0 + rng.uniform(-520, 520), C0 + rng.uniform(-520, 520)
        R_ = float(rng.uniform(8.0, 13.0))
        if math.hypot(x - C0, (y - C0) * 1.06) < 88 or any(math.hypot(x - c.x, y - c.y) < 40 for c in out):
            continue
        P = np.stack([x + DRIFT[0] * ts, y + DRIFT[1] * ts, np.full_like(ts, CLOUD_Z)], 1)
        if np.linalg.norm(P - cams, axis=1).min() < 45 + R_:
            continue
        out.append(S.Cloud(x, y, CLOUD_Z, R_, int(rng.integers(2, 5)), SEED + 100 + len(out)))
    return out


CLOUDS = _clouds()


def sink(t):
    if t < 2.9:
        return 1.0
    if t < 3.9:
        return 1.0 - S.ease('inOutCubic', (t - 2.9) / 1.0)
    if t < 7.6:
        return 0.0
    if t < 11.2:
        return 0.6 * S.ease('inOutSine', (t - 7.6) / 3.6)
    if t < 12.6:
        return 0.6 + 0.4 * S.ease('inOutSine', (t - 11.2) / 1.4)
    return 1.0


def cut_open(t):
    return S.ease('inOutCubic', (t - 4.0) / 0.8)


R = S.Renderer(pal, focal=416.0, wall_speck=0.25, haze_k=(1.6, 2.2, 2.9, 3.7, 4.7, 6.0))   # mer : brume plus lointaine

# un seul cartouche à la fois, calé sur narration.json (mots repérés par silencedetect) ; (t0, t1, lignes, taille, x, y,
# ancre, options)
CARDS = [
    (0.15, 2.05, ['UN ANNEAU', 'EN PLEINE MER ?'], 15, S.CX_SAFE, 62, 'ct', {}),
    (3.5, 5.0, ['1. UN VOLCAN', 'BORDÉ DE CORAIL'], 15, S.CX_SAFE, 62, 'ct', {}),
    (6.3, 7.6, ['marches : convention de dessin'], 10, S.CX_SAFE, 62, 'ct', {}),
    (7.6, 9.2, ["2. IL S'ENFONCE,", 'LE CORAIL MONTE'], 15, S.CX_SAFE, 62, 'ct', {}),
    (11.8, 13.4, ['3. UN VOLCAN', "SOUS L'ANNEAU"], 15, S.CX_SAFE, 62, 'ct', {}),
    (15.0, 16.8, ['DARWIN, 1842'], 15, S.CX_SAFE, 62, 'ct', {'inverted': True, 'colors': 'GOLD'}),
    (16.8, 18.6, ['basalte trouvé', 'dessous en 1952'], 15, S.CX_SAFE, 62, 'ct', {}),
]
PINS = [  # étiquettes au sol (C9), une à la fois : (t0, t1, lignes, point monde, position du cartouche)
    (5.0, 6.3, ['basalte'], lambda: (C0 + 10, C0 - 0.3, -10.0), (40, 330)),
    (9.2, 11.2, ['calcaire'], lambda: (C0 + 62, C0 - 0.3, -6.0), (40, 330)),
    (13.4, 15.0, ['niveau de la mer'], lambda: (C0 + 36, C0 - 0.3, -1.0), (18, 338)),
]
LAST = {}


def haze_ref(p):
    """Distance de référence de la brume : la distance de la caméra, bornée en bas (220) pour que les plans
    rapprochés (coupe) et les piqués ne fassent pas glisser tous les paliers d'un coup."""
    return max(p['dist'], 220.0)


def frame_idx(t, cam_override=None, s_override=None, u_override=None, cards=True):
    s = sink(t) if s_override is None else s_override
    u = cut_open(t) if u_override is None else u_override
    w, Bs = build_world(s, u, t)
    p = cam_path.at(t) if cam_override is None else cam_override
    cam = S.Cam(p, R.focal)
    disks = S.cloud_shadow_disks(CLOUDS, R.sun, t, DRIFT)
    shadow = S.disk_mask(disks, 0.0, 0.0, G, G, 1.0)
    idx, depth, hit = R.ground(w, cam, t, shadow, haze_ref=haze_ref(p))
    LAST['hit'] = hit
    tr = static()['trees']
    txi = np.clip(tr[:, 0].astype(int), 0, G - 1)
    tyi = np.clip(tr[:, 1].astype(int), 0, G - 1)
    tz = w.top[tyi, txi]
    on = (tz > 0.45 + DH * 0.9) & (tz < 0.45 + DH * 8.5) & ~(w.cut[tyi, txi])
    if on.any():
        T = tr[on].copy()
        T[:, 2] = tz[on]
        S.draw_trees(idx, depth, cam, pal, T, R.sun, haze=(haze_ref(p), R.haze_k, R.haze_jit))
    if s > 0.7:
        for k, a in enumerate(np.linspace(0.4, 2 * math.pi + 0.4, 14, endpoint=False)):
            rr = 62.5
            x, y = C0 + rr * math.cos(a), C0 + rr * math.sin(a) / 1.06
            xi, yi = int(x), int(y)
            if 0 <= xi < G and 0 <= yi < G and w.top[yi, xi] > 0.5:
                palm.draw(idx, depth, cam, pal, x, y, w.top[yi, xi], w.top[yi, xi], sun=R.sun)
    if t < 3.4 or t > 12.4:
        tb = t if t < 3.4 else t - 12.4
        x = C0 - 70 + 40 * tb
        y = C0 - 85 + 30 * tb
        bird.draw(idx, depth, cam, pal, x, y, 34.0, 0.0, frame=int(t * 3) % 2, sun=R.sun)
    S.draw_clouds(idx, depth, cam, pal, CLOUDS, t, DRIFT)
    LAST['clean'] = idx.copy()
    if cam_override is None and cards:
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
    static()
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
