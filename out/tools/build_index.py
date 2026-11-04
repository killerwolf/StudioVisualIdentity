#!/usr/bin/env python3
"""
build_index.py — génère out/identities/index.json, l'index machine des identités (point d'entrée des agents).

USAGE (depuis la racine du dépôt) :  python3 out/tools/build_index.py      (aucune dépendance hors stdlib)

Pour chaque identité :
  - mesuré / extrait des fichiers : rang, statut, familles prouvées, libs, coût de rendu par short (s/100 frames),
    durée, voix utilisée, chemins (identity.md, tokens.json, recettes, poster, planche-contact, shorts, module partagé)
  - `coreTokens` : sous-ensemble NORMALISÉ des tokens.json (les tokens.json d'origine varient : ms vs s, tailles en texte,
    slug de police absent…). Unités : secondes, pixels (canvas 1080×1920), slugs @fontsource. Schéma : out/identities/core-tokens.schema.json
  - `curation` : jugement de l'orchestrateur, NON mesuré (public conseillé, signature à préserver, résumé en anglais,
    identités avec lesquelles elle se confond) — à traiter comme une recommandation.
Relancer ce script après toute modification d'une identité ou d'un short.
"""
import glob, hashlib, json, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out'

ORDER = ['swiss-data', 'gazette-1900', 'pixel-arcade', 'brut-meme', 'bauhaus-kinetic', 'tableau-craie', 'riso-zine',
         'pastel-diorama', 'topo-relief', 'atlas-grave', 'aquarelle-conte', 'neon-lab', 'cosmos-doc', 'liquid-chrome']
REHAB = {'brut-meme', 'riso-zine', 'topo-relief', 'cosmos-doc'}
VOICE = {'provider': 'Fish Audio', 'name': 'Arnold', 'reference_id': 'd704cf8f1216490cbfbed89955f0e938', 'model': 's2.1-pro', 'language': 'fr'}

