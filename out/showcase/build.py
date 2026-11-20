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

COMPOSER (section « Composer ses identités ») : depuis le 20/11/2026 (migration.md étape 6), les données sont lues dans les
  sections briques de out/identities/index.json (schéma 2.0 : habillages[], mecaniques[], formats[], recettes[],
  compatibilite[] calculée par build_index.py depuis les fiches out/habillages, out/mecaniques, out/formats, out/recettes,
  dont propositions.json pour les cases C3, C5…C8) et dans out/report/recognition-briques.json (reconnaissance à deux
  étages, recognition.py --briques), puis injectées à la place de __COMPOSER__ avec les noms lisibles des fiches. La
  maquette vitrine-composer.html n'est plus lue (gardée, marquée « remplacée »). Les chiffres de la section (recettes,
  habillages, pâtes, mécaniques, cases par état, facile / moyen / difficile) sont calculés. Les recettes nées d'une case de
  la matrice (clé « case » : C1, C2, C4) remplissent leur case : short, aperçu v/<short>.mp4, poster p/<short>.jpg (image à
  posterT), verdict et statut (« validee » = recette adoptée, comme C2 « Données qui se tracent » ; « essai » ;
  « abandonnee », comme C4). Leurs 3 shorts comptent dans « shorts livrés » de l'en-tête (53 = 50 des identités + 3 nés de
  la matrice) et dans le contrôle qualité, pas dans les bandes des identités.

Les textes fixes de la page (limites, directions, colophon) sont dans page.tpl.html : les mettre à jour à la main quand le
rapport (out/report/) change. Les chiffres (identités, shorts, QA, reconnaissance mesurée, voix) sont calculés ici.
"""
import argparse, glob, json, os, re, subprocess, sys
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
    comp = {d for d, _, _ in essai_shorts()}          # shorts nés d'une case de la matrice (hors bandes des identités)
    qa = [row for k, row in qa_by.items() if k in shown or k in comp]
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
        'qaMissing': sorted((shown | comp) - set(qa_by)), 'recogMissing': sorted(shown - {r['short'] for r in rec.get('rows', [])}),
        'shortsAll': len(shown | comp), 'shortsComposes': len(comp - shown),
        'briques': index_briques()['counts']['briques'], 'recogBriques': reconnaissance_briques(),
    }


# ---------- section « Composer ses identités » ----------
# Depuis le 20/11/2026 (migration.md étape 6) : lue dans les sections briques de out/identities/index.json (schéma 2.0,
# build_index.py, elles-mêmes lues dans les fiches out/habillages, out/mecaniques, out/formats, out/recettes), et dans
# out/report/recognition-briques.json (reconnaissance à deux étages). La maquette vitrine-composer.html n'est plus lue
# (gardée, marquée « remplacée »). Noms lisibles : champ « nom » des fiches.
sys.path.insert(0, str(ROOT / 'out/tools'))
import briques as B  # noqa: E402

FMT_NOM = {'narre-court': 'Narré court', 'narre-long': 'Narré long', 'paroles-muet': 'Paroles, muet', 'boucle': 'Boucle'}


def index_briques():
    ix = json.load(open(ROOT / 'out/identities/index.json'))
    assert ix.get('schemaVersion', '1') >= '2', "index.json sans briques : lancer python3 out/tools/build_index.py"
    return ix


def composer_short_habillage():
    """dossier de short -> nom lisible de son habillage (fiche de la pâte, via etiquettes.json / short.json)."""
    out = {}
    for d in (ROOT / 'out/shorts').iterdir():
        if d.is_dir():
            b = B.briques_du_short(d.name)
            if b['pate']:
                out[d.name] = B.nom_pate(b['pate'])
    return out


def essais():
    """Recettes nées d'une case de la matrice (clé « case » ou ancienne clé « essai » : C1, C2, C4…), adoptées, à l'essai
    ou abandonnées : leur short est hors identités. r['case'] est rempli depuis l'ancienne clé si besoin."""
    return [{**r, 'case': r.get('case') or r['essai']} for r in B.recettes().values() if r.get('case') or r.get('essai')]


