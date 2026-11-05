#!/usr/bin/env python3
"""
build.py — régénère la page vitrine « Studio Visual Identity » (artifact claude.ai) depuis le dépôt.

USAGE (depuis la racine du dépôt)
  .venv/bin/python out/showcase/build.py                       # données + page + aperçus manquants ou périmés
  .venv/bin/python out/showcase/build.py --force-videos        # ré-encode tous les aperçus (ex. après remix voix off)
  .venv/bin/python out/showcase/build.py --videos-for <slug>   # ré-encode seulement les aperçus d'une identité (répétable),
                                                               #   ex. après l'ajout de la voix off du lot 2
  .venv/bin/python out/showcase/build.py --no-media            # data.json + index.html seulement

ENTRÉES : out/identities/index.json (ordre = `rank`, statut `selected` / `rehabilitated` / `added`), tokens.json et identity.md
  de chaque identité, short.json + narration.json de chaque short, out/report/qa.json et out/report/recognition.json (chiffres
  de l'en-tête et de la section reconnaissance, injectés à la place de __META__).
SORTIE : out/showcase/build/   (non versionné, voir .gitignore)
  index.html          page autonome (gabarit page.tpl.html + __DATA__ et __META__ remplacés)
  data.json           identités dans l'ordre du classement, shorts, coûts mesurés, 1re ligne de voix off, état de la voix
  v/<short>.mp4       aperçus 540×960 (crf 27, ≤ 1,6 Mb/s, AAC 112 kb/s)
  p/<short>.jpg       posters des vidéos (image à 2,2 s), p/directions.jpg (planche des 14 directions)

VOIX : short.json.sound.voice faux -> « voix prévue : <nom>, non enregistrée » (cas d'un short sans voix) ; narration.json.voiceUsed
  (dict, ex. Gemini Sulafat des identités papier et du lot 2) ou narration.json.voice (texte) sinon.

PUBLIER : outil Artifact, file_path = out/showcase/build/index.html, root = out/showcase/build,
  files = tous les chemins v/*.mp4 et p/*.jpg (une publication accepte ≤ 64 Mo, ≤ 15 Mo par fichier).
  Artifact existant : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (repasser son url pour le mettre à jour).

Les textes fixes de la page (limites, directions, colophon) sont dans page.tpl.html : les mettre à jour à la main quand le
rapport (out/report/) change. Les chiffres (identités, shorts, QA, reconnaissance mesurée, voix) sont calculés ici.
"""
import argparse, glob, json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = HERE / 'build'


def load_index():
    """Ordre et statut depuis out/identities/index.json (classement de comparison.md §5)."""
    idx = json.load(open(ROOT / 'out/identities/index.json'))
    return sorted(idx['identities'], key=lambda i: i['rank'])


def voice_of(nr, sj):
    """(texte affiché, voisé ?) — robuste aux shorts sans voix et aux narration.json papier (voiceUsed dict)."""
    snd = sj.get('sound') or {}
    if not snd.get('voice'):
        planned = snd.get('voicePlanned') or nr.get('voice') or 'Arnold'
        name = re.sub(r'\s*\(.*\)\s*$', '', str(planned)).strip() or 'Arnold'
        return f'voix prévue : {name}, non enregistrée', False
    vu = nr.get('voiceUsed')
    if isinstance(vu, dict):
        name = ' '.join(x for x in (vu.get('provider'), vu.get('name')) if x)
        return name or 'voix', True
    if isinstance(vu, str) and vu:
        return vu, True
    return str(nr.get('voice') or snd.get('voiceName') or 'voix'), True


def build_data():
    ids = []
    for e in load_index():
        s = e['id']
        t = json.load(open(ROOT / f'out/identities/{s}/tokens.json'))
        ty = t.get('typography', {})
        shorts = []
        for d in sorted(glob.glob(str(ROOT / 'out' / 'shorts' / f'{s}__*'))):
            if not os.path.isdir(d):
                continue
            n = os.path.basename(d)
            j = json.load(open(os.path.join(d, 'short.json')))
            nr = json.load(open(os.path.join(d, 'narration.json')))
            frames = round(j['duration'] * 30)
            rt = j.get('renderTimeSec')
            voice, voiced = voice_of(nr, j)
            lines = nr.get('lines') or []
            shorts.append({'dir': n, 'title': j['title'], 'family': j['family'], 'duration': j['duration'],
                           'render': rt, 'cost': round(rt / frames * 100, 1) if rt else None,
                           'libs': j.get('libraries') or [], 'loop': bool(j.get('loopable')),
                           'voice': voice, 'voiced': voiced, 'line': lines[0]['text'] if lines else ''})
        c = t['color']
        libs = [l.split(' ')[0] if l.split(' ')[0] in ('PixiJS', 'GSAP') else l for l in (t.get('libraries') or [])]
        ids.append({'id': s, 'name': t['name'], 'rank': e['rank'], 'status': e['status'],
                    'reh': e['status'] == 'rehabilitated', 'added': e['status'] == 'added', 'promise': e['promiseFr'].replace('**', ''),
                    'bg': c.get('bg'), 'surface': c.get('surface'), 'text': c.get('text'),
                    'accent': (c.get('accent') or [])[:4], 'display': (ty.get('display') or {}).get('family'),
                    'title': (ty.get('title') or {}).get('family'),
                    'body': (ty.get('body') or {}).get('family'), 'libs': libs, 'shorts': shorts})
    return ids


