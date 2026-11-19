#!/usr/bin/env python3
"""
build.py — régénère la page vitrine « Studio Visual Identity » (artifact claude.ai) depuis le dépôt.

USAGE (depuis la racine du dépôt)
  .venv/bin/python out/showcase/build.py                       # données + page + aperçus manquants ou périmés
  .venv/bin/python out/showcase/build.py --force-videos        # ré-encode tous les aperçus (ex. après remix voix off)
  .venv/bin/python out/showcase/build.py --videos-for <slug>   # ré-encode seulement les aperçus d'une identité (répétable),
                                                               #   ex. après l'ajout de la voix off du lot 2
  .venv/bin/python out/showcase/build.py --no-media            # data.json + index.html seulement
  python3 out/showcase/build.py --also-from ~/git/StudioVisualIdentity
                                    # ajoute les identités d'un autre checkout absentes d'ici (ex. survol-pixel de main,
                                    #   vue depuis le worktree identite-lyrics) : leur ordre, leurs shorts et leurs vidéos
                                    #   sont lus là-bas ; les identités propres à ce checkout passent après

ENTRÉES : out/identities/index.json (ordre = `rank`, statut `selected` / `rehabilitated` / `added`, `variantOf` / `variants` :
  une identité racine présentée avec ses dérivations — Papier découpé et ses 3 dérivations), tokens.json et identity.md
  de chaque identité, short.json + narration.json de chaque short, out/report/qa.json et out/report/recognition.json (chiffres
  de l'en-tête et de la section reconnaissance, injectés à la place de __META__).
SORTIE : out/showcase/build/   (non versionné, voir .gitignore)
  index.html          page autonome (gabarit page.tpl.html + __DATA__ et __META__ remplacés)
  data.json           identités dans l'ordre du classement, shorts, coûts mesurés, 1re ligne de voix off, état de la voix
  v/<short>.mp4       aperçus 540×960 (crf 27, ≤ 1,6 Mb/s, AAC 112 kb/s)
  p/<short>.jpg       posters des vidéos (image à 2,2 s), p/directions.jpg (planche des 14 directions)

VOIX : short.json.sound.voice faux -> « voix prévue : <nom>, non enregistrée », ou « voix non enregistrée » quand la voix
  n'est pas encore décidée (sound.voicePlanned « à décider par le propriétaire … » ; aucun short depuis la voix de survol-pixel,
  2026-11-18) ; narration.json.voiceUsed (dict, ex. Gemini Sulafat des identités papier, du lot 2 et de survol-pixel) ou
  narration.json.voice (texte) sinon.

PUBLIER : outil Artifact, file_path = out/showcase/build/index.html, root = out/showcase/build,
  files = tous les chemins v/*.mp4 et p/*.jpg (une publication accepte ≤ 64 Mo, ≤ 15 Mo par fichier).
  Artifact existant : https://claude.ai/artifact/VJEgxZpSjAn3cGGb51c1nK (repasser son url pour le mettre à jour).

COMPOSER (section « Composer ses identités ») : les données (habillages, mécaniques, formats, cases de la matrice, essais
  C1…C8) sont lues dans la maquette out/report/notes/composition/vitrine-composer.html (objet `const D = {…}`), et
  injectées à la place de __COMPOSER__ avec des noms lisibles (HAB_NOM, MEC_NOM ci-dessous) et le poster de chaque
  habillage (p/<short>.jpg, déjà produit pour les bandes). Les chiffres d'inventaire (23 identités, 7/12/4) et l'effort
  sont des textes fixes de page.tpl.html, repris de inventaire.md et migration.md.

Les textes fixes de la page (limites, directions, colophon) sont dans page.tpl.html : les mettre à jour à la main quand le
rapport (out/report/) change. Les chiffres (identités, shorts, QA, reconnaissance mesurée, voix) sont calculés ici.
"""
import argparse, glob, json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = HERE / 'build'


