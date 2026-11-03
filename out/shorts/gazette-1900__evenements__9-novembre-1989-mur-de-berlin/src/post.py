#!/usr/bin/env python3
"""post.py — post-traitement « Gazette 1900 » (OpenCV + numpy), frame par frame, déterministe.

  video : décode IN.mp4 via un pipe ffmpeg (rawvideo bgr24), traite chaque frame, ré-encode via un second pipe.
      out/tools/slot.sh .venv/bin/python post.py video IN.mp4 OUT.mp4 [--seed 1900] [--flash 0.0,2.8]
  image : même traitement sur un still (pour la revue avant rendu complet), à l'instant t.
      .venv/bin/python post.py image IN.jpg OUT.jpg --t 3.2

Effets (dans l'ordre) : gate weave (tremblement de projecteur, warpAffine), bavure d'encre (érosion 2×2 mélangée),
virage sépia + taches de papier basse fréquence + fibres + vignette (carte multiplicative fixe), scintillement global
(flicker lissé + creux rares), grain de film (12 champs pré-tirés), rayures verticales qui vivent quelques frames,
poussières et cheveux occasionnels, flash blanc bref sur les coupes (--flash).
Imprime un JSON {frames, seconds, secPer100Frames}.
"""
import argparse, json, subprocess, sys, time
import cv2
import numpy as np

W, H, FPS = 1080, 1920, 30