def build_meta(ids):
    qa = json.load(open(ROOT / 'out/report/qa.json'))
    rec = json.load(open(ROOT / 'out/report/recognition.json'))
    shorts = [s for i in ids for s in i['shorts']]
    voices = {}
    for s in shorts:
        k = s['voice'] if s['voiced'] else 'non enregistrée'
        voices[k] = voices.get(k, 0) + 1
    fails = [r for r in rec.get('rows', []) if not r.get('sameIdentity')]
    return {
        'identities': len(ids), 'shorts': len(shorts),
        'qaOk': sum(1 for r in qa if r.get('ok')), 'qaTotal': len(qa),
        'recogHits': sum(1 for r in rec.get('rows', []) if r.get('sameIdentity')), 'recogTotal': len(rec.get('rows', [])),
        'recogIntra': rec.get('meanIntra'), 'recogInter': rec.get('meanInter'), 'recogRatio': rec.get('ratioIntraOverInter'),
        'recogFails': [{'short': r['short'], 'nearest': r['nearest'], 'distance': r['distance']} for r in fails],
        'blindJudge14': (rec.get('blindJudge14') or {}).get('pureGroups'),
        'voiced': sum(1 for s in shorts if s['voiced']), 'voices': voices,
    }


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def build_media(ids, force, only=None):
    (BUILD / 'v').mkdir(parents=True, exist_ok=True)
    (BUILD / 'p').mkdir(parents=True, exist_ok=True)
    for i in ids:
        if only and i['id'] not in only:
            continue
        redo = force or bool(only)
        for s in i['shorts']:
            src = ROOT / f"out/shorts/{s['dir']}/short.mp4"
            v, p = BUILD / f"v/{s['dir']}.mp4", BUILD / f"p/{s['dir']}.jpg"
            if redo or not v.exists() or v.stat().st_mtime < src.stat().st_mtime:
                ff('-i', str(src), '-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27',
                   '-maxrate', '1.6M', '-bufsize', '3M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '112k',
                   '-movflags', '+faststart', str(v))
                print('aperçu', v.name)
            if redo or not p.exists() or p.stat().st_mtime < src.stat().st_mtime:
                ff('-ss', '2.2', '-i', str(src), '-frames:v', '1', '-vf', 'scale=540:-1', '-q:v', '4', str(p))
    sheet = BUILD / 'p/directions.jpg'
    if (force and not only) or not sheet.exists():
        ff('-i', str(ROOT / 'out/report/directions-contact-sheet.jpg'), '-vf', 'scale=1600:-1', '-q:v', '4', str(sheet))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force-videos', action='store_true', help='ré-encode tous les aperçus')
    ap.add_argument('--videos-for', action='append', metavar='SLUG', default=[],
                    help="ré-encode seulement les aperçus de cette identité (répétable)")
    ap.add_argument('--no-media', action='store_true', help='ne régénère que data.json et index.html')
    a = ap.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    ids = build_data()
    unknown = set(a.videos_for) - {i['id'] for i in ids}
    if unknown:
        ap.error(f"identité inconnue : {', '.join(sorted(unknown))}")
    data = json.dumps(ids, ensure_ascii=False)
    meta = json.dumps(build_meta(ids), ensure_ascii=False)
    (BUILD / 'data.json').write_text(data)
    tpl = (HERE / 'page.tpl.html').read_text()
    assert tpl.count('__DATA__') == 1 and tpl.count('__META__') == 1
    (BUILD / 'index.html').write_text(tpl.replace('__DATA__', data).replace('__META__', meta))
    if not a.no_media:
        build_media(ids, a.force_videos, set(a.videos_for) or None)
    n = sum(len(i['shorts']) for i in ids)
    print(f'{len(ids)} identités, {n} shorts -> {BUILD / "index.html"}')


if __name__ == '__main__':
    main()
