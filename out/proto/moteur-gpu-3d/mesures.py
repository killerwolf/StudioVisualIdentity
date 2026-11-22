#!/usr/bin/env python3
"""
mesures.py — compare des séries d'images natives (indices de palette, .npy écrits par proto.py --dump).

  .venv/bin/python mesures.py ecart a.npy b.npy     # pixels différents entre deux rendus (par image et au total)
  .venv/bin/python mesures.py aba a.npy [b.npy …]   # scintillement A-B-A : même pixel, 3 images consécutives,
                                                    # image n = image n+2 mais ≠ image n+1 (indices exacts, natif)
"""
import json
import sys

import numpy as np


def ecart(a, b):
    a, b = np.load(a), np.load(b)
    d = a != b
    per = d.reshape(len(a), -1).mean(axis=1) * 100
    return {'images': int(len(a)), 'pixelsDifferents': int(d.sum()), 'pixelsTotal': int(d.size),
            'partPct': round(float(d.mean() * 100), 4), 'pireImagePct': round(float(per.max()), 4),
            'imagesIdentiques': int((per == 0).sum())}


def aba(a):
    f = np.load(a)
    x = (f[:-2] == f[2:]) & (f[:-2] != f[1:-1])
    per = x.reshape(len(x), -1).mean(axis=1) * 100
    ch = (f[1:] != f[:-1]).reshape(len(f) - 1, -1).mean(axis=1) * 100
    return {'abaMoyenPct': round(float(per.mean()), 3), 'abaMaxPct': round(float(per.max()), 3),
            'pixelsQuiChangentParImagePct': round(float(ch.mean()), 2)}


if __name__ == '__main__':
    if sys.argv[1] == 'ecart':
        print(json.dumps(ecart(sys.argv[2], sys.argv[3]), ensure_ascii=False))
    else:
        for p in sys.argv[2:]:
            print(p.split('/')[-1], json.dumps(aba(p), ensure_ascii=False))
