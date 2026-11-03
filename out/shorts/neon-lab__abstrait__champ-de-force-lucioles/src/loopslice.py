#!/usr/bin/env python3
"""loopslice.py in.wav out.wav START END — garde [START,END) d'un WAV rendu sur 3 cycles identiques -> boucle parfaite
(les queues de son du cycle précédent sont déjà présentes au début de la tranche). Renormalise la crête à -1 dBFS."""
import sys
import numpy as np
from scipy.io import wavfile
sr, x = wavfile.read(sys.argv[1]); a, b = int(float(sys.argv[3]) * sr), int(float(sys.argv[4]) * sr)
y = x[a:b].astype(np.float32)
peak = np.max(np.abs(y)) or 1.0
full = 32767 if x.dtype == np.int16 else 1.0
y = y / peak * full * 10 ** (-1 / 20)
wavfile.write(sys.argv[2], sr, y.astype(x.dtype))
print(f'loop slice {sys.argv[3]}-{sys.argv[4]} s, {len(y)/sr:.3f} s')
