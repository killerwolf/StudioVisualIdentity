#!/usr/bin/env python3
"""
build.py — régénère la page vitrine « Studio Visual Identity » (artifact claude.ai) depuis le dépôt.

USAGE (depuis la racine du dépôt)
  .venv/bin/python out/showcase/build.py                 # données + page + aperçus manquants
  .venv/bin/python out/showcase/build.py --force-videos  # ré-encode tous les aperçus (ex. après remix voix off)

SORTIE : out/showcase/build/   (non versionné, voir .gitignore)
  index.html          page autonome (gabarit page.tpl.html + données injectées à la place de __DATA__)
  data.json           identités dans l'ordre du classement, shorts, coûts mesurés, 1re ligne de voix off
  v/<short>.mp4       aperçus 540×960 (crf 27, ≤ 1,6 Mb/s, AAC 112 kb/s) — ~27 Mo pour 31 shorts
  p/<short>.jpg       posters des vidéos (image à 2,2 s), p/directions.jpg (planche des 14 directions)

PUBLIER : outil Artifact, file_path = out/showcase/build/index.html, root = out/showcase/build,
  files = tous les chemins v/*.mp4 et p/*.jpg (une publication accepte ≤ 64 Mo, ≤ 15 Mo par fichier).
  Artifact existant : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (repasser son url pour le mettre à jour).

Les textes fixes de la page (chiffres de l'en-tête, tests de reconnaissance, limites) sont dans page.tpl.html :
les mettre à jour à la main quand le rapport (out/report/) change. Ordre et statut « réhabilitée » : ORDER / REHAB.
"""
import argparse, glob, json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = HERE / 'build'

# classement de durabilité (out/report/comparison.md §5)
ORDER = ['swiss-data', 'gazette-1900', 'pixel-arcade', 'brut-meme', 'bauhaus-kinetic', 'tableau-craie', 'riso-zine',
         'pastel-diorama', 'topo-relief', 'atlas-grave', 'aquarelle-conte', 'neon-lab', 'cosmos-doc', 'liquid-chrome']
REHAB = {'brut-meme', 'riso-zine', 'topo-relief', 'cosmos-doc'}   # écartées en Phase 1 puis produites à la demande


def build_data():
    ids = []
    for rank, s in enumerate(ORDER, 1):
        t = json.load(open(ROOT / f'out/identities/{s}/tokens.json'))
        md = (ROOT / f'out/identities/{s}/identity.md').read_text()
        promise = md.split('## Promesse', 1)[1].split('\n', 1)[1].strip().split('\n')[0].strip('« »"')
        ty = t.get('typography', {})
        shorts = []
        for d in sorted(glob.glob(str(ROOT / 'out' / 'shorts' / f'{s}__*'))):
            if not os.path.isdir(d):
                continue
            n = os.path.basename(d)
            j = json.load(open(os.path.join(d, 'short.json')))
            nr = json.load(open(os.path.join(d, 'narration.json')))
            frames = round(j['duration'] * 30)
            shorts.append({'dir': n, 'title': j['title'], 'family': j['family'], 'duration': j['duration'],
                           'render': j.get('renderTimeSec'), 'cost': round(j['renderTimeSec'] / frames * 100, 1),
                           'libs': j['libraries'], 'loop': bool(j.get('loopable')),
                           'voice': (nr.get('voiceUsed') or {}).get('name') or nr.get('voice'), 'voiced': bool((j.get('sound') or {}).get('voice')),
                           'line': nr['lines'][0]['text'] if nr['lines'] else ''})
        c = t['color']
        libs = [l.split(' ')[0] if l.split(' ')[0] in ('PixiJS', 'GSAP') else l for l in (t.get('libraries') or [])]
        ids.append({'id': s, 'name': t['name'], 'rank': rank, 'reh': s in REHAB, 'promise': promise,
                    'bg': c.get('bg'), 'surface': c.get('surface'), 'text': c.get('text'),
                    'accent': (c.get('accent') or [])[:4], 'display': ty.get('display', {}).get('family'),
                    'body': ty.get('body', {}).get('family'), 'libs': libs, 'shorts': shorts})
    return ids


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def build_media(ids, force):
    (BUILD / 'v').mkdir(parents=True, exist_ok=True)
    (BUILD / 'p').mkdir(parents=True, exist_ok=True)
    for i in ids:
        for s in i['shorts']:
            src = ROOT / f"out/shorts/{s['dir']}/short.mp4"
            v, p = BUILD / f"v/{s['dir']}.mp4", BUILD / f"p/{s['dir']}.jpg"
            if force or not v.exists() or v.stat().st_mtime < src.stat().st_mtime:
                ff('-i', str(src), '-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27',
                   '-maxrate', '1.6M', '-bufsize', '3M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '112k',
                   '-movflags', '+faststart', str(v))
                print('aperçu', v.name)
            if force or not p.exists():
                ff('-ss', '2.2', '-i', str(src), '-frames:v', '1', '-vf', 'scale=540:-1', '-q:v', '4', str(p))
    sheet = BUILD / 'p/directions.jpg'
    if force or not sheet.exists():
        ff('-i', str(ROOT / 'out/report/directions-contact-sheet.jpg'), '-vf', 'scale=1600:-1', '-q:v', '4', str(sheet))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force-videos', action='store_true')
    ap.add_argument('--no-media', action='store_true', help='ne régénère que data.json et index.html')
    a = ap.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    ids = build_data()
    data = json.dumps(ids, ensure_ascii=False)
    (BUILD / 'data.json').write_text(data)
    tpl = (HERE / 'page.tpl.html').read_text()
    assert tpl.count('__DATA__') == 1
    (BUILD / 'index.html').write_text(tpl.replace('__DATA__', data))
    if not a.no_media:
        build_media(ids, a.force_videos)
    n = sum(len(i['shorts']) for i in ids)
    print(f'{len(ids)} identités, {n} shorts -> {BUILD / "index.html"}')


if __name__ == '__main__':
    main()
