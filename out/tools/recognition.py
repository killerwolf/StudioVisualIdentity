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
Un short seul de son identité (préfixe neuf : recette née d'une case de la matrice, ex. chemin-grille-suisse) n'a aucun
voisin possible de même identité : il est marqué `sansPair` et sorti du score top-1 (ce n'est pas un échec).

MODE --briques (2026-11-20, migration.md étape 5 ; proposition.md § 8) :
  .venv/bin/python out/tools/recognition.py --briques   # -> out/report/recognition-briques.json (recognition.json intact)
  Reconnaissance à deux étages, clés lues par out/tools/briques.py (etiquettes.json, puis short.json, puis recette) :
  1. HABILLAGE : le descripteur d'apparence ci-dessus (inchangé) ; clé = pâte (grille-suisse, craie/ardoise…).
  2. MÉCANIQUE : descripteur temporel neuf, sur toutes les images à 30 i/s, en niveaux de gris 108×192 (l'apparence ne
     compte plus) : énergie de différence image à image (médiane, p90, dispersion), part des images tenues et longueur des
     tenues (cadence 12 i/s, « on twos »), taux de coupes, part de l'image qui bouge, mouvement global par corrélation de
     phase (vitesse de caméra, part des images où la caméra bouge, cohérence), énergie résiduelle après compensation du
     mouvement global (caméra contre animation locale). Chaque composante est centrée-réduite sur l'ensemble des shorts ;
     distance euclidienne.
  Pour chaque étage : précision top-1 (le plus proche voisin a la même clé) sur les shorts qui ont au moins un pair ; les
  shorts seuls de leur clé sont listés `sansPair`. Les shorts d'une recette abandonnée (C4) sont exclus de tous les scores
  et listés à part. Tests croisés (ceux qui comptent) : habillage reconnu ENTRE mécaniques différentes (voisin cherché
  parmi les shorts d'une autre mécanique) et mécanique reconnue ENTRE habillages différents (voisin cherché parmi les
  shorts d'un autre habillage), refaits sans les shorts du même sujet (`autreSujet` : les 4 papiers rendent les mêmes
  épisodes, on vérifie que c'est le mouvement et pas l'épisode qui est reconnu). Voisinage (§ 8.3) : paires d'habillages plus proches que la distance moyenne intra-habillage.
"""
import json, random, subprocess, sys, shutil
from pathlib import Path
import numpy as np, cv2

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import briques as B  # noqa: E402


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


# ---------- mode --briques : descripteur de mécanique ----------
MW, MH = 108, 192


def gray_frames(mp4):
    """toutes les images à leur cadence native, niveaux de gris MW×MH (float32)."""
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(mp4), '-an', '-vf', f'scale={MW}:{MH}:flags=area,format=gray',
                                   '-f', 'rawvideo', '-pix_fmt', 'gray', '-'])
    return np.frombuffer(raw, np.uint8).reshape(-1, MH, MW).astype(np.float32)


def motion_descriptor(g, fps=30.0):
    d = np.abs(np.diff(g, axis=0))                     # T-1 × H × W
    e = d.mean(axis=(1, 2))                            # énergie de différence par image
    held = e < 0.35                                    # image tenue (aucun changement visible à cette échelle)
    runs, k = [], 0                                    # longueurs des tenues (cadence)
    for h in held:
        if h: k += 1
        elif k: runs.append(k); k = 0
    if k: runs.append(k)
    runs = np.array(runs) if runs else np.zeros(1)
    le = np.log1p(e)
    cuts = (e > max(25.0, np.median(e) * 8)).sum()
    moving = (d > 12).mean(axis=(1, 2))                # part de l'image qui bouge
    win = cv2.createHanningWindow((MW, MH), cv2.CV_32F)
    shifts, resp, resid = [], [], []
    for t in range(1, len(g)):
        if held[t - 1]:
            continue
        (dx, dy), r = cv2.phaseCorrelate(g[t - 1], g[t], win)
        shifts.append(np.hypot(dx, dy)); resp.append(r)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        warped = cv2.warpAffine(g[t - 1], M, (MW, MH), borderMode=cv2.BORDER_REPLICATE)
        resid.append(np.abs(g[t] - warped)[8:-8, 8:-8].mean() / (e[t - 1] + 1e-6))
    shifts, resp, resid = (np.array(x) if x else np.zeros(1) for x in (shifts, resp, resid))
    cam = shifts > 0.3
    return np.array([
        np.median(le), np.percentile(le, 90), le.std(),          # énergie
        held.mean(), np.mean(np.clip(runs, 0, 6)), np.mean(runs == 1) if runs.size else 0, np.mean((runs >= 2) & (runs <= 3)),  # cadence
        cuts / (len(g) / fps),                                   # coupes par seconde
        moving.mean(), np.percentile(moving, 90),                # part de l'image qui bouge
        np.log1p(np.median(shifts)), cam.mean(), np.median(resp),  # caméra
        np.median(np.clip(resid, 0, 3)),                         # résidu après compensation
    ], dtype=np.float64)


MOTION_FEATURES = ['diff_med', 'diff_p90', 'diff_std', 'held_frac', 'held_run_mean', 'run1_frac', 'run23_frac', 'cuts_per_s',
                   'moving_mean', 'moving_p90', 'cam_speed', 'cam_frac', 'cam_coherence', 'residual']


def _nn(D, i, pool):
    c = [j for j in pool if j != i]
    return min(c, key=lambda j: D[i, j]) if c else None


def evaluate(D, keys, pool, names, other=None):
    """top-1 sur le pool (shorts avec pair) ; `other` = clé de l'autre étage pour les tests croisés."""
    rows, hits, n = [], 0, 0
    intra, inter = [], []
    for i in pool:
        same = [j for j in pool if j != i and keys[j] == keys[i]]
        nn = _nn(D, i, pool)
        row = {'short': names[i], 'cle': keys[i], 'voisin': names[nn], 'cleVoisin': keys[nn], 'distance': round(float(D[i, nn]), 4)}
        if not same:
            row['sansPair'] = True
        else:
            ok = keys[nn] == keys[i]
            row['reconnu'] = bool(ok); hits += ok; n += 1
        for j in pool:
            if j != i:
                (intra if keys[j] == keys[i] else inter).append(D[i, j])
        if other is not None:   # test croisé : voisin cherché parmi les shorts dont l'autre clé diffère
            cross_pool = [j for j in pool if other[j] != other[i]]
            if any(keys[j] == keys[i] for j in cross_pool):
                cn = _nn(D, i, cross_pool)
                rank = sorted(cross_pool, key=lambda j: D[i, j]).index(cn)
                first = min((sorted(cross_pool, key=lambda j: D[i, j]).index(j) + 1 for j in cross_pool if keys[j] == keys[i]))
                row['croise'] = {'voisin': names[cn], 'cleVoisin': keys[cn], 'reconnu': keys[cn] == keys[i],
                                 'rangDuPremierPair': first, 'candidats': len(cross_pool)}
                # contrôle : sans les shorts du même sujet (les 4 papiers rendent les 2 mêmes épisodes) — reconnaît-on
                # la mécanique, ou seulement l'épisode ?
                sujet = lambda k: names[k].split('__')[-1]
                strict = [j for j in cross_pool if sujet(j) != sujet(i)]
                if any(keys[j] == keys[i] for j in strict):
                    sn = _nn(D, i, strict)
                    row['croise']['autreSujet'] = {'voisin': names[sn], 'reconnu': keys[sn] == keys[i]}
        rows.append(row)
    cross = [r for r in rows if 'croise' in r]
    return {'top1': f'{hits}/{n}', 'top1Accuracy': round(hits / n, 3) if n else None,
            'sansPair': [r['short'] for r in rows if r.get('sansPair')],
            'meanIntra': round(float(np.mean(intra)), 4) if intra else None, 'meanInter': round(float(np.mean(inter)), 4),
            'ratioIntraOverInter': round(float(np.mean(intra) / np.mean(inter)), 3) if intra else None,
            'croise': {'reussis': f"{sum(r['croise']['reconnu'] for r in cross)}/{len(cross)}",
                       'reussisAutreSujet': f"{sum(r['croise']['autreSujet']['reconnu'] for r in cross if 'autreSujet' in r['croise'])}/{sum(1 for r in cross if 'autreSujet' in r['croise'])}",
                       'lignes': [{'short': r['short'], 'cle': r['cle'], **r['croise']} for r in cross]},
            'echecs': [{'short': r['short'], 'cle': r['cle'], 'voisin': r['voisin'], 'cleVoisin': r['cleVoisin']} for r in rows if r.get('reconnu') is False],
            'rows': rows}


def main_briques():
    dirs = sorted(d for d in (ROOT / 'out/shorts').iterdir() if (d / 'short.mp4').exists())
    names = [d.name for d in dirs]
    bq = [B.briques_du_short(n) for n in names]
    pate = [b['pate'] for b in bq]; mec = [b['mecanique'] for b in bq]
    excl = [i for i, b in enumerate(bq) if b['statut'] == 'abandonnee']
    pool = [i for i in range(len(dirs)) if i not in excl]
    n = len(dirs)
    print(f'{n} shorts ; exclus (recette abandonnée) : {[names[i] for i in excl]}', flush=True)
    app = []
    mot = []
    for k, d in enumerate(dirs):
        app.append(descriptor(frames(d / 'short.mp4')))
        mot.append(motion_descriptor(gray_frames(d / 'short.mp4')))
        print(f'  {k + 1}/{n} {d.name}', flush=True)
    Da = np.array([[dist(app[i], app[j]) for j in range(n)] for i in range(n)])
    X = np.array(mot)
    mu, sd = X[pool].mean(0), X[pool].std(0) + 1e-9
    Z = (X - mu) / sd
    Dm = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    hab = evaluate(Da, pate, pool, names, other=mec)
    mcn = evaluate(Dm, mec, pool, names, other=pate)
    # voisinage (§ 8.3) : paires d'habillages dont la distance moyenne est sous la distance intra-habillage moyenne
    keys = sorted({pate[i] for i in pool})
    idx = {k: [i for i in pool if pate[i] == k] for k in keys}
    pairs = []
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            ka, kb = keys[a], keys[b]
            dab = float(np.mean([Da[i, j] for i in idx[ka] for j in idx[kb]]))
            pairs.append((dab, ka, kb))
    pairs.sort()
    thr = hab['meanIntra']
    voisinage = {'seuil (distance intra-habillage moyenne)': thr,
                 'doublonsProbables': [{'a': a, 'b': b, 'distance': round(x, 4)} for x, a, b in pairs if thr and x < thr],
                 'plusProches': [{'a': a, 'b': b, 'distance': round(x, 4)} for x, a, b in pairs[:8]]}
    # M3 (matrice.md § 2) : même sujet, mécaniques et habillages voisins
    m3 = [n_ for n_ in ('atlas-grave__histoire__premier-tour-du-monde-1519-1522', 'lyrics-chemin__histoire__le-premier-tour-du-monde') if n_ in names]
    m3r = None
    if len(m3) == 2:
        i, j = names.index(m3[0]), names.index(m3[1])
        m3r = {'shorts': m3, 'distanceHabillage': round(float(Da[i, j]), 4), 'distanceMecanique': round(float(Dm[i, j]), 4),
               'rangHabillage': sorted([x for x in pool if x != i], key=lambda x: Da[i, x]).index(j) + 1,
               'rangMecanique': sorted([x for x in pool if x != i], key=lambda x: Dm[i, x]).index(j) + 1}
    exclus = [{'short': names[i], 'recette': bq[i]['recette'], 'statut': 'abandonnee',
               'voisinHabillage': names[_nn(Da, i, pool)], 'voisinMecanique': names[_nn(Dm, i, pool)]} for i in excl]
    res = {'date': '2026-11-20', 'generePar': 'out/tools/recognition.py --briques',
           'regle': 'proposition.md § 8 : une recette est reconnaissable quand son habillage et sa mécanique le sont, mesurés séparément',
           'shorts': n, 'mesures': len(pool), 'exclus': exclus,
           'habillage': {'methode': 'Lab 8x8x8 Bhattacharyya + edge-histogram chi2, 8 frames/short (descripteur de recognition.json, inchangé) ; clé = pâte', **hab},
           'mecanique': {'methode': 'descripteur temporel sur toutes les images (30 i/s, gris 108x192), composantes centrées-réduites, distance euclidienne ; clé = mécanique',
                         'composantes': MOTION_FEATURES, **mcn},
           'voisinage': voisinage, 'M3': m3r,
           'briques': {names[i]: {'pate': pate[i], 'mecanique': mec[i], 'recette': bq[i]['recette'], 'statut': bq[i]['statut'], 'source': bq[i]['source']} for i in range(n)},
           'vecteursMecanique': {names[i]: [round(float(x), 4) for x in X[i]] for i in range(n)}}
    (ROOT / 'out/report/recognition-briques.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for nm, r in (('habillage', hab), ('mécanique', mcn)):
        print(f"{nm} : top-1 {r['top1']} (sans pair : {len(r['sansPair'])}) ; croisé {r['croise']['reussis']} (sans le même sujet : {r['croise']['reussisAutreSujet']}) ; intra/inter {r['ratioIntraOverInter']}")
        for e in r['echecs']:
            print('   échec', e['short'], '->', e['voisin'])
        for c in r['croise']['lignes']:
            print('   croisé', 'OK ' if c['reconnu'] else 'NON', c['short'], '->', c['voisin'], f"(1er pair au rang {c['rangDuPremierPair']}/{c['candidats']})")
    print('doublons probables :', voisinage['doublonsProbables'])
    print('M3 :', m3r)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--briques':
        return main_briques()
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
    lone = {i for i in range(n) if ident.count(ident[i]) == 1}   # seul de son identité : aucun pair possible, pas un échec
    for i in range(n):
        order = [j for j in np.argsort(D[i]) if j != i]
        nn = order[0]
        ok = ident[nn] == ident[i]
        if i not in lone:
            hits += ok
        rows.append({'short': dirs[i].name, 'nearest': dirs[nn].name, 'sameIdentity': bool(ok), 'distance': round(D[i, nn], 4),
                     **({'sansPair': True} if i in lone else {})})
        for j in range(n):
            if j != i:
                (intra if ident[j] == ident[i] else inter).append(D[i, j])
    res = {'method': 'Lab 8x8x8 Bhattacharyya + edge-histogram chi2, 8 frames/short, nearest neighbour',
           'shorts': n, 'sansPair': len(lone), 'top1Accuracy': round(hits / (n - len(lone)), 3), 'meanIntra': round(float(np.mean(intra)), 4),
           'meanInter': round(float(np.mean(inter)), 4), 'ratioIntraOverInter': round(float(np.mean(intra) / np.mean(inter)), 3),
           'rows': rows}
    old = ROOT / 'out/report/recognition.json'
    if old.exists():  # conserve les résultats des juges aveugles (ajoutés à part : blindJudge, blindJudge14, …)
        prev = json.loads(old.read_text())
        for k, v in prev.items():
            if k.startswith('blindJudge'):
                res[k] = v
    (ROOT / 'out/report/recognition.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(f"top-1 = {hits}/{n - len(lone)} ({hits / (n - len(lone)):.0%}, {len(lone)} sans pair) ; intra moyen {res['meanIntra']} vs inter {res['meanInter']} (ratio {res['ratioIntraOverInter']})")
    for r in rows:
        if not r['sameIdentity'] and not r.get('sansPair'):
            print('  ÉCHEC', r['short'], '->', r['nearest'])


if __name__ == '__main__':
    main()
