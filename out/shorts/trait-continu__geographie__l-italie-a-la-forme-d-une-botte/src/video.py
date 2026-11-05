#!/usr/bin/env python3
"""Trait continu — géographie : « L'Italie a la forme d'une botte » (16 s, graine 11).

Plaque 1 : une botte générique, inclinée comme la péninsule, d'un seul trait (le hook).
Avance plaque (3 crans) + clac. Plaque 2 : le trait part de la pointe, remonte la côte tyrrhénienne, longe les Alpes,
descend l'Adriatique jusqu'au talon (arrêt : repère bleu « Pouilles »), traverse le golfe de Tarente jusqu'à la pointe
(arrêt : repère « Calabre »), puis un pont calculé (le coup de pied) l'emmène autour de la Sicile, le ballon.
Contours tracés à la main (lon/lat, ≈ 0,1° près), puis shapely.simplify : c'est un choix de style, le trait simplifie.
Usage : video.py [--out x.mp4] | --stills 4,8 --dir D | --info | --sound-json src/sound.json
"""
import math, sys
from pathlib import Path
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely import affinity

sys.path.insert(0, str(Path(__file__).resolve().parent))
import traceur as T  # noqa: E402

DIR = 'trait-continu__geographie__l-italie-a-la-forme-d-une-botte'
SEED = 11
DUR = 16.0

# Péninsule, sens horaire depuis Vintimille (lon, lat), tracée à la main.
MAINLAND = [
    (7.53, 43.79), (7.65, 44.15), (6.95, 44.42), (6.85, 45.0), (7.1, 45.25), (6.8, 45.8), (7.55, 45.95), (8.2, 46.15),
    (8.45, 46.45), (9.0, 45.85), (9.3, 46.5), (10.1, 46.6), (10.45, 46.9), (11.0, 46.8), (12.2, 47.05), (12.7, 46.65),
    (13.7, 46.5), (13.45, 46.2), (13.65, 45.8), (13.75, 45.6),                                   # Trieste
    (13.1, 45.75), (12.4, 45.45), (12.3, 45.2), (12.5, 44.95), (12.25, 44.6), (12.4, 44.2), (12.9, 43.9),
    (13.5, 43.6), (13.85, 43.1), (14.2, 42.45), (14.7, 42.1), (15.15, 41.93), (16.0, 41.95), (16.18, 41.85),
    (15.9, 41.55), (16.5, 41.3), (16.9, 41.12), (17.5, 40.85), (17.95, 40.65), (18.5, 40.15), (18.37, 39.8),  # Leuca
    (18.0, 40.05), (17.25, 40.45), (16.8, 40.37), (16.55, 39.95), (16.55, 39.65), (17.1, 39.4), (17.13, 39.05),
    (16.55, 38.75), (16.55, 38.45), (16.15, 38.3), (15.95, 37.93), (15.65, 38.0), (15.64, 38.11),        # Reggio
    (15.7, 38.25), (15.9, 38.5), (15.85, 38.68), (16.15, 39.1), (15.8, 39.6), (15.65, 40.05), (15.28, 40.03),
    (14.95, 40.25), (14.75, 40.65), (14.35, 40.6), (14.25, 40.83), (13.9, 41.15), (13.55, 41.22), (13.05, 41.25),
    (12.6, 41.5), (12.2, 41.75), (11.75, 42.1), (11.1, 42.4), (10.55, 42.95), (10.5, 43.3), (10.3, 43.55),
    (10.25, 43.95), (9.85, 44.07), (9.2, 44.3), (8.75, 44.4), (8.2, 44.05),
]
SICILY = [
    (15.55, 38.25), (15.65, 38.27), (15.28, 37.85), (15.1, 37.5), (15.3, 37.07), (15.1, 36.68), (14.85, 36.72),
    (14.25, 37.06), (13.95, 37.1), (13.55, 37.28), (13.05, 37.5), (12.6, 37.65), (12.43, 37.8), (12.5, 38.02),
    (12.73, 38.18), (13.35, 38.12), (14.0, 38.04), (15.24, 38.26),
]
I_TRIESTE, I_LEUCA, I_REGGIO = 19, 40, 53

K, LON0, LAT0, X0, Y0 = 76.0, 12.6, 41.875, 556, 1000


def proj(lon, lat):
    return X0 + (lon - LON0) * math.cos(math.radians(42)) * K, Y0 - (lat - LAT0) * K