def essai_shorts():
    """(dossier, chemin du short.mp4, instant du poster) des shorts d'essai ; posterT de la recette = une image qui montre l'essai (souvent l'image finale)."""
    return [(Path(d).name, ROOT / d / 'short.mp4', r.get('posterT', 2.2)) for r in essais() for d in r['shorts'] if (ROOT / d / 'short.mp4').exists()]


def reconnaissance_briques():
    """résumé de out/report/recognition-briques.json (None s'il n'a pas été mesuré)."""
    p = ROOT / 'out/report/recognition-briques.json'
    if not p.exists():
        return None
    r = json.load(open(p))
    nom = lambda k: B.nom_pate(k) if k and k in B.habillages() else (B.mecaniques().get(k) or {}).get('nom', k)
    bq = r.get('briques') or {}
    autre = lambda d, cle: nom(bq.get(d, {}).get('mecanique' if cle == 'pate' else 'pate'))   # l'autre brique du short
    def etage(e, cle_nom, cle):
        lignes = [{'short': c['short'], 'cle': cle_nom(c['cle']), 'autre': autre(c['short'], cle), 'voisin': c['voisin'],
                   'cleVoisin': cle_nom(c['cleVoisin']), 'autreVoisin': autre(c['voisin'], cle),
                   'ok': c['reconnu'], 'rang': c['rangDuPremierPair'], 'n': c['candidats']} for c in e['croise']['lignes']]
        groupes = {}
        for l in lignes:
            g = groupes.setdefault(l['cle'], [0, 0]); g[0] += l['ok']; g[1] += 1
        return {'top1': e['top1'], 'acc': e['top1Accuracy'], 'sansPair': len(e['sansPair']), 'ratio': e['ratioIntraOverInter'],
                'croise': e['croise']['reussis'], 'groupes': [{'cle': k, 'ok': v[0], 'n': v[1]} for k, v in groupes.items()],
                'lignes': lignes,
                'echecs': [{'short': x['short'], 'cle': cle_nom(x['cle']), 'voisin': x['voisin'], 'cleVoisin': cle_nom(x['cleVoisin'])} for x in e['echecs']]}
    return {'date': r.get('date'), 'shorts': r['shorts'], 'mesures': r['mesures'], 'exclus': [x['short'] for x in r['exclus']],
            'habillage': etage(r['habillage'], nom, 'pate'), 'mecanique': etage(r['mecanique'], nom, 'mecanique'),
            'doublons': [{'a': nom(x['a']), 'b': nom(x['b'])} for x in r['voisinage']['doublonsProbables']], 'M3': r.get('M3')}


