"""post.py <in.jpg> <out.jpg> — vieillissement "Gazette 1900" (OpenCV + numpy, déterministe).
Taches de papier basse fréquence, bavure d'encre, grain de film, rayures verticales, vignette."""
import sys
import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
img = cv2.imread(src).astype(np.float32) / 255.0
h, w = img.shape[:2]
rng = np.random.default_rng(1900)

# bavure d'encre : les zones sombres s'épaississent légèrement (érosion du clair)
ink = cv2.erode(img, np.ones((2, 2), np.uint8))
img = img * 0.55 + ink * 0.45

# taches de papier : bruit basse fréquence multiplié, teinté sépia
blot = cv2.resize(rng.random((24, 14)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
blot = cv2.GaussianBlur(blot, (0, 0), 40)
blot = (blot - blot.min()) / (np.ptp(blot) + 1e-6)
sepia = np.array([0.80, 0.90, 1.0], np.float32)  # BGR : assombrit le bleu => jaunit
stain = 1.0 - 0.10 * blot[..., None] * (1.0 - sepia * 0.6)
img *= stain

# fibres du papier
fib = rng.normal(0, 1, (h, w)).astype(np.float32)
fib = cv2.GaussianBlur(fib, (0, 0), sigmaX=6, sigmaY=0.8)
img += fib[..., None] * 0.035

# grain de film
grain = rng.normal(0, 0.045, (h, w)).astype(np.float32)
img += grain[..., None]

# rayures verticales de projecteur
for _ in range(5):
    x = int(rng.integers(40, w - 40)); a = float(rng.uniform(0.04, 0.10))
    y0 = int(rng.integers(0, h // 2)); y1 = int(rng.integers(h // 2, h))
    cv2.line(img, (x, y0), (x + int(rng.integers(-6, 6)), y1), (a + 0.9,) * 3 if rng.random() < .5 else (0.2,) * 3, 1)

# vignette
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
d = np.sqrt(((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.62)) ** 2)
img *= (1.0 - 0.28 * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None]

out = np.clip(img * 255, 0, 255).astype(np.uint8)
cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 94])
