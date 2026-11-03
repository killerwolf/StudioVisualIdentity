"""post.py <in.jpg> <out.jpg> — texture risographie (OpenCV + numpy, déterministe).
Speckles blancs dans l'encre (manque d'encre), légère bavure, fibres et grain du papier."""
import sys
import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
img = cv2.imread(src).astype(np.float32) / 255.0
h, w = img.shape[:2]
rng = np.random.default_rng(1977)
paper = np.array([228, 240, 246], np.float32) / 255.0  # BGR du papier #F6F0E4

# bavure d'encre douce
img = cv2.GaussianBlur(img, (0, 0), 0.8)

# couverture d'encre = distance au papier
cov = np.clip(np.linalg.norm(paper - img, axis=2) / 0.9, 0, 1)

# manque d'encre : bruit moyen-fréquence seuillé -> petites zones où l'encre "saute"
n = rng.random((h // 3, w // 3)).astype(np.float32)
n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (w, h), interpolation=cv2.INTER_LINEAR)
skip = np.clip((n - 0.62) * 6, 0, 1) * 0.55
# grandes variations de densité (rouleau inégal)
roll = cv2.resize(rng.random((10, 6)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
roll = (roll - roll.min()) / (np.ptp(roll) + 1e-6)
k = (skip + 0.12 * roll)[..., None] * cov[..., None]
img = img * (1 - k) + paper * k

# grain papier
g = rng.normal(0, 0.022, (h, w)).astype(np.float32)
fib = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.7, sigmaY=5) * 0.03
img += (g + fib)[..., None]

cv2.imwrite(dst, np.clip(img * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
