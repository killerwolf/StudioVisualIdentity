#!/usr/bin/env python3
"""voix.py — reconstruit la piste de voix seule de l'essai C2 à partir des voix existantes de swiss-data (aucun nouvel appel).

Même placement que out/tools/tts.py --engine files : chaque voice_lines/NN.mp3 de
out/shorts/swiss-data__geographie__ou-vivent-8-milliards est rogné de ses silences (seuil 0,01), accéléré (atempo ≤ 1,35) s'il
dépasse maxDuration, posé à son temps t de narration.json, puis la piste est normalisée en crête à 0,89. Sans musique.
Depuis le 20/11/2026 (version adoptée) : la réplique 1 « Un carré, cent millions d'humains » n'est plus posée (plus de carrés à
l'image : l'échelle « 100 % = 8 Md » s'écrit sans voix) et les répliques 2 à 5 sont avancées de 1,2 s (POSE ci-dessous).
usage : python3 voix.py <sortie.wav>   (numpy ; ffmpeg)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR = 44100
SRC = Path(__file__).resolve().parents[2] / 'swiss-data__geographie__ou-vivent-8-milliards'


def lit(f, filtre=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(f)] + (['-filter:a', filtre] if filtre else []) + ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


nar = json.load(open(SRC / 'narration.json'))
POSE = {0: 0.3, 2: 4.35, 3: 6.0, 4: 7.7, 5: 10.5}   # réplique -> temps de pose dans C2 (1 : retirée)
dur = 13.8
piste = np.zeros(int((dur + 1) * SR), np.float32)
for i, ln in enumerate(nar['lines']):
    if i not in POSE:
        continue
    f = SRC / 'voice_lines' / f'{i:02d}.mp3'
    x = lit(f)
    idx = np.where(np.abs(x) > 0.01)[0]
    a, b = (max(0, idx[0] - 480), idx[-1] + 2400) if len(idx) else (0, len(x))
    if (b - a) / SR > ln['maxDuration']:
        fac = min(1.35, (b - a) / SR / ln['maxDuration'])
        x = lit(f, f'atrim=start_sample={a}:end_sample={b},atempo={fac:.3f}')
    else:
        x = x[a:b]
    s = int(POSE[i] * SR)
    e = min(len(piste), s + len(x))
    piste[s:e] += x[:e - s]
piste = piste[:int(dur * SR)]
piste = piste / (np.max(np.abs(piste)) + 1e-9) * 0.89
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-i', '-', '-ac', '2', sys.argv[1]],
               input=piste.astype(np.float32).tobytes(), check=True)
print('voix :', sys.argv[1], f'{dur} s')