# Jugement de l'orchestrateur (non mesuré). audience : kids = 6–10, teens = 13–17, adults = 18+.
CURATION = {
    'swiss-data': dict(audience=['teens', 'adults'], confusableWith=['bauhaus-kinetic'],
        promiseEn='One number per screen that lands hard, on a visible 12-column grid, revealed by clean red wipes: a fact understood in 4 seconds.',
        signature=['visible 12-column grid on warm off-white', 'one giant Archivo Black number per screen', 'red wipe transitions', 'palette limited to red / black / blue']),
    'gazette-1900': dict(audience=['teens', 'adults'], confusableWith=[],
        promiseEn='Every big moment arrives as an invented newspaper front page that spins in, lands and gets stamped, with newsreel grain.',
        signature=['broadsheet front page that spins in and lands', 'Playfair Display 900 headline + typewriter dispatch in IBM Plex Mono', 'red rubber stamp', 'sepia + film-grain OpenCV pass']),
    'pixel-arcade': dict(audience=['kids', 'teens', 'adults'], confusableWith=[],
        promiseEn='A real deterministic physics simulation filmed like an arcade game: you bet, you follow, you see the score drop.',
        signature=['dark navy pixel playfield, motion quantised to 4 px', 'Press Start 2P HUD (score, time)', 'real pre-simulated physics with photo finish', 'pixel-mosaic transition + chiptune blips on collisions']),
    'brut-meme': dict(audience=['teens', 'adults'], confusableWith=[],
        promiseEn='Brutalist meme energy: one word or number slams on the beat, black and hazard yellow, giant condensed type.',
        signature=['black / #FFE600 yellow / red only', 'Anton auto-fitted to fill the frame', 'hard cuts on the beat with 3-frame punch-in', 'round stickers and hazard-stripe progress bar', 'photosensitivity rule: <= 3 flashes/s, no full-frame flash']),
    'bauhaus-kinetic': dict(audience=['kids', 'teens', 'adults'], confusableWith=['swiss-data'],
        promiseEn='Primary shapes snapping together on a strict grid: every idea becomes a geometric puzzle solved in 15 seconds.',
        signature=['cream ground with red / yellow / blue / black primary shapes', 'Unbounded 800 headlines', 'grid staggers and shape morphs (flubber)', 'grid-wipe transition']),
    'tableau-craie': dict(audience=['kids', 'teens'], confusableWith=[],
        promiseEn='A kind teacher explains the world by drawing it in chalk: one idea = one diagram that draws itself, then a wipe of the cloth.',
        signature=['dark green chalkboard with chalk grain', 'everything draws itself (Manim Create / stroke-dashoffset)', 'Caveat handwriting + Nunito titles', 'eraser-cloth wipe between ideas']),
    'riso-zine': dict(audience=['teens', 'adults'], confusableWith=[],
        promiseEn='An indie risograph fanzine: overprinted spot inks, misregistration and marker notes, animated on twos.',
        signature=['cream paper with 2–3 overprinted spot inks (fluo pink, blue, yellow)', 'misregistration + halftone dots', 'Space Mono + Permanent Marker annotations', 'stepped 12 fps motion, collage cut-outs']),
    'pastel-diorama': dict(audience=['kids'], confusableWith=[],
        promiseEn='Explain or play with 6–10 year-olds in a soft toy world where every idea bounces into place, never scary or abrupt.',
        signature=['pink pastel toy diorama on a felt base', 'soft rounded toys and invented recurring characters', 'Baloo 2 titles and pill labels', 'bouncy back.out motion']),
    'topo-relief': dict(audience=['teens', 'adults'], confusableWith=['atlas-grave'],
        promiseEn='A 3D topographic expedition: terrain extrudes, contour lines light up, drone fly-overs and an altitude readout.',
        signature=['dark forest-green 3D terrain block with glowing contour lines', 'drone fly-over camera', 'altitude readout in JetBrains Mono', 'ochre / terracotta / teal accents']),
    'atlas-grave': dict(audience=['teens', 'adults'], confusableWith=['topo-relief'],
        promiseEn='Geographic or historical knowledge printed in ink before your eyes on an engraved map that barely moves, ending on an open question.',
        signature=['laid-paper parchment and engraved hand-drawn maps', 'ink that draws itself', 'Cormorant Garamond / Cinzel serif', 'wax seals, compass rose, slow pans']),
    'aquarelle-conte': dict(audience=['kids', 'adults'], confusableWith=['pastel-diorama'],
        promiseEn='Each short is a picture-book page: a breathing watercolour landscape, a small vector character or monument, one short sentence, told by a storyteller.',
        signature=['watercolour washes on cream paper', 'multiplane parallax', 'Fraunces storybook titles on a bottom album page', 'gentle storyteller pacing and fades']),
    'neon-lab': dict(audience=['teens', 'adults'], confusableWith=['liquid-chrome', 'cosmos-doc'],
        promiseEn='A night in the lab where science is seen as light: a real phenomenon staged like a museum visualisation, precise and full of wonder.',
        signature=['near-black lab with cyan / magenta / lime neon', 'bloom pulses on beat changes', 'GLSL force-field background', 'LABO/0X tag + JetBrains Mono data captions']),
    'cosmos-doc': dict(audience=['teens', 'adults'], confusableWith=['neon-lab', 'liquid-chrome'],
        promiseEn='Cinematic space documentary: warm starlight, vertiginous scale, silence and gravity.',
        signature=['true black space with warm starlight and anamorphic lens flare', 'Bebas Neue capitals with tracking that tightens', 'single slow sine easing, slow dolly', 'film grain, no HUD or neon lines']),
    'liquid-chrome': dict(audience=['kids', 'teens', 'adults'], confusableWith=['neon-lab', 'cosmos-doc'],
        promiseEn='Hypnotic liquid chrome matter watched until the end: each short is one continuous satisfying shot where physics is the show.',
        signature=['chrome / iridescent liquid matter in one continuous macro shot', 'Syne 800 titles with a pastel-gradient keyword', 'slow motion, no cuts', 'prefer the warm graphite/pearl background to stay distinct from neon-lab and cosmos-doc']),
}
SHARED = {  # modules identiques (md5) dans les shorts de l'identité — vérifié par ce script
    'swiss-data': ['grille.js'], 'gazette-1900': ['gazette.js', 'post.py'], 'bauhaus-kinetic': ['bk.js'], 'aquarelle-conte': ['aq.js'],
    'atlas-grave': ['atlas.js', 'textures.py'], 'neon-lab': ['field.glsl.js', 'neon_grade.py'], 'brut-meme': ['brut.js'],
    'cosmos-doc': ['cosmos.js'], 'riso-zine': ['riso.js'], 'topo-relief': ['topo.js'],
}