def load_index(also=None):
    """Ordre et statut depuis out/identities/index.json (classement de comparison.md §5).

    Avec `also` (racine d'un autre checkout, ex. main) : l'ordre de cet index-là d'abord, chaque entrée lue dans le
    checkout qui la possède (ici de préférence), puis les identités propres à ce checkout ; rangs renumérotés 1..N.
    Rend des couples (entrée d'index, racine où lire tokens, shorts et vidéos)."""
    here = sorted(json.load(open(ROOT / 'out/identities/index.json'))['identities'], key=lambda i: i['rank'])
    if not also:
        return [(e, ROOT) for e in here]
    other = sorted(json.load(open(also / 'out/identities/index.json'))['identities'], key=lambda i: i['rank'])
    mine = {e['id']: e for e in here}
    out = [(mine[e['id']], ROOT) if e['id'] in mine else (e, also) for e in other]
    seen = {e['id'] for e in other}
    out += [(e, ROOT) for e in here if e['id'] not in seen]
    return [(dict(e, rank=n), r) for n, (e, r) in enumerate(out, 1)]


def voice_of(nr, sj):
    """(texte affiché, voisé ?) — robuste aux shorts sans voix et aux narration.json papier (voiceUsed dict)."""
    snd = sj.get('sound') or {}
    if snd.get('type') == 'none' or snd.get('silentTrack'):
        # vidéo de paroles rendue muette : la chanson (hors dépôt) est ajoutée dans l'appli à la publication
        return "muet ici : la chanson est ajoutée dans l'appli à la publication (hors dépôt)", False
    if not snd.get('voice'):
        planned = str(snd.get('voicePlanned') or nr.get('voice') or 'Arnold')
        # voix pas encore décidée (ex. « à décider par le propriétaire (…) ») -> « voix non enregistrée »
        if re.search(r'décid|decid|attente|pending', planned, re.I):
            return 'voix non enregistrée', False
        name = re.sub(r'\s*\(.*\)\s*$', '', planned).strip() or 'Arnold'
        return f'voix prévue : {name}, non enregistrée', False
    vu = nr.get('voiceUsed')
    if isinstance(vu, dict):
        nm = (vu.get('name') or '').split(' - ')[0]   # « Gipsy Paladini - Narration, conversation » -> « Gipsy Paladini »
        name = ' '.join(x for x in (vu.get('provider'), nm) if x)
        return name or 'voix', True
    if isinstance(vu, str) and vu:
        return vu, True
    return str(nr.get('voice') or snd.get('voiceName') or 'voix'), True


def build_data(also=None):
    ids = []
    hab_of = composer_short_habillage()
    for e, root in load_index(also):
        s = e['id']
        t = json.load(open(root / f'out/identities/{s}/tokens.json'))
        ty = t.get('typography', {})
        shorts = []
        for d in sorted(glob.glob(str(root / 'out' / 'shorts' / f'{s}__*'))):
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
                           'voice': voice, 'voiced': voiced, 'line': lines[0]['text'] if lines else '',
                           'hab': hab_of.get(n), 'src': str(Path(d) / 'short.mp4')})
        c = t['color']
        libs = [l.split(' ')[0] if l.split(' ')[0] in ('PixiJS', 'GSAP') else l for l in (t.get('libraries') or [])]
        ids.append({'id': s, 'name': t['name'], 'rank': e['rank'], 'status': e['status'],
                    'reh': e['status'] == 'rehabilitated', 'added': e['status'] == 'added', 'promise': e['promiseFr'].replace('**', ''),
                    'bg': c.get('bg'), 'surface': c.get('surface'), 'text': c.get('text'),
                    'accent': (c.get('accent') or [])[:4], 'display': (ty.get('display') or {}).get('family'),
                    'title': (ty.get('title') or {}).get('family'),
                    'body': (ty.get('body') or {}).get('family'), 'libs': libs, 'shorts': shorts,
                    # une identité racine et ses dérivations (index.json : variantOf / variants / variantAxis)
                    'variantOf': e.get('variantOf'), 'variants': e.get('variants') or [],
                    'axis': (e.get('variantAxis') or {}).get('axisFr'), 'from': None if root == ROOT else 'main'})
    for i in ids:   # l'habillage n'est affiché que pour une identité qui en a plusieurs (lyrics-chemin)
        if len({s['hab'] for s in i['shorts']}) < 2:
            for s in i['shorts']:
                s['hab'] = None
    return ids


