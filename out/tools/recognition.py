#!/usr/bin/env python3
"""
recognition.py — test de reconnaissance « à l'aveugle » (mesuré, pas déclaratif).

USAGE
  .venv/bin/python out/tools/recognition.py            # -> out/report/recognition.json + résumé
  .venv/bin/python out/tools/recognition.py --blind-pack /tmp/blind   # prépare un paquet anonymisé pour un juge

Méthode (signature visuelle par short) :
  - 8 frames échantillonnées uniformément dans short.mp4 (de 8 % à 92 % de la durée), réduites à 96×170.
  - descripteur = histogramme couleur Lab 3D (8×8×8, normalisé) + histogramme de gradients (densité de bords, 16 bins)
  - distance entre shorts = distance de Bhattacharyya moyenne (couleur) + 0,5 × distance chi² (bords).
  Pour chaque short on cherche son plus proche voisin parmi TOUS les autres shorts : le test est réussi si ce voisin
  appartient à la même identité (précision top-1). On rapporte aussi le ratio distance intra / distance inter.
Le paquet --blind-pack copie 2 frames par short sous des noms aléatoires (graine fixe) + une clé séparée.
"""
import json, random, subprocess, sys, shutil
from pathlib import Path
import numpy as np, cv2

ROOT = Path(__file__).resolve().parents[2]


def frames(mp4, n=8):
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)]))
    out = []
    for k in range(n):
        t = dur * (0.08 + 0.84 * k / (n - 1))
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', str(mp4), '-frames:v', '1',
                                       '-vf', 'scale=96:170', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'])
        out.append(np.frombuffer(raw, np.uint8).reshape(170, 96, 3))
    return out


def descriptor(fr):
    hs, es = [], []
    for f in fr:
        lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB)
        h = cv2.calcHist([lab], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]).flatten()
        hs.append(h / (h.sum() + 1e-9))
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        mag = np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
        e, _ = np.histogram(np.clip(mag, 0, 400), bins=16, range=(0, 400))
        es.append(e / (e.sum() + 1e-9))
    return np.mean(hs, 0), np.mean(es, 0)


def dist(a, b):
    bc = np.sum(np.sqrt(a[0] * b[0]))
    bhat = np.sqrt(max(0.0, 1 - bc))
    chi = 0.5 * np.sum((a[1] - b[1]) ** 2 / (a[1] + b[1] + 1e-9))
    return float(bhat + 0.5 * chi)


def main():
    dirs = sorted(d for d in (ROOT / 'out/shorts').iterdir() if (d / 'short.mp4').exists())
    if len(sys.argv) > 2 and sys.argv[1] == '--blind-pack':
        dst = Path(sys.argv[2]); shutil.rmtree(dst, ignore_errors=True); dst.mkdir(parents=True)
        rnd = random.Random(2026)
        items = []
        for d in dirs:
            for k, t in enumerate((0.35, 0.7)):
                items.append((d.name, t))
        names = rnd.sample(range(1000, 9999), len(items))
        key = {}
        for (name, t), code in zip(items, names):
            mp4 = ROOT / 'out/shorts' / name / 'short.mp4'
            dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)]))
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{dur * t:.2f}', '-i', str(mp4), '-frames:v', '1', '-vf', 'scale=360:-1',
                            str(dst / f'img_{code}.jpg')], check=True)
            key[f'img_{code}.jpg'] = name
        (dst.parent / (dst.name + '_KEY.json')).write_text(json.dumps(key, indent=1))
        print(f'{len(key)} images -> {dst} ; clé -> {dst.parent / (dst.name + "_KEY.json")}')
        return
    ident = [d.name.split('__')[0] for d in dirs]
    desc = [descriptor(frames(d / 'short.mp4')) for d in dirs]
    n = len(dirs)
    D = np.array([[dist(desc[i], desc[j]) for j in range(n)] for i in range(n)])
    hits, rows = 0, []
    intra, inter = [], []
    for i in range(n):
        order = [j for j in np.argsort(D[i]) if j != i]
        nn = order[0]
        ok = ident[nn] == ident[i]
        hits += ok
        rows.append({'short': dirs[i].name, 'nearest': dirs[nn].name, 'sameIdentity': bool(ok), 'distance': round(D[i, nn], 4)})
        for j in range(n):
            if j != i:
                (intra if ident[j] == ident[i] else inter).append(D[i, j])
    res = {'method': 'Lab 8x8x8 Bhattacharyya + edge-histogram chi2, 8 frames/short, nearest neighbour',
           'shorts': n, 'top1Accuracy': round(hits / n, 3), 'meanIntra': round(float(np.mean(intra)), 4),
           'meanInter': round(float(np.mean(inter)), 4), 'ratioIntraOverInter': round(float(np.mean(intra) / np.mean(inter)), 3),
           'rows': rows}
    old = ROOT / 'out/report/recognition.json'
    if old.exists():  # conserve les résultats des juges aveugles (ajoutés à part : blindJudge, blindJudge14, …)
        prev = json.loads(old.read_text())
        for k, v in prev.items():
            if k.startswith('blindJudge'):
                res[k] = v
    (ROOT / 'out/report/recognition.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(f"top-1 = {hits}/{n} ({hits / n:.0%}) ; intra moyen {res['meanIntra']} vs inter {res['meanInter']} (ratio {res['ratioIntraOverInter']})")
    for r in rows:
        if not r['sameIdentity']:
            print('  ÉCHEC', r['short'], '->', r['nearest'])


if __name__ == '__main__':
    main()