def num(v, default=None):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.search(r'-?\d+(?:[.,]\d+)?', v)
        if m:
            return float(m.group(0).replace(',', '.'))
    if isinstance(v, dict):
        for k in ('default', 'base'):
            if k in v:
                return num(v[k], default)
        for x in v.values():
            r = num(x)
            if r is not None:
                return r
    return default


def slug(family):
    return re.sub(r'[^a-z0-9]+', '-', (family or '').lower()).strip('-') or None


def font(t):
    t = t or {}
    size = t.get('size')
    size_px = num(size) if isinstance(size, (int, float)) or (isinstance(size, str) and re.match(r'\s*\d', size)) else None
    return {'family': t.get('family'), 'fontsourceSlug': slug(t.get('family')), 'weight': t.get('weight'),
            'sizePx': size_px, 'sizeNote': t.get('size') if isinstance(t.get('size'), str) else None}


def core_tokens(t):
    m = t.get('motion', {}) or {}
    dur = m.get('duration', {}) or {}
    vals = {k: num(dur.get(k)) for k in ('fast', 'base', 'slow')}
    ms = any(v is not None and v > 10 for v in vals.values())          # bauhaus-kinetic écrit ses durées en ms
    div = 1000.0 if ms else 1.0
    stag = num(m.get('stagger'))
    if stag is not None and (ms or stag > 10):
        stag = stag / 1000.0
    sa = t.get('safeArea', {}) or {}
    c = t.get('color', {}) or {}
    ty = t.get('typography', {}) or {}
    ease = (m.get('easing') or {})
    return {
        'color': {'bg': c.get('bg'), 'surface': c.get('surface'), 'text': c.get('text'), 'muted': c.get('muted'),
                  'accent': c.get('accent') or [], 'success': c.get('success'), 'danger': c.get('danger')},
        'typography': {'display': font(ty.get('display')), 'title': font(ty.get('title')), 'body': font(ty.get('body')),
                       'caption': font(ty.get('caption'))},
        'motion': {'durationSec': {k: (round(v / div, 4) if v is not None else None) for k, v in vals.items()},
                   'staggerSec': round(stag, 4) if stag is not None else None,
                   'easingRaw': {k: ease.get(k) for k in ('enter', 'exit', 'emphasis')},
                   'hookDeadlineSec': num(m.get('hookDeadline'), 1.0),
                   'sourceUnits': 'ms' if ms else 's'},
        'transitions': [{'name': x.get('name'), 'ffmpegXfade': x.get('ffmpegXfade'), 'durationSec': num(x.get('duration')),
                         'use': x.get('use')} for x in (t.get('transitions') or [])],
        'safeAreaPx': {'top': num(sa.get('top'), 220), 'bottom': num(sa.get('bottom'), 320), 'right': num(sa.get('right'), 120),
                       'left': num(sa.get('left'), 60)},
        'canvas': {'width': 1080, 'height': 1920, 'fps': 30},
    }


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def main():
    recog = json.load(open(OUT / 'report/recognition.json')) if (OUT / 'report/recognition.json').exists() else {}
    nn = {r['short']: r for r in recog.get('rows', [])}
    ids = []
    for rank, s in enumerate(ORDER, 1):
        base = OUT / 'identities' / s
        t = json.load(open(base / 'tokens.json'))
        md = (base / 'identity.md').read_text()
        promise = md.split('## Promesse', 1)[1].split('\n', 1)[1].strip().split('\n')[0].strip('« »"')
        shorts, costs = [], []
        for d in sorted(glob.glob(str(OUT / 'shorts' / f'{s}__*'))):
            n = os.path.basename(d)
            j = json.load(open(os.path.join(d, 'short.json')))
            fr = round(j['duration'] * 30)
            cost = round(j['renderTimeSec'] / fr * 100, 1) if j.get('renderTimeSec') else None
            if cost:
                costs.append(cost)
            r = nn.get(n, {})
            shorts.append({'dir': f'out/shorts/{n}', 'family': j['family'], 'title': j['title'], 'durationSec': j['duration'],
                           'libraries': j['libraries'], 'renderCostSecPer100Frames': cost, 'loopable': bool(j.get('loopable')),
                           'voiced': bool((j.get('sound') or {}).get('voice')),
                           'recognitionNearestShort': r.get('nearest'), 'recognitionSameIdentity': r.get('sameIdentity')})
        shared = []
        for f in SHARED.get(s, []):
            files = sorted(glob.glob(str(OUT / 'shorts' / f'{s}__*' / 'src' / f)))
            if len(files) >= 2 and len({md5(x) for x in files}) == 1:
                shared.append(f'out/shorts/{os.path.basename(os.path.dirname(os.path.dirname(files[0])))}/src/{f}')
        cur = CURATION[s]
        ids.append({
            'id': s, 'name': t.get('name'), 'rank': rank,
            'status': 'rehabilitated' if s in REHAB else 'selected',
            'promiseFr': promise, 'promiseEn': cur['promiseEn'],
            'familiesProven': sorted({x['family'] for x in shorts}),
            'libraries': t.get('libraries'),
            'renderCostSecPer100Frames': {'min': min(costs), 'max': max(costs), 'measuredUnderLoad': True} if costs else None,
            'sharedModule': shared or None,
            'voiceUsed': VOICE,
            'paths': {'identityMd': f'out/identities/{s}/identity.md', 'tokens': f'out/identities/{s}/tokens.json',
                      'recipes': sorted(f'out/identities/{s}/recipes/{os.path.basename(x)}' for x in glob.glob(str(base / 'recipes' / '*.md'))),
                      'poster': f'out/identities/{s}/poster.jpg', 'contactSheet': f'out/identities/{s}/contact-sheet.jpg',
                      'phase1Poster': f'out/report/posters/{s}.jpg'},
            'shorts': shorts,
            'coreTokens': core_tokens(t),
            'curation': {'by': 'orchestrator judgment, not measured', 'audience': cur['audience'],
                         'signatureToPreserve': cur['signature'], 'confusableWith': cur['confusableWith']},
        })
    index = {
        'schemaVersion': '1.0',
        'description': ('Machine index of the 14 visual identities for 9:16 shorts. Use it to shortlist identities, then read each '
                        "identity's identity.md (16 sections, French) and tokens.json. coreTokens is a normalised subset "
                        '(seconds, pixels on a 1080x1920 canvas, @fontsource slugs); the original tokens.json is authoritative for '
                        'everything else. curation.* is orchestrator judgment. See AGENTS.md.'),
        'generatedBy': 'out/tools/build_index.py',
        'rankingCriteria': 'durability/industrialisability: measured render cost 25%, templatability 25%, editorial breadth 20%, recognisability 15%, production risk 15% (out/report/comparison.md §5)',
        'recognition': {'blindJudge14': (recog.get('blindJudge14') or {}).get('pureGroups'), 'blindJudgeGroups': 14,
                        'measuredTop1': f"{sum(1 for r in recog.get('rows', []) if r.get('sameIdentity'))}/{len(recog.get('rows', []))}"},
        'identities': ids,
    }
    json.dump(index, open(OUT / 'identities/index.json', 'w'), ensure_ascii=False, indent=1)
    schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'coreTokens (normalised subset of an identity tokens.json)',
        'type': 'object', 'required': ['color', 'typography', 'motion', 'safeAreaPx', 'canvas'],
        'properties': {
            'color': {'type': 'object', 'required': ['bg', 'accent'], 'properties': {'bg': {'type': 'string'}, 'surface': {'type': ['string', 'null']},
                      'text': {'type': ['string', 'null']}, 'accent': {'type': 'array', 'items': {'type': 'string'}}}},
            'typography': {'type': 'object', 'description': 'each role: family, fontsourceSlug (npm @fontsource/<slug>), weight, sizePx (px on 1080x1920), sizeNote (original free text when not a plain number)'},
            'motion': {'type': 'object', 'properties': {'durationSec': {'type': 'object'}, 'staggerSec': {'type': ['number', 'null']},
                       'easingRaw': {'type': 'object', 'description': 'original easing strings (GSAP, svi.ease or prose)'},
                       'hookDeadlineSec': {'type': 'number'}, 'sourceUnits': {'enum': ['s', 'ms']}}},
            'transitions': {'type': 'array'},
            'safeAreaPx': {'type': 'object', 'description': 'TikTok safe zones; left defaults to 60 when absent from tokens.json',
                           'required': ['top', 'bottom', 'right', 'left']},
            'canvas': {'type': 'object'}}}
    json.dump(schema, open(OUT / 'identities/core-tokens.schema.json', 'w'), ensure_ascii=False, indent=1)
    print(f"{len(ids)} identités -> out/identities/index.json ; modules partagés vérifiés : {sum(bool(i['sharedModule']) for i in ids)}")


if __name__ == '__main__':
    main()
