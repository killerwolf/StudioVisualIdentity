#!/usr/bin/env python3
"""
neon_grade.py — post-traitement OpenCV « neon grade » de l'identité Labo Néon (identique dans les 2 shorts).

  .venv/bin/python neon_grade.py in.mp4 out.mp4 [--glow 0.55] [--ca 0.0022] [--vignette 0.22]

Par frame (déterministe, sans aléa) :
  1. glow : seuil doux des hautes lumières -> réduction 1/4 -> 2 flous gaussiens (σ 6 et 18 px à 1/4) -> addition (screen)
  2. aberration chromatique radiale : R agrandi de (1+ca), B réduit de (1-ca) autour du centre (warpAffine) ;
     0 px au centre, ≈ 2,4 px dans les coins pour ca=0.0022 -> le texte central reste net
  3. vignette douce (multiplication par un masque radial précalculé)
Lecture cv2.VideoCapture, écriture par pipe rawvideo -> ffmpeg libx264 crf 14 yuv420p 30 fps.
"""
import argparse, subprocess, sys, time
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('inp'); ap.add_argument('out')
ap.add_argument('--glow', type=float, default=0.55)
ap.add_argument('--ca', type=float, default=0.0022)
ap.add_argument('--vignette', type=float, default=0.22)
a = ap.parse_args()

cap = cv2.VideoCapture(a.inp)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cx, cy = W / 2, H / 2
def scale_m(s):
    return np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
MR, MB = scale_m(1 + a.ca), scale_m(1 - a.ca)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - cx) / (W * 0.5)) ** 2 + ((yy - cy) / (H * 0.5)) ** 2) / np.sqrt(2)
vig = (1.0 - a.vignette * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6).astype(np.float32)[..., None]

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30',
                       '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '30', a.out],
                      stdin=subprocess.PIPE)
t0 = time.time(); n = 0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    f = fr.astype(np.float32) / 255.0
    # 1. glow
    lum = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    mask = np.clip((lum - 0.42) / 0.45, 0, 1)[..., None]
    small = cv2.resize(f * mask, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(small, (0, 0), 6) * 0.6 + cv2.GaussianBlur(small, (0, 0), 18) * 0.4
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    f = 1.0 - (1.0 - f) * (1.0 - np.clip(g * a.glow * 1.6, 0, 1))
    # 2. aberration chromatique radiale
    b, gch, rch = cv2.split(f)
    rch = cv2.warpAffine(rch, MR, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    b = cv2.warpAffine(b, MB, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    f = cv2.merge([b, gch, rch])
    # 3. vignette
    f = f * vig
    ff.stdin.write((np.clip(f, 0, 1) * 255.0 + 0.5).astype(np.uint8).tobytes())
    n += 1
ff.stdin.close(); ff.wait()
dt = time.time() - t0
print(f'{{"frames": {n}, "seconds": {dt:.1f}, "secPer100Frames": {dt / max(n, 1) * 100:.1f}}}')
