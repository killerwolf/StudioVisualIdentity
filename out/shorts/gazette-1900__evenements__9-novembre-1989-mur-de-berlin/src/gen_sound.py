#!/usr/bin/env python3
"""gen_sound.py — écrit sound.json calé sur la grille de la scène (128 bpm, mêmes formules que index.html).
usage : python gen_sound.py > sound.json"""
import json, math

B = 60 / 128
st = [0, 8 * B, 18 * B, 24 * B]
DUR = 32 * B   # 15.0


def ticks(text, t0, cps=34, every=3):
    out, k = [], 0
    for i, c in enumerate(text):
        if c != ' ':
            if k % every == 0:
                out.append(round(t0 + (i + 1) / cps, 3))
            k += 1
    return out


ev = []
for k, s in enumerate(st):
    ev.append({'t': round(max(0, s - 0.05), 3), 'type': 'whoosh', 'gain': 0.55, 'dur': 0.55})
    ev.append({'t': round(s + (0.5 if k == 0 else 0.55), 3), 'type': 'thud', 'gain': 0.7})
# p0
ev.append({'t': 0.77, 'type': 'impact', 'gain': 0.55, 'dur': 0.5})
ev.append({'t': round(5 * B, 3), 'type': 'click', 'gain': 0.7})
ev += [{'t': t, 'type': 'tick', 'gain': 0.35} for t in ticks('la frontière est ouverte !', 0.9)]
# p1 — trois chiffres tamponnés + lignes tapées
facts = ['le Mur est construit.', 'autour de Berlin-Ouest.', 'une ville coupée en deux.']
for i, f in enumerate(facts):
    t = st[1] + 0.7 + i * 3 * B
    ev.append({'t': round(t + 0.15, 3), 'type': 'impact', 'gain': 0.5, 'dur': 0.45})
    ev += [{'t': x, 'type': 'tick', 'gain': 0.35} for x in ticks(f, t + 0.2, 40)]
ev.append({'t': round(st[1] + 0.7 + 8 * B, 3), 'type': 'click', 'gain': 0.7})
# p2 — fissure, chute des blocs, tampon
crack, fall = st[2] + 0.62, st[2] + 0.62 + 2 * B
ev.append({'t': round(crack, 3), 'type': 'glass', 'note': 'A4', 'gain': 0.35})
ev.append({'t': round(crack, 3), 'type': 'thud', 'gain': 0.6})
ev.append({'t': round(fall, 3), 'type': 'whoosh', 'gain': 0.5, 'dur': 0.6})
ev.append({'t': round(fall + 0.5, 3), 'type': 'impact', 'gain': 0.9, 'dur': 0.9})
ev.append({'t': round(fall + 0.62 + 0.15, 3), 'type': 'impact', 'gain': 0.5, 'dur': 0.45})
ev += [{'t': x, 'type': 'tick', 'gain': 0.35} for x in ticks('Berlin fait la fête !', st[2] + 0.62)]
# p3 — compteur 0 -> 37 (power2.out sur 4 temps), frise, tampon final
c0, cd = st[3] + 0.5, 4 * B
for n in range(1, 38, 2):
    x = 1 - math.sqrt(1 - n / 37)
    ev.append({'t': round(c0 + x * cd, 3), 'type': 'blip', 'note': 'E6', 'gain': 0.18})
ev.append({'t': round(c0 + cd, 3), 'type': 'chime', 'note': 'E5', 'gain': 0.35})
ev += [{'t': x, 'type': 'tick', 'gain': 0.35} for x in ticks('racontez en commentaire.', st[3] + 4 * B + 0.3)]
ev.append({'t': round(st[3] + 6 * B + 0.15, 3), 'type': 'impact', 'gain': 0.7, 'dur': 0.7})
ev.append({'t': round(st[3] + 6 * B + 0.2, 3), 'type': 'chime', 'note': 'A5', 'gain': 0.3})
spec = {'duration': round(DUR, 4), 'seed': 1989, 'bpm': 128, 'key': 'A', 'scale': 'minor',
        'music': {'preset': 'pulse', 'gain': 0.45, 'octave': 3, 'density': 0.6}, 'reverb': 0.14,
        'events': sorted(ev, key=lambda e: e['t'])}
print(json.dumps(spec, ensure_ascii=False, indent=1))
