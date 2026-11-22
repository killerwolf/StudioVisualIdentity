#!/usr/bin/env python3
"""
mesure_ombre.py — mesure SUR L'IMAGE RENDUE la longueur visible de l'ombre de la tour.

On projette l'axe de l'ombre (du pied de la tour vers l'opposé du soleil) dans l'image, on lit la couleur des pixels le long
de cet axe et de deux parallèles témoins (à ±18 unités), et l'on compte comme « ombre » les points nettement plus sombres que
leurs témoins. Sortie : longueur visible en unités monde et en multiples de la hauteur de la tour, et hauteur de la tour en pixels.

  ../.venv/bin/python mesure_ombre.py sortie/tour4/still_4.5s.png 4.5
  options (pour rejouer un ancien tour) : --cam "x,y,yaw0,yaw1,speed,z0,z1,p0,p1" --sun "sx,sy,tan"
"""
import argparse
import math
import sys

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('still')
ap.add_argument('t', type=float)
ap.add_argument('--cam')
ap.add_argument('--sun')
a = ap.parse_args()
import paris as PA  # noqa: E402
V, mq = PA.V, PA.mq
cam = dict(PA.CAM)
sun, tan = PA.SUN, PA.SUN_TAN
if a.cam:
    c = [float(x) for x in a.cam.split(',')]
    cam = {'start': (c[0], c[1]), 'yaw': (c[2], c[3]), 'speed': c[4], 'z': (c[5], c[6]), 'pitch': (c[7], c[8])}
if a.sun:
    s = [float(x) for x in a.sun.split(',')]
    sun, tan = np.array(s[:2]), s[2]
eye, yaw, pitch, roll = V.camera_table(cam, 150)[int(round(a.t * 30))]
f, r, u = mq.basis(yaw, pitch, roll)
vp = mq.view_proj(eye, f, r, u)
img = np.asarray(Image.open(a.still).convert('RGB')).astype(float)
H, W = img.shape[:2]


def px(p):
    q = vp @ np.array([p[0], p[1], p[2], 1.0])
    if q[3] <= 0:
        return None
    x, y = (q[0] / q[3] * 0.5 + 0.5) * W, (0.5 - q[1] / q[3] * 0.5) * H
    return (x, y) if (0 <= x < W and 0 <= y < H) else None


def lum(p):
    q = px(p)
    if q is None:
        return None
    c = img[int(q[1]), int(q[0])]
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


T = np.array(PA.TOWER)
d = -sun / np.linalg.norm(sun)
n = np.array([-d[1], d[0]])
L = PA.TH / tan
base, top = px((T[0], T[1], 0)), px((T[0], T[1], PA.TH))
print('soleil : hauteur %.1f°, ombre théorique %.0f unités = %.1f × la tour' % (math.degrees(math.atan(tan)), L, L / PA.TH))
print('tour dans l\'image : pied', None if base is None else tuple(int(v) for v in base), 'sommet', None if top is None else tuple(int(v) for v in top))
vis = dark = 0
runs, cur = [], 0
for s_ in np.arange(18.0, L, 2.0):
    p = T + d * s_
    l0, l1, l2 = lum((p[0], p[1], 0)), lum((p[0] + n[0] * 18, p[1] + n[1] * 18, 0)), lum((p[0] - n[0] * 18, p[1] - n[1] * 18, 0))
    if l0 is None:
        continue
    vis += 1
    ref = max(v for v in (l1, l2) if v is not None) if (l1 is not None or l2 is not None) else None
    is_dark = ref is not None and l0 < ref - 22
    dark += is_dark
    cur = cur + 2 if is_dark else 0
    runs.append(cur)
print('axe de l\'ombre dans le cadre : %.0f unités sur %.0f' % (vis * 2, L - 18))
print('points plus sombres que leurs témoins : %.0f unités = %.2f × la tour ; plus long tronçon continu : %.0f unités = %.2f × la tour'
      % (dark * 2, dark * 2 / PA.TH, max(runs) if runs else 0, (max(runs) if runs else 0) / PA.TH))
tip = px((T[0] + d[0] * L, T[1] + d[1] * L, 0))
if base and tip and top:
    print('dans l\'image : ombre %.0f px, tour %.0f px' % (math.hypot(tip[0] - base[0], tip[1] - base[1]), math.hypot(top[0] - base[0], top[1] - base[1])))
