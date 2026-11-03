#!/usr/bin/env python3
"""gen_sound.py — écrit sound.json calé sur la grille de la scène (128 bpm, mêmes formules que index.html).
usage : python gen_sound.py > sound.json"""
import json

B = 60 / 128
P0, PAGE = 4 * B, 6 * B
DUR = P0 + 5 * PAGE + 6 * B          # 18.75
CPS = 34
starts = [0] + [P0 + k * PAGE for k in range(6)]
deps = ['tournez la page !', 'le tiers état veut le vote par tête.', 'pas de séparation sans Constitution.',
        'les Parisiens prennent la forteresse.', "l'Assemblée vote la fin des privilèges.", 'libres et égaux en droits.', 'quelle date ?']


def ticks(text, t0, cps=CPS, every=3):
    out, k = [], 0
    for i, c in enumerate(text):
        if c != ' ':
            if k % every == 0:
                out.append(round(t0 + (i + 1) / cps, 3))
            k += 1
    return out


ev = []
for k, s in enumerate(starts):
    ev.append({'t': round(max(0, s - 0.05), 3), 'type': 'whoosh', 'gain': 0.55, 'dur': 0.55})
    ev.append({'t': round(s + (0.5 if k == 0 else 0.55), 3), 'type': 'thud', 'gain': 0.7})
    if k < 6:
        ev.append({'t': round(s + (0.62 if k == 0 else 1.5 * B) + 0.15, 3), 'type': 'impact', 'gain': 0.55, 'dur': 0.5})
    if 1 <= k <= 5:
        ev.append({'t': round(s + 4 * B, 3), 'type': 'click', 'gain': 0.7})
    dep_t = s + (0.75 if k == 0 else 1.95 if k == 6 else 0.62)
    ev += [{'t': t, 'type': 'tick', 'gain': 0.35} for t in ticks(deps[k], dep_t)]
s6 = starts[6]
for i in range(5):
    ev.append({'t': round(s6 + 0.5 + i * 0.26 + 0.05, 3), 'type': 'tick', 'gain': 0.45})
ev.append({'t': round(s6 + 4 * B + 0.15, 3), 'type': 'impact', 'gain': 0.7, 'dur': 0.7})
ev.append({'t': round(s6 + 4 * B + 0.2, 3), 'type': 'chime', 'note': 'D5', 'gain': 0.35})
spec = {'duration': round(DUR, 4), 'seed': 1789, 'bpm': 128, 'key': 'D', 'scale': 'minor',
        'music': {'preset': 'pulse', 'gain': 0.45, 'octave': 3, 'density': 0.6}, 'reverb': 0.14,
        'events': sorted(ev, key=lambda e: e['t'])}
print(json.dumps(spec, ensure_ascii=False, indent=1))
