#!/usr/bin/env python3
"""
aggregate.py — agrégation Phase 4 (orchestrateur).

USAGE
  .venv/bin/python out/tools/aggregate.py

1. Fusionne out/library-cards/_drafts/<identité>__<lib>.json -> out/library-cards/<lib>.json
   (bestFor/avoidFor/gotchas/pairsWellWith dédupliqués, coûts mesurés listés par source, snippetPaths multiples).
2. Lit out/shorts/*/short.json -> out/report/campaign.json (index machine-lisible : shorts, durées, temps de rendu,
   libs, familles) + matrice identité × famille × librairie (out/report/matrix.json).
3. Imprime un résumé texte (couverture familles / libs A / libs B).
"""
import json, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out'
LIBS_A = ['three.js', 'Matter.js', 'p5.js', 'GSAP', 'D3.js', 'Manim', 'A-Frame', 'Taichi']
LIBS_B = ['PixiJS', 'Babylon.js', 'Zdog', 'Paper.js', 'anime.js', 'flubber', 'Rough.js', 'twgl.js', 'pycairo', 'Matplotlib', 'OpenCV']
FAMILIES = ['abstrait', 'enfants', 'explicatif', 'histoire', 'geographie', 'evenements', 'engagement']
CANON = {re.sub(r'[^a-z0-9]', '', n.lower()): n for n in LIBS_A + LIBS_B}
CANON.update({'three': 'three.js', 'matter': 'Matter.js', 'matterjs': 'Matter.js', 'p5': 'p5.js', 'd3': 'D3.js', 'aframe': 'A-Frame',
              'pixi': 'PixiJS', 'pixijs': 'PixiJS', 'babylon': 'Babylon.js', 'paper': 'Paper.js', 'paperjs': 'Paper.js', 'anime': 'anime.js',
              'animejs': 'anime.js', 'rough': 'Rough.js', 'roughjs': 'Rough.js', 'twgl': 'twgl.js', 'twgljs': 'twgl.js', 'opencv': 'OpenCV',
              'cv2': 'OpenCV', 'opencvpython': 'OpenCV', 'matplotlib': 'Matplotlib', 'gsap': 'GSAP', 'manim': 'Manim', 'taichi': 'Taichi',
              'zdog': 'Zdog', 'flubber': 'flubber', 'pycairo': 'pycairo', 'cairo': 'pycairo'})


def canon(name):
    base = name.lower().split('(')[0]
    base = re.sub(r'\bv?\d+(\.\d+)*\b', ' ', base)          # retire les versions (« D3.js 7.9 », « anime.js 4.5 v4 »)
    k = re.sub(r'[^a-z0-9]', '', base.replace('.js', 'js'))
    return CANON.get(k, name.strip())


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def dedup(seq):
    seen, out = set(), []
    for x in seq:
        k = x.strip().lower()
        if k and k not in seen:
            seen.add(k); out.append(x.strip())
    return out


def merge_cards():
    drafts = sorted((OUT / 'library-cards' / '_drafts').glob('*.json'))
    by = defaultdict(list)
    for p in drafts:
        try:
            j = json.load(open(p))
        except Exception as e:
            print('carte invalide', p, e); continue
        ident = p.stem.split('__')[0]
        by[canon(j.get('name') or p.stem.split('__')[-1])].append((ident, j))
    for old in (OUT / 'library-cards').glob('*.json'):
        old.unlink()  # régénéré à chaque exécution
    written = []
    for lib, items in sorted(by.items()):
        card = {'name': lib, 'role': items[0][1].get('role', ''), 'bestFor': [], 'avoidFor': [], 'renderCostPer100Frames': [],
                'gotchas': [], 'snippetPath': [], 'pairsWellWith': [], 'usedBy': []}
        for ident, j in items:
            card['usedBy'].append(ident)
            for k in ('bestFor', 'avoidFor', 'gotchas', 'pairsWellWith'):
                v = j.get(k, [])
                card[k] += v if isinstance(v, list) else [v]
            c = j.get('renderCostPer100Frames')
            if c:
                card['renderCostPer100Frames'].append(f'{c} [{ident}]')
            sp = j.get('snippetPath')
            if sp:
                card['snippetPath'] += sp if isinstance(sp, list) else [sp]
        for k in ('bestFor', 'avoidFor', 'gotchas', 'pairsWellWith', 'snippetPath', 'usedBy'):
            card[k] = dedup(card[k])
        roles = dedup([j.get('role', '') for _, j in items])
        card['role'] = ' | '.join(roles)
        f = OUT / 'library-cards' / f'{slugify(lib)}.json'
        json.dump(card, open(f, 'w'), ensure_ascii=False, indent=1)
        written.append(f.name)
    return written


def campaign():
    shorts = []
    for d in sorted((OUT / 'shorts').iterdir()):
        if not d.is_dir() or not (d / 'short.json').exists():
            continue
        j = json.load(open(d / 'short.json'))
        n = json.load(open(d / 'narration.json')) if (d / 'narration.json').exists() else {}
        shorts.append({'dir': f'shorts/{d.name}', 'identity': j.get('identity'), 'family': j.get('family'), 'title': j.get('title'),
                       'duration': j.get('duration'), 'renderTimeSec': j.get('renderTimeSec'),
                       'libraries': [canon(x) for x in j.get('libraries', [])], 'loopable': j.get('loopable'),
                       'mechanic': (j.get('engagement') or {}).get('mechanic'), 'narrationLines': len(n.get('lines', [])),
                       'video': f'shorts/{d.name}/short.mp4'})
    matrix = defaultdict(lambda: defaultdict(list))
    for s in shorts:
        matrix[s['identity']][s['family']] = sorted(set(matrix[s['identity']][s['family']] + s['libraries']))
    json.dump({'shorts': shorts}, open(OUT / 'report' / 'campaign.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(matrix, open(OUT / 'report' / 'matrix.json', 'w'), ensure_ascii=False, indent=1)
    return shorts, matrix


def main():
    cards = merge_cards()
    shorts, matrix = campaign()
    fam = defaultdict(set); libs = defaultdict(set)
    for s in shorts:
        fam[s['family']].add(s['identity'])
        for l in s['libraries']:
            libs[l].add(s['identity'])
    print(f'{len(shorts)} shorts, {len(matrix)} identités, {len(cards)} cartes librairie')
    for f in FAMILIES:
        print(f'  famille {f:11s}: {len(fam[f])} identités {sorted(fam[f])}')
    for l in LIBS_A:
        print(f'  lib A {l:10s}: {sorted(libs[l]) or "MANQUANTE"}')
    print('  libs B utilisées:', sorted(l for l in LIBS_B if libs[l]))
    tot = sum((s['renderTimeSec'] or 0) for s in shorts)
    print(f'  temps de rendu cumulé (déclaré dans short.json): {tot/60:.1f} min')


if __name__ == '__main__':
    main()
