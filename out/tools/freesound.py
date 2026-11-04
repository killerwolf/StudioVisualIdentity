#!/usr/bin/env python3
"""
freesound.py — chercher et télécharger des effets sonores sur Freesound (https://freesound.org), sans MCP.

PRÉREQUIS
  - une clé API Freesound (gratuite) : https://freesound.org/apiv2/apply  -> variable d'environnement FREESOUND_API_KEY
  - accès réseau à freesound.org et cdn.freesound.org (proxy de l'environnement cloud : « Allowed domains »)

USAGE
  python3 out/tools/freesound.py search "whoosh fast" [--license cc0] [--max-dur 2] [-n 10]
  python3 out/tools/freesound.py get <id> [<id> ...] --dir out/demo/sfx       # télécharge l'aperçu HQ (mp3 ~128 kb/s)

Par défaut on ne garde que les sons CC0 (domaine public, pas d'attribution obligatoire). Chaque téléchargement est
consigné dans <dir>/credits.json (id, nom, auteur, licence, URL) : gardez-le à côté des sons, même pour du CC0.
L'aperçu HQ suffit pour des SFX de vidéo courte ; le fichier original exige OAuth2 et n'est pas géré ici.
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

API = 'https://freesound.org/apiv2'
LICENSES = {'cc0': 'license:"Creative Commons 0"', 'by': 'license:"Attribution"', 'any': ''}
FIELDS = 'id,name,username,license,duration,tags,previews,url,avg_rating,num_downloads'


def key():
    k = os.environ.get('FREESOUND_API_KEY')
    if not k:
        sys.exit('FREESOUND_API_KEY absente : créez une clé sur https://freesound.org/apiv2/apply')
    return k


def call(path, **params):
    params['token'] = key()
    url = f'{API}{path}?{urllib.parse.urlencode(params)}'
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'svi-freesound/1.0'}), timeout=30) as r:
        return json.load(r)


def search(a):
    filt = ' '.join(x for x in [LICENSES[a.license], f'duration:[0 TO {a.max_dur}]' if a.max_dur else ''] if x)
    res = call('/search/text/', query=a.query, filter=filt, fields=FIELDS, page_size=a.n, sort=a.sort)
    for s in res['results']:
        print(f"{s['id']:>8}  {s['duration']:5.2f}s  ★{s.get('avg_rating', 0):.1f}  ↓{s.get('num_downloads', 0):<6} "
              f"{s['name'][:50]:<50}  {s['username']}  [{s['license'].rstrip('/').split('/')[-2]}]")
    print(f"({res['count']} résultats)", file=sys.stderr)


def get(a):
    d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
    cred_p = d / 'credits.json'
    credits = json.load(open(cred_p)) if cred_p.exists() else {}
    for sid in a.ids:
        s = call(f'/sounds/{sid}/', fields=FIELDS)
        name = a.name if (a.name and len(a.ids) == 1) else f"fs{s['id']}"
        out = d / f'{name}.mp3'
        req = urllib.request.Request(s['previews']['preview-hq-mp3'], headers={'User-Agent': 'svi-freesound/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.write_bytes(r.read())
        credits[out.name] = {'id': s['id'], 'name': s['name'], 'author': s['username'], 'license': s['license'], 'url': s['url']}
        print(out)
    json.dump(credits, open(cred_p, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('search'); s.add_argument('query'); s.add_argument('--license', default='cc0', choices=LICENSES)
    s.add_argument('--max-dur', type=float, default=None); s.add_argument('-n', type=int, default=10)
    s.add_argument('--sort', default='score', choices=['score', 'downloads_desc', 'rating_desc', 'duration_asc'])
    g = sub.add_parser('get'); g.add_argument('ids', nargs='+'); g.add_argument('--dir', default='sfx'); g.add_argument('--name')
    a = p.parse_args()
    search(a) if a.cmd == 'search' else get(a)