def build_composer(ids):
    ix = index_briques()
    shown = {s['dir'] for i in ids for s in i['shorts']}
    ident_of = {s['dir']: i['id'] for i in ids for s in i['shorts']}
    rank = {i['id']: i['rank'] for i in ids}
    R = {r['id']: r for r in ix['recettes']}
    ess = {}
    for r in essais():
        if not r['shorts'] or not (ROOT / r['shorts'][0] / 'short.mp4').exists():
            continue
        d = Path(r['shorts'][0]).name
        ess[r['case']] = {'essai': r['case'], 'statut': r.get('statut'), 'video': f'v/{d}.mp4', 'nom': r['nom'], 'recette': r['id'],
                          'verdict': r.get('verdict') or {}, 'question': r.get('question'), 'dir': d,
                          'duree': json.load(open(ROOT / r['shorts'][0] / 'short.json')).get('duration')}
    anchor = lambda d, case=None: f'essai-{case}' if case else ident_of.get(d)
    cases = []
    for c in ix['compatibilite']:
        prv = [Path(x).name for x in c.get('preuve') or []]
        cat = [d for d in prv if d in shown]
        poster = (cat or prv or [None])[0]
        fait = ess.get(c.get('case')) if c.get('case') and prv else None
        cases.append({'h': c['pate'], 'm': c['mecanique'], 'f': c['format'], 'fNom': FMT_NOM.get(c['format'], c['format'] or '—'),
                      'etat': c['etat'], 'recette': c.get('recette'), 'statut': c.get('statut'), 'essai': c.get('case'),
                      'note': c.get('raison') if c['etat'] in ('incompatible', 'inconnu') else c.get('question') or c.get('raison'),
                      'alerte': c.get('alerte'), 'cout': c.get('cout'), 'poster': (fait or {}).get('dir') or poster,
                      'ancre': anchor(poster, c.get('case') if (fait or not prv) else None), 'n': len(prv),
                      **({'fait': fait} if fait else {})})
    # habillages (lignes de la matrice) : pâtes en service, dans l'ordre du classement de la recette d'où elles viennent
    top, pates = B.actifs()
    H = {h['id']: h for h in ix['habillages']}
    def de_rank(k):
        de = H[k].get('de') or ''
        return rank.get(de, rank.get('lyrics-chemin', 99) + 0.5 if de.startswith('chemin-') else 99)
    habs = []
    for k in sorted(pates, key=lambda k: (de_rank(k), k)):
        tc = [c for c in cases if c['h'] == k and c['etat'] == 'teste' and not c.get('fait') and c['poster'] in shown]
        habs.append({'id': k, 'nom': H[k].get('nom') or k, 'de': H[k].get('de'), 'niveau': H[k].get('niveau'),
                     'famille': k.split('/')[0] if '/' in k else None,
                     'poster': tc[0]['poster'] if tc else None, 'ancre': tc[0]['ancre'] if tc else None})
    mecs = [{'id': m['id'], 'nom': m.get('nom') or m['id'], 'de': m.get('recettes') or [], 'niveau': m.get('niveau'),
             'separation': m.get('separation')} for m in sorted(ix['mecaniques'], key=lambda m: min([rank.get(r, 99) for r in m.get('recettes') or []] or [99]))]
    # chiffres de la section, calculés
    sep = {}
    for r in ix['recettes']:
        if r.get('separation') and r.get('statut') == 'validee':
            k = {'exécutable': 'facile', 'FACILE': 'facile', 'MOYEN': 'moyen', 'DIFFICILE': 'difficile'}.get(r['separation'], 'moyen')
            sep[k] = sep.get(k, 0) + 1
    cb = ix['counts']['briques']
    fam = B.habillages().get('craie') or {}
    return {'habillages': habs, 'mecaniques': mecs, 'formats': [{**f, 'nom': FMT_NOM.get(f['id'], f.get('nom'))} for f in ix['formats']],
            'cases': cases, 'essais': sorted(ess), 'counts': cb, 'separation': sep, 'recog': reconnaissance_briques(),
            'famille': {'id': 'craie', 'nom': fam.get('nom'), 'variantes': fam.get('variantes') or [], 'differences': fam.get('differences') or {}}}


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
    if not only:   # shorts d'essai de la composition (hors index) : mêmes aperçus et posters
        for d, src, pt in essai_shorts():
            v, p = BUILD / f"v/{d}.mp4", BUILD / f"p/{d}.jpg"
            if force or not v.exists() or v.stat().st_mtime < src.stat().st_mtime:
                ff('-i', str(src), '-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27',
                   '-maxrate', '1.6M', '-bufsize', '3M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '112k',
                   '-movflags', '+faststart', str(v))
                print('aperçu (essai)', v.name)
            if force or not p.exists() or p.stat().st_mtime < src.stat().st_mtime:
                ff('-ss', str(pt), '-i', str(src), '-frames:v', '1', '-vf', 'scale=540:-1', '-q:v', '4', str(p))
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
