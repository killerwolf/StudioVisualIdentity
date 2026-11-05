#!/usr/bin/env python3
"""Trait continu — enfants : « Dessine un escargot d'un seul trait » (15,5 s, graine 7).

Plaque 1 : un petit escargot (spirale de 2,5 tours partie du centre + corps), d'un seul trait.
Avance plaque (3 crans, 0,6 s) + clac. Plaque 2 : l'escargot a grandi, sa coquille a 4 tours (+1 repère bleu),
flèche bleue du sens (vers la droite, horaire), question finale.
Usage : video.py [--out x.mp4] | --stills 4,8 --dir D | --info | --sound-json src/sound.json
"""
import math, sys
from pathlib import Path
import numpy as np
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

sys.path.insert(0, str(Path(__file__).resolve().parent))
import traceur as T  # noqa: E402

DIR = 'trait-continu__enfants__dessine-un-escargot-d-un-seul-trait'
SEED = 7
DUR = 15.5


def snail_pieces(cx, cy, R, turns, tag):
    """Escargot d'un seul trait : spirale (centre -> dehors, horaire) puis corps, antennes en aller-retour."""
    sp = T.spiral(cx, cy, R, turns, end_angle=math.pi / 2)
    B = (cx, cy + R)
    # contour du corps : sous la coquille -> cou -> tête (linemerge raccorde les morceaux qui se touchent)
    under = [B, (cx + R * 0.7, cy + R * 1.0), (cx + R * 1.25, cy + R * 0.98)]
    neck = [(cx + R * 1.25, cy + R * 0.98), (cx + R * 1.33, cy + R * 0.78), (cx + R * 1.34, cy + R * 0.5),
            (cx + R * 1.5, cy + R * 0.3)]
    merged = linemerge(MultiLineString([under, neck]))
    body_top = np.asarray(merged.coords)
    if np.hypot(*(body_top[0] - B)) > 1:
        body_top = body_top[::-1]
    body_top = T.chaikin(body_top, 3)
    head = tuple(body_top[-1])
    a1 = (cx + R * 1.38, cy - R * 0.42)
    a2 = (cx + R * 1.92, cy - R * 0.22)
    eye_r = max(9, R * 0.075)

    def antenna(tip):
        out = T.chaikin([head, ((head[0] + tip[0]) / 2 + R * 0.05, (head[1] + tip[1]) / 2), tip], 2)
        eye = T.loop(tip[0], tip[1] - eye_r, eye_r, a0=math.pi / 2)
        return out, eye, out[::-1]

    o1, e1, b1 = antenna(a1)
    o2, e2, b2 = antenna(a2)
    front = T.chaikin([head, (cx + R * 1.82, cy + R * 0.36), (cx + R * 1.93, cy + R * 0.68),
                       (cx + R * 1.95, cy + R * 1.02), (cx + R * 1.84, cy + R * 1.22)], 3)
    sole = T.chaikin([tuple(front[-1]), (cx + R * 0.5, cy + R * 1.26), (cx - R * 0.8, cy + R * 1.25),
                      (cx - R * 1.3, cy + R * 1.24), (cx - R * 1.05, cy + R * 1.04), (cx - R * 0.78, cy + R * 0.93)], 3)
    return [(f'{tag}_coquille', sp), (f'{tag}_dessous', body_top), (f'{tag}_ant1', o1), (f'{tag}_oeil1', e1),
            (f'{tag}_ant1r', b1), (f'{tag}_ant2', o2), (f'{tag}_oeil2', e2), (f'{tag}_ant2r', b2),
            (f'{tag}_front', front), (f'{tag}_pied', sole)]


def spiral_split(pieces, tag, R, turns, cx, cy, turn_marks):
    """Coupe la coquille aux tours entiers pour poser des jalons (tour_k)."""
    out = []
    for name, c in pieces:
        if name != f'{tag}_coquille':
            out.append((name, c)); continue
        n = len(c)
        cuts = [0] + [int(round(n * k / turns)) for k in turn_marks] + [n - 1]
        for i in range(len(cuts) - 1):
            seg = c[cuts[i]:cuts[i + 1] + 1]
            out.append((f'{tag}_tour{turn_marks[i]}' if i < len(turn_marks) else name, seg))
    return out


def build():
    s = T.Short(SEED, DUR, f'/tmp/svi/{DIR}')
    vib = s.vib
    # ---- plaque 1 : petit escargot ----
    c1 = (440, 1000); R1 = 172
    p1 = s.plate(enter=None, exit=None)
    p1.path = T.build_path(snail_pieces(*c1, R1, 2.5, 'a'), start=0.3, speed=820, vib=vib)
    end1 = p1.path.end_time
    p1.exit = round(end1 + 0.45, 2)
    p1.items.append(dict(kind='ring', t=0.0, xy=c1))
    p1.items.append(dict(kind='label', t=2.7, xy=(T.CX, 1372), surf=T.text_surface('Du centre', 600, 60, T.INK_PLATE, label=T.CREAM),
                         sfx='pop', note='A5', gain=0.45))
    # ---- plaque 2 : il a grandi, 4 tours ----
    c2 = (470, 975); R2 = 185
    p2 = s.plate(enter=T.next_enter(p1.exit))
    pcs = spiral_split(snail_pieces(*c2, R2, 4, 'b'), 'b', R2, 4, *c2, turn_marks=[3])
    p2.path = T.build_path(pcs, start=p2.enter + 0.15, speed=900, vib=vib)
    t_plus = p2.path.time_at(p2.path.mlen['b_tour3']) + 0.25
    p2.items.append(dict(kind='ring', t=p2.enter - T.ENTER, xy=c2))
    p2.items.append(dict(kind='text', t=t_plus, xy=(c2[0] - R2 - 48, c2[1] - 40),
                         surf=T.text_surface('+1', 700, 76, T.BLUE), sfx='pop', note='C6', gain=0.5))
    t_arrow = 9.2
    p2.items.append(dict(kind='arrow', t=t_arrow, xy=c2, r=R2 + 52, a0=math.radians(-158), a1=math.radians(-28),
                         sfx='chime', note='E6', gain=0.35))
    # ---- titres (bande orange, ≤ 4 mots) ----
    s.title(-0.3, p1.exit + 0.2, "Un escargot\nd'un trait ?")
    s.title(p1.exit + 0.45, t_arrow - 0.05, 'Un tour\nde plus')
    s.title(t_arrow, 11.65, 'Vers la\ndroite')
    s.title(11.7, DUR + 1, 'Et toi,\nquel sens ?')
    return s


if __name__ == '__main__':
    T.main(build, f'/tmp/svi/{DIR}/video.mp4')