def italy_pieces():
    xy = [proj(*p) for p in MAINLAND]
    ring = Polygon(xy).exterior
    simp = ring.simplify(1.2)        # shapely : retire les points superflus (< 1,2 px), garde la silhouette
    keep = [tuple(c) for c in simp.coords[:-1]]
    # index des sommets-clés dans le contour simplifié
    def idx(p):
        return int(np.argmin([math.hypot(x - p[0], y - p[1]) for x, y in keep]))
    i_t, i_l, i_r = idx(xy[I_TRIESTE]), idx(xy[I_LEUCA]), idx(xy[I_REGGIO])
    loop_ = keep + keep                # pour découper circulairement
    n = len(keep)
    west = loop_[i_r:n + 1]           # Reggio -> côte tyrrhénienne -> Vintimille (fin du contour, retour à l'index 0)
    alps = keep[0:i_t + 1]
    adri = keep[i_t:i_l + 1]
    gulf = keep[i_l:i_r + 1]
    sic = [proj(*p) for p in SICILY]
    sic_ring = T.bridge_ring(gulf[-1], sic)   # pont le plus court depuis la pointe : le coup de pied
    return [('ouest', west), ('alpes', alps), ('talon', adri), ('pointe', gulf), ('sicile', sic_ring)], len(keep), len(sic)


def boot_pieces():
    """Botte générique (pointe à gauche, talon à droite), inclinée comme la péninsule, ajustée dans la zone de dessin."""
    pts = [(0, 0), (200, 0), (205, 200), (215, 400), (235, 520), (250, 560), (250, 640), (170, 640), (160, 610),
           (100, 615), (-80, 640), (-190, 640), (-230, 610), (-215, 570), (-140, 530), (-40, 470), (-10, 380),
           (-5, 200), (0, 0)]
    ls = affinity.rotate(LineString(pts), -24, origin='centroid')
    x0, y0, x1, y1 = ls.bounds
    k = min(600 / (x1 - x0), 760 / (y1 - y0))
    ls = affinity.scale(ls, k, k, origin='centroid')
    x0, y0, x1, y1 = ls.bounds
    ls = affinity.translate(ls, 558 - (x0 + x1) / 2, 1010 - (y0 + y1) / 2)
    return [('botte', T.chaikin(np.asarray(ls.coords), 2))]


def build():
    s = T.Short(SEED, DUR, f'/tmp/svi/{DIR}')
    vib = s.vib
    p1 = s.plate()
    p1.path = T.build_path(boot_pieces(), start=0.3, speed=850, vib=vib)
    p1.exit = round(p1.path.end_time + 0.35, 2)
    p1.items.append(dict(kind='ring', t=0.0, xy=tuple(p1.path.pts[0])))
    pieces, n_main, n_sic = italy_pieces()
    p2 = s.plate(enter=T.next_enter(p1.exit))
    p2.path = T.build_path(pieces, start=p2.enter + 0.12, speed=900, vib=vib, stops={'talon': 1.9, 'pointe': 1.7})
    t_heel = p2.path.time_at(p2.path.mlen['talon'])
    t_toe = p2.path.time_at(p2.path.mlen['pointe'])
    t_sic0 = t_toe + 1.7
    heel_xy, toe_xy = proj(*MAINLAND[I_LEUCA]), proj(*MAINLAND[I_REGGIO])
    p2.items.append(dict(kind='ring', t=p2.enter - T.ENTER, xy=tuple(p2.path.pts[0])))
    p2.items.append(dict(kind='pin', t=t_heel, xy=heel_xy, sfx='pop', note='A5', gain=0.5))
    p2.items.append(dict(kind='lead', t=t_heel + 0.1, xy=(0, 0), a=(heel_xy[0] - 4, 990), b=(heel_xy[0] - 2, heel_xy[1] - 30)))
    p2.items.append(dict(kind='label', t=t_heel + 0.2, xy=(818, 948),
                         surf=T.text_surface('Pouilles', 600, 56, T.INK_PLATE, label=T.CREAM)))
    p2.items.append(dict(kind='pin', t=t_toe, xy=toe_xy, sfx='pop', note='C6', gain=0.5))
    p2.items.append(dict(kind='label', t=t_toe + 0.2, xy=(515, 1222),
                         surf=T.text_surface('Calabre', 600, 60, T.INK_PLATE, label=T.CREAM)))
    t_end = p2.path.end_time
    p2.items.append(dict(kind='label', t=t_end + 0.05, xy=(380, 1330),
                         surf=T.text_surface('Sicile', 600, 60, T.INK_PLATE, label=T.CREAM), sfx='chime', note='E6', gain=0.35))
    s.title(-0.3, p1.exit + 0.2, "L'Italie,\nune botte ?")
    s.title(p1.exit + 0.45, t_heel - 0.05, 'Suis\nle trait')
    s.title(t_heel, t_toe - 0.05, 'Le talon')
    s.title(t_toe, t_sic0 - 0.05, 'La pointe')
    s.title(t_sic0, DUR + 1, 'Et le\nballon ?')
    s.meta = dict(n_main=n_main, n_sic=n_sic, t_heel=t_heel, t_toe=t_toe, t_sic0=t_sic0, t_end=t_end)
    return s


if __name__ == '__main__':
    if '--info' in sys.argv:
        print(build().meta)
    T.main(build, f'/tmp/svi/{DIR}/video.mp4')