def build_meta(ids, also=None):
    roots = [ROOT] + ([also] if also else [])
    # QA : union par short des qa.json des deux checkouts (ici d'abord), restreinte aux shorts affichés
    shorts = [s for i in ids for s in i['shorts']]
    shown = {s['dir'] for s in shorts}
    qa_by = {}
    for r in roots:
        for row in json.load(open(r / 'out/report/qa.json')):
            qa_by.setdefault(row['short'], row)
    qa = [row for k, row in qa_by.items() if k in shown]
    # reconnaissance : le recognition.json qui mesure le plus de shorts (il n'est pas fusionnable : moyennes globales)
    rec = max((json.load(open(r / 'out/report/recognition.json')) for r in roots), key=lambda x: len(x.get('rows', [])))
    voices = {}
    for s in shorts:
        k = s['voice'] if s['voiced'] else 'non enregistrée'
        voices[k] = voices.get(k, 0) + 1
    fails = [r for r in rec.get('rows', []) if not r.get('sameIdentity')]
    derivations = sum(1 for i in ids if i.get('variantOf'))
    return {
        # identités = racines seules ; déclinaisons = toutes les entrées de l'index (racines + dérivations)
        'identities': len(ids) - derivations, 'derivations': derivations, 'declinations': len(ids), 'shorts': len(shorts),
        'qaOk': sum(1 for r in qa if r.get('ok')), 'qaTotal': len(qa),
        'recogHits': sum(1 for r in rec.get('rows', []) if r.get('sameIdentity')), 'recogTotal': len(rec.get('rows', [])),
        'recogIntra': rec.get('meanIntra'), 'recogInter': rec.get('meanInter'), 'recogRatio': rec.get('ratioIntraOverInter'),
        'recogFails': [{'short': r['short'], 'nearest': r['nearest'], 'distance': r['distance']} for r in fails],
        'blindJudge14': (rec.get('blindJudge14') or {}).get('pureGroups'),
        'voiced': sum(1 for s in shorts if s['voiced']), 'voices': voices,
        'qaMissing': sorted(shown - set(qa_by)), 'recogMissing': sorted(shown - {r['short'] for r in rec.get('rows', [])}),
    }


# ---------- section « Composer ses identités » ----------
MAQUETTE = ROOT / 'out/report/notes/composition/vitrine-composer.html'
# noms lisibles par un non-technicien (les ids viennent de inventaire.md)
HAB_NOM = {
    'grille-suisse': 'Grille suisse', 'gazette-sepia': 'Gazette sépia', 'arcade-marine': 'Arcade marine',
    'brut-jaune': 'Brut jaune', 'meteo-clair': 'Météo claire', 'bauhaus-primaires': 'Bauhaus primaires',
    'craie-verte': 'Craie verte', 'riso-3-encres': 'Riso 3 encres', 'orange-graphite': 'Orange graphite',
    'diorama-pastel': 'Diorama pastel', 'relief-vert': 'Relief vert', 'gravure-parchemin': 'Gravure parchemin',
    'aquarelle': 'Aquarelle', 'neon-labo': 'Néon labo', 'cosmos-noir': 'Cosmos noir', 'chrome-irise': 'Chrome irisé',
    'papier-decoupe': 'Papier, tapis vert', 'atelier-papier': 'Papier, bleu nuit', 'carnet-archives': 'Carnet kraft',
    'cabinet-curiosites': 'Cabinet bleu et or', 'punchy': 'Punchy (3 camaïeux)', 'plan-bleu': 'Plan bleu (blueprint)',
    'editeur': 'Éditeur de code', 'ardoise': 'Ardoise', 'portulan': 'Portulan', 'pixel-jour': 'Pixel jour',
}
MEC_NOM = {
    'trace-chemin': 'Chemin qui se trace', 'pop-papier-12ips': 'Papier qui saute (12 images/s)',
    'chiffre-volet-compteur': 'Chiffres qui roulent, volets', 'tourniquet-tampon': 'Journal qui tourne, tampon',
    'simulation-deterministe': 'Simulation (billes, territoires)', 'punch-cut-slam': 'Coupes franches, mots qui claquent',
    'carte-champs-front': 'Carte météo et front', 'puzzle-grille-morph': 'Formes qui pivotent en grille',
    'ecriture-trace-chiffon': 'Écriture à la craie, chiffon', 'impression-on-twos': 'Impression riso saccadée',
    'traceur-escalier-plaque': 'Traceur sur plaque', 'maquette-rebond': 'Maquette qui rebondit',
    'survol-terrain': 'Survol de relief', 'carte-trace-panoramique': 'Carte qui se trace, panoramique',
    'lavis-multiplan': "Lavis qui s'ouvre, plans superposés", 'orbite-phenomene-neon': "Orbite autour d'un phénomène",
    'travelling-cine-3d': 'Travelling de cinéma 3D', 'plan-sequence-matiere': 'Plan-séquence de matière',
    'colonne-mot-a-mot': 'Colonne mot à mot',
}
FMT_NOM = {'narre-court': 'Narré court', 'narre-long': 'Narré long', 'paroles-muet': 'Paroles, muet', 'boucle': 'Boucle'}