class Film:
    def __init__(self, seed=1900, flashes=()):
        self.seed = seed
        rng = np.random.default_rng(seed)
        self.flashes = list(flashes)
        # --- carte multiplicative fixe : sépia + taches + fibres + vignette ---
        blot = cv2.resize(rng.random((24, 14)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
        blot = cv2.GaussianBlur(blot, (0, 0), 40)
        blot = (blot - blot.min()) / (np.ptp(blot) + 1e-6)
        sepia = np.array([0.80, 0.90, 1.0], np.float32)  # BGR : le bleu baisse => jaunit
        stain = 1.0 - 0.10 * blot[..., None] * (1.0 - sepia * 0.6)
        tone = np.array([0.955, 0.985, 1.0], np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        vig = (1.0 - 0.30 * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None]
        self.mult = (stain * tone * vig).astype(np.float32)
        fib = rng.normal(0, 1, (H, W)).astype(np.float32)
        fib = cv2.GaussianBlur(fib, (0, 0), sigmaX=6, sigmaY=0.8)
        self.fib = (fib * 0.035 * 255).astype(np.float32)
        # --- grains pré-tirés ---
        self.grains = [rng.normal(0, 0.042 * 255, (H, W)).astype(np.float32) for _ in range(12)]
        self.kernel = np.ones((2, 2), np.uint8)
        self.state_rng = np.random.default_rng(seed + 1)
        self.scratches = []
        self.frame = -1

    def _flicker(self, f):
        t = f / FPS
        v = 0.022 * np.sin(t * 2 * np.pi * 7.3) + 0.016 * np.sin(t * 2 * np.pi * 11.1 + 1.3) + 0.012 * np.sin(t * 2 * np.pi * 2.9)
        if (f * 2654435761 + self.seed) % 97 < 3:  # creux rares
            v -= 0.06
        return 1.0 + v

    def _weave(self, f):
        t = f / FPS
        dx = 1.4 * np.sin(t * 5.1) + 0.8 * np.sin(t * 13.7 + 0.4)
        dy = 1.8 * np.sin(t * 3.3 + 1.0) + 0.9 * np.sin(t * 17.9)
        return float(dx), float(dy)

    def _step_state(self, f):
        """avance l'état (rayures, poussières) jusqu'à la frame f — séquentiel donc déterministe."""
        out = None
        while self.frame < f:
            self.frame += 1
            r = self.state_rng
            self.scratches = [s for s in self.scratches if s['life'] > 0]
            for s in self.scratches:
                s['life'] -= 1; s['x'] += s['drift'] + r.normal(0, 0.6)
            if r.random() < 0.22 and len(self.scratches) < 3:
                self.scratches.append({'x': float(r.uniform(40, W - 40)), 'life': int(r.integers(3, 16)), 'drift': float(r.normal(0, 0.8)),
                                       'y0': int(r.integers(0, H // 3)), 'y1': int(r.integers(H // 2, H)), 'a': float(r.uniform(0.25, 0.6)),
                                       'light': bool(r.random() < 0.6)})
            dust = []
            for _ in range(int(r.poisson(1.6))):
                dust.append((int(r.integers(0, W)), int(r.integers(0, H)), int(r.integers(2, 7)), int(r.integers(2, 5)), float(r.uniform(0, 3.14)), bool(r.random() < 0.7)))
            hair = None
            if r.random() < 0.04:
                x0, y0 = r.uniform(100, W - 100), r.uniform(200, H - 200)
                pts = [(x0, y0)]
                a = r.uniform(0, 6.28)
                for _ in range(14):
                    a += r.normal(0, 0.35); x0 += np.cos(a) * 9; y0 += np.sin(a) * 9; pts.append((x0, y0))
                hair = np.array(pts, np.int32)
            out = (dust, hair)
        return out

    def process(self, bgr, f):
        dust, hair = self._step_state(f)
        dx, dy = self._weave(f)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        img = cv2.warpAffine(bgr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        ink = cv2.erode(img, self.kernel)
        img = cv2.addWeighted(img, 0.55, ink, 0.45, 0)
        x = img.astype(np.float32)
        x *= self.mult
        x *= self._flicker(f)
        g = self.grains[(f * 7 + 3) % len(self.grains)]
        x += (g + self.fib)[..., None]
        for s in self.scratches:
            c = (255 * (0.9 + s['a'] * 0.1),) * 3 if s['light'] else (40.0,) * 3
            cv2.line(x, (int(s['x']), s['y0']), (int(s['x'] + s['drift'] * 6), s['y1']), c, 1, cv2.LINE_AA)
        for (px, py, ax, ay, ang, dark) in dust:
            cv2.ellipse(x, (px, py), (ax, ay), np.degrees(ang), 0, 360, (30.0,) * 3 if dark else (245.0,) * 3, -1, cv2.LINE_AA)
        if hair is not None:
            cv2.polylines(x, [hair], False, (25.0,) * 3, 1, cv2.LINE_AA)
        t = f / FPS
        for ft in self.flashes:  # flash de coupe : 2 frames surexposées
            k = (t - ft) * FPS
            if 0 <= k < 2:
                x = x * (1.25 - 0.1 * k) + 18
        return np.clip(x, 0, 255).astype(np.uint8)


def run_video(a):
    film = Film(a.seed, [float(v) for v in a.flash.split(',')] if a.flash else [])
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', a.inp, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out],
                           stdin=subprocess.PIPE)
    t0 = time.time(); n = 0; fsz = W * H * 3
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        enc.stdin.write(film.process(frame, n).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    secs = time.time() - t0
    print(json.dumps({'mode': 'video', 'frames': n, 'seconds': round(secs, 1), 'secPer100Frames': round(secs / max(n, 1) * 100, 1)}))


def run_image(a):
    film = Film(a.seed, [float(v) for v in a.flash.split(',')] if a.flash else [])
    img = cv2.imread(a.inp)
    img = cv2.resize(img, (W, H)) if img.shape[:2] != (H, W) else img
    cv2.imwrite(a.out, film.process(img, int(round(a.t * FPS))), [cv2.IMWRITE_JPEG_QUALITY, 92])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['video', 'image'])
    p.add_argument('inp'); p.add_argument('out')
    p.add_argument('--seed', type=int, default=1900)
    p.add_argument('--t', type=float, default=0.0)
    p.add_argument('--flash', default='')
    a = p.parse_args()
    run_video(a) if a.mode == 'video' else run_image(a)
