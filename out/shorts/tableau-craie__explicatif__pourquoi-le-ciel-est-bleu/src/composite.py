"""composite.py — pose les overlays PNG (grain de craie + textes Caveat/Nunito) sur la vidéo Manim, frame par frame (numpy).
Plus rapide que 18 entrées -loop d'ffmpeg sous contention CPU. Mêmes règles de fondu que assemble.py --overlay
(fondu alpha linéaire d'entrée/sortie, actif sur [t0, t1]).
usage : python composite.py video_manim.mp4 overlays.txt out.mp4 [duration]
"""
import sys, subprocess
import numpy as np
from PIL import Image

W, H = 1080, 1920
FPS = int(sys.argv[5]) if len(sys.argv) > 5 else 30
src, ovl, out = sys.argv[1:4]
dur = float(sys.argv[4]) if len(sys.argv) > 4 else None
layers = []
for line in open(ovl).read().split():
    path, t0, t1, fd = line.rsplit(':', 3)
    a = np.asarray(Image.open(path).convert('RGBA'))
    ys, xs = np.nonzero(a[..., 3])
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = a[y0:y1, x0:x1].astype(np.float32)
    layers.append(dict(t0=float(t0), t1=float(t1), fd=max(float(fd), 1e-3), box=(y0, y1, x0, x1),
                       rgb=crop[..., :3], a=crop[..., 3:4] / 255.0))
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc_cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if dur:
    enc_cmd += ['-t', f'{dur:.3f}']
enc = subprocess.Popen(enc_cmd + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = n / FPS
    if dur and t >= dur:
        break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    for L in layers:
        if not (L['t0'] <= t <= L['t1']):
            continue
        k = min(1.0, (t - L['t0']) / L['fd'], (L['t1'] - t) / L['fd'])
        if k <= 0:
            continue
        y0, y1, x0, x1 = L['box']
        a = L['a'] * k
        fr[y0:y1, x0:x1] = fr[y0:y1, x0:x1] * (1 - a) + L['rgb'] * a
    enc.stdin.write(fr.clip(0, 255).astype(np.uint8).tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(f'{n} frames -> {out}')
