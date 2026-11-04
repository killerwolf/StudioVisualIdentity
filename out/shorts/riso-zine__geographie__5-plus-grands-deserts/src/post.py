#!/usr/bin/env python3
"""post.py — passe « tirage risographie » (OpenCV + numpy), frame par frame, déterministe. Identité riso-zine.

  video : décode IN.mp4 par un pipe ffmpeg (rawvideo bgr24), traite chaque frame, ré-encode par un second pipe.
      out/tools/slot.sh .venv/bin/python post.py video IN.mp4 OUT.mp4 [--seed 13]
  image : même traitement sur un still (revue avant rendu complet), à l'instant t.
      .venv/bin/python post.py image IN.jpg OUT.jpg --t 3.2

Effets (dans l'ordre) :
  1. feuille qui ondule : petite rotation/translation de toute la page, qui change « on twos » (12 pas/s) ;
  2. bavure d'encre (flou 0,7 px) ;
  3. manques d'encre : 6 cartes de « sauts » pré-tirées, alternées à chaque pas, appliquées ∝ couverture d'encre ;
  4. rouleau inégal : densité basse fréquence fixe ;
  5. grain du papier (6 champs alternés) + fibres fixes + léger voile de papier aux bords.
Imprime un JSON {frames, seconds, secPer100Frames}.
"""
import argparse, json, subprocess, time
import cv2
import numpy as np

W, H, FPS, STEP_FPS = 1080, 1920, 30, 12
PAPER = np.array([228, 240, 246], np.float32)  # BGR de #F6F0E4


class Riso:
    def __init__(self, seed=13):
        rng = np.random.default_rng(seed)
        self.seed = seed
        self.skips = []
        for _ in range(6):
            n = rng.random((H // 3, W // 3)).astype(np.float32)
            n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.3), (W, H), interpolation=cv2.INTER_LINEAR)
            self.skips.append((np.clip((n - 0.6) * 5.5, 0, 1) * 0.6).astype(np.float32))
        roll = cv2.resize(rng.random((9, 5)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
        self.roll = ((roll - roll.min()) / (np.ptp(roll) + 1e-6) * 0.14).astype(np.float32)
        self.grains = [rng.normal(0, 0.024 * 255, (H, W)).astype(np.float32) for _ in range(6)]
        fib = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=0.7, sigmaY=6)
        self.fib = (fib * 0.03 * 255).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        self.vig = (1.0 - 0.06 * np.clip(d - 0.7, 0, 1))[..., None].astype(np.float32)

    def wobble(self, k):
        r = np.random.default_rng(self.seed * 1000 + k)
        ang = float(r.normal(0, 0.18))            # degrés
        dx, dy = float(r.normal(0, 2.2)), float(r.normal(0, 2.2))
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.012)
        M[0, 2] += dx; M[1, 2] += dy
        return M

    def process(self, bgr, f):
        k = int(f * STEP_FPS / FPS + 1e-6)                  # pas « on twos »
        img = cv2.warpAffine(bgr, self.wobble(k), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        img = cv2.GaussianBlur(img, (0, 0), 0.7).astype(np.float32)
        cov = np.clip(np.abs(PAPER - img).sum(axis=2) / 330.0, 0, 1)
        kmap = (self.skips[k % 6] + self.roll) * cov
        img += (PAPER - img) * kmap[..., None]
        img += (self.grains[k % 6] + self.fib)[..., None]
        img *= self.vig
        return np.clip(img, 0, 255).astype(np.uint8)


def run_video(a):
    rz = Riso(a.seed)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', a.inp, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out],
                           stdin=subprocess.PIPE)
    t0 = time.time(); n = 0; fsz = W * H * 3
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        enc.stdin.write(rz.process(np.frombuffer(buf, np.uint8).reshape(H, W, 3), n).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    secs = time.time() - t0
    print(json.dumps({'mode': 'video', 'frames': n, 'seconds': round(secs, 1), 'secPer100Frames': round(secs / max(n, 1) * 100, 1)}))


def run_image(a):
    img = cv2.imread(a.inp)
    cv2.imwrite(a.out, Riso(a.seed).process(img, int(round(a.t * FPS))), [cv2.IMWRITE_JPEG_QUALITY, 92])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['video', 'image'])
    p.add_argument('inp'); p.add_argument('out')
    p.add_argument('--seed', type=int, default=13)
    p.add_argument('--t', type=float, default=0.0)
    a = p.parse_args()
    run_video(a) if a.mode == 'video' else run_image(a)