def maquette():
    m = re.search(r'const D = (\{.*?\});\n', MAQUETTE.read_text(), re.S)
    assert m, f'objet D introuvable dans {MAQUETTE}'
    return json.loads(m.group(1))


def composer_short_habillage():
    """dossier de short -> nom lisible de son habillage (recettes de la maquette)."""
    return {s['dir']: HAB_NOM.get(r['habillage'], r['habillage']) for r in maquette()['recettes'] for s in r['shorts']}


def build_composer(ids):
    D = maquette()
    by_id = {i['id']: i for i in ids}
    first = {}   # recette -> premier short (poster)
    for r in D['recettes']:
        dirs = [s['dir'] for s in r['shorts']] or [s['dir'] for s in (by_id.get(r['id']) or {}).get('shorts', [])]
        first[r['id']] = dirs[0] if dirs else None
    anchor = lambda rid: rid if rid in by_id else 'lyrics-chemin' if rid.startswith('chemin-') else rid
    tested = {c['h']: c['recette'] for c in D['cases'] if c['etat'] == 'teste'}
    habs = [{'id': h['id'], 'nom': HAB_NOM.get(h['id'], h['id']), 'de': h['de'],
             'poster': first.get(tested.get(h['id'])), 'ancre': anchor(tested.get(h['id'], h['de']))}
            for h in D['habillages']]
    mecs = [{'id': m['id'], 'nom': MEC_NOM.get(m['id'], m['id']), 'de': m['de']} for m in D['mecaniques']]
    cases = [{**c, 'poster': first.get(c.get('recette')), 'ancre': anchor(c['recette']) if c.get('recette') else None,
              'fNom': FMT_NOM.get(c['f'], c['f'])} for c in D['cases']]
    # un habillage dont aucun short n'est dans la page (ex. pixel-jour sans --also-from sur identite-lyrics) garde un
    # poster nul : il n'apparaît que dans la matrice complète, sous forme de point
    return {'habillages': habs, 'mecaniques': mecs, 'formats': [{**f, 'nom': FMT_NOM.get(f['id'], f['id'])} for f in D['formats']],
            'cases': cases}


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
            src = Path(s['src'])
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
    ap.add_argument('--also-from', metavar='RACINE', type=lambda x: Path(x).expanduser().resolve(),
                    help="racine d'un autre checkout dont on ajoute les identités absentes d'ici (ex. ~/git/StudioVisualIdentity)")
    a = ap.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    ids = build_data(a.also_from)
    unknown = set(a.videos_for) - {i['id'] for i in ids}
    if unknown:
        ap.error(f"identité inconnue : {', '.join(sorted(unknown))}")
    # 'src' (chemin local du short.mp4) ne sert qu'à l'encodage : il ne part pas dans la page publiée
    data = json.dumps([{**i, 'shorts': [{k: v for k, v in s.items() if k != 'src'} for s in i['shorts']]} for i in ids],
                      ensure_ascii=False)
    meta = json.dumps(build_meta(ids, a.also_from), ensure_ascii=False)
    comp = json.dumps(build_composer(ids), ensure_ascii=False)
    (BUILD / 'data.json').write_text(data)
    tpl = (HERE / 'page.tpl.html').read_text()
    assert tpl.count('__DATA__') == 1 and tpl.count('__META__') == 1 and tpl.count('__COMPOSER__') == 1
    (BUILD / 'index.html').write_text(tpl.replace('__DATA__', data).replace('__META__', meta).replace('__COMPOSER__', comp))
    if not a.no_media:
        build_media(ids, a.force_videos, set(a.videos_for) or None)
    n = sum(len(i['shorts']) for i in ids)
    nd = sum(1 for i in ids if i['variantOf'])
    print(f'{len(ids) - nd} identités, {len(ids)} déclinaisons, {n} shorts -> {BUILD / "index.html"}')


if __name__ == '__main__':
    main()
