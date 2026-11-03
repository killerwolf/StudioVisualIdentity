"""post.py <in.jpg> <out.jpg> — papier aquarelle grain fin (OpenCV + numpy, déterministe).
Relief de papier (bruit multi-échelle "embossé" par la lumière), pigment qui se dépose dans les creux,
vignette chaude très douce."""
import sys
import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
img = cv2.imread(src).astype(np.float32) / 255.0
h, w = img.shape[:2]
rng = np.random.default_rng(31)

# hauteur du papier : somme de bruits flous (grain cold-press)
hgt = np.zeros((h, w), np.float32)
for s, a in [(1.2, .5), (3.0, .35), (8.0, .25)]:
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    hgt += cv2.GaussianBlur(n, (0, 0), s) * a * s
hgt = (hgt - hgt.mean()) / (hgt.std() + 1e-6)
# éclairage rasant : dérivée de la hauteur
light = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) * .6 + cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) * .4
light = light / (np.abs(light).max() + 1e-6)
img *= (1 + light[..., None] * 0.07)

# pigment granulé : là où il y a de la couleur, les creux foncent un peu
paper = np.array([230, 241, 247], np.float32) / 255.0
cov = np.clip(np.linalg.norm(paper - img, axis=2) / 0.6, 0, 1)
img *= (1 - np.clip(-hgt, 0, 3)[..., None] * 0.035 * cov[..., None])

# vignette chaude
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
d = np.sqrt(((xx - w / 2) / (w * .7)) ** 2 + ((yy - h / 2) / (h * .7)) ** 2)
v = np.clip(d - .6, 0, 1) ** 2
img *= (1 - v[..., None] * np.array([.10, .14, .18], np.float32))

cv2.imwrite(dst, np.clip(img * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
