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

SCHÉMA 2.0 (2026-11-20, migration.md étape 4) : `identities[]` est inchangé (mêmes champs, mêmes valeurs ; chaque entrée
gagne seulement `habillage`, `variante`, `mecanique`, `formats`, `recette` lus dans out/recettes/<id>.json). L'index gagne
les briques, lues par out/tools/briques.py dans les fiches :
  - `habillages[]`  (out/habillages/ : une famille, ex. craie, et ses variantes craie/ardoise, craie/tableau-vert ; les fiches
                    remplacées restent listées avec statut « remplacee »), `mecaniques[]`, `formats[]`, `recettes[]`
                    (out/recettes/*.json : 27 validées, essais, abandonnées) ;
  - `compatibilite[]` : la matrice creuse habillage × mécanique × format, états CALCULÉS (proposition.md § 5) :
      teste        un short déclare ce triplet et passe check.py (out/report/qa.json) ;
      compatible   adaptateur + image fixe (out/habillages/<id>/planche.jpg), pas de short ;
      a-tester     les rôles de palette exigés par la mécanique sont dans la fiche, la projection ne se contredit pas,
                   pas d'adaptateur (ou adaptateur sans image) ; une contrainte de l'habillage (cadence, grille pixel) qui
                   ne colle pas à la mécanique est signalée dans `alerte` ;
      incompatible seulement avec une raison écrite (out/recettes/propositions.json : C6, C7).
    Les cases proposées non rendues (C3, C5…C8) viennent de out/recettes/propositions.json.
Les dictionnaires en dur (ORDER, CURATION, FAMILIES…) restent la source de identities[] dans cette étape.
"""
import glob, hashlib, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import briques as B  # noqa: E402

# Classement de durabilité (out/report/comparison.md §5). Le lot 2 (2026-11-05, skill fabrique-identites) est classé
# parmi les autres : carte-meteo 5ᵉ, trait-continu 9ᵉ (justification dans comparison.md §5 et decisions.md). Survol pixel (2026-11-18,
# même skill, d'après une vidéo source) est classée 10ᵉ, sous trait-continu et au-dessus de pastel-diorama (comparison.md §5).
ORDER = ['swiss-data', 'gazette-1900', 'pixel-arcade', 'brut-meme', 'carte-meteo', 'bauhaus-kinetic', 'tableau-craie', 'riso-zine',
         'trait-continu', 'survol-pixel', 'pastel-diorama', 'topo-relief', 'atlas-grave', 'aquarelle-conte', 'neon-lab', 'cosmos-doc', 'liquid-chrome',
         # ajoutées le 2026-11-04 (hors campagne de classement) : le papier découpé du gabarit StudioGabarit et ses 3 déclinaisons
         'papier-decoupe', 'atelier-papier', 'carnet-archives', 'cabinet-curiosites',
         # ajoutée le 2026-11-19 (hors classement) : première identité de la famille de contenus « paroles »
         'lyrics-punchy',
         # ajoutée le 2026-11-19 (hors classement) : seconde identité « paroles », conçue sans regarder lyrics-punchy
         'lyrics-chemin']
PAPIER = {'papier-decoupe', 'atelier-papier', 'carnet-archives', 'cabinet-curiosites'}   # non classées, moteur papier partagé
LOT2 = {'trait-continu', 'carte-meteo'}                                                  # lot 2, classées, voix Gemini Sulafat
LYRICS = {'lyrics-punchy', 'lyrics-chemin'}                                                            # vidéo de paroles muette, non classée, sans voix off
SURVOL = {'survol-pixel'}                                                              # 2026-11-18, classée, voix Gemini Sulafat (API v1beta)
ADDED = PAPIER | LOT2 | SURVOL | LYRICS
# Une seule identité « Papier découpé » et trois dérivations (décision du 2026-11-05) : même moteur out/shared/papier-moteur/, même
# pop stop-motion, mêmes bandes inclinées, mêmes sous-titres sur bande ; seuls le fond, la palette et les polices changent.
# Les ids, dossiers et slugs ne changent pas (StudioGabarit les consomme). variantOf = id de la racine, null pour toute autre identité.
FAMILIES = {
    'papier-decoupe': dict(
        variants=['atelier-papier', 'carnet-archives', 'cabinet-curiosites'],
        sharedEngine='out/shared/papier-moteur/',
        shared=['shared engine out/shared/papier-moteur/ (Python, Pillow/OpenCV)', 'stop-motion pop at 12 fps in 4 steps with drop shadow',
                'tilted paper strips for titles', 'burned-in captions on a paper strip', 'same motion, transitions, safe areas and voice (Gemini Sulafat)'],
        varies=['ground (green cutting mat / midnight-blue mat / kraft / plain vignetted midnight blue)', 'palette and paper colours',
                'fonts (Dela Gothic One + Kalam / Abril Fatface + Special Elite / DM Serif Display)', 'theme file out/shared/papier-moteur/themes/<id>.json'],
        axisFr='Même moteur papier-moteur, même pop stop-motion à 12 i/s, mêmes bandes de papier inclinées, mêmes sous-titres sur bande ; '
               'seuls changent le fond (tapis vert, tapis bleu nuit, kraft, bleu nuit uni), la palette et les polices.'),
}
VARIANT_OF = {v: root for root, f in FAMILIES.items() for v in f['variants']}
# Lot 2 : Arnold prévu, crédits Fish Audio épuisés (1 ligne sur 20) ; décision du propriétaire (2026-11-05) : Gemini Sulafat,
# comme les identités papier (1 appel par short, découpé en voice_lines/, mixé par tts.py --engine files ; out/report/notes/voix-lot2.md)
VOICE_LOT2 = {'provider': 'Gemini', 'name': 'Sulafat', 'model': 'gemini-3.8-flash-tts', 'language': 'fr',
              'note': 'owner decision 2026-11-05: Sulafat instead of the planned Fish Audio Arnold (Fish Audio credits ran out); '
                      'one Gemini call per short, split into voice_lines/NN.mp3, mixed by out/tools/tts.py --engine files'}
VOICE_ADDED = {'provider': 'Gemini', 'name': 'Sulafat', 'model': 'gemini-3.8-flash-tts', 'language': 'fr'}
VOICE_SURVOL = {'provider': 'Gemini', 'name': 'Sulafat', 'model': 'gemini-3.8-flash-tts', 'language': 'fr',
                'note': 'owner decision 2026-11-18: one Gemini call per short (API v1beta: the v1 endpoint returns 404 for the TTS model), '
                        'split into voice_lines/NN.mp3 by word timestamps, mixed by out/tools/tts.py --engine files; log out/report/notes/voix-survol-pixel.md'}
PAPIER_MODULE = 'out/shared/papier-moteur/'
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
CURATION.update({
    'trait-continu': dict(audience=['kids'], confusableWith=['tableau-craie'],
        promiseEn='One single line that moves on two axes and is never lifted draws the idea in front of you; then the plate advances and we start again.',
        signature=['full-bleed orange ground with a sharp-cornered grey plate',
                   'one continuous graphite stair-stepped line at constant speed, never lifted',
                   'two rulers with sliding cursors and a carriage at the pen tip',
                   'plate-advance transition in steps',
                   'never cream or white on the orange; Fredoka only']),
    'carte-meteo': dict(audience=['adults', 'teens'], confusableWith=['swiss-data'],
        promiseEn='A clear weather map where isobars breathe, wind runs in dark trails, temperature pills pop, and a weather front sweeps the screen diagonally to move on.',
        signature=['pale sky-blue sea and tender green land with coastline and breathing isobars',
                   'dark wind trails when wind is the subject (proven by the mistral short only)',
                   'temperature pills on white cartouches, Atkinson Hyperlegible + Space Grotesk titles',
                   'diagonal cold-front (blue triangles) / warm-front sweep as the only transition',
                   'map always visible, no tables or bars',
                   'text only on white cartouches']),
})
CURATION.update({
    'survol-pixel': dict(audience=['kids', 'teens', 'adults'], confusableWith=['pixel-arcade', 'topo-relief'],
        promiseEn='Each topic becomes a small 16-bit pixel-art world that one camera flies over, dives into and skims to the horizon: '
                  'the depth of a 90s console game put at the service of a narrated story.',
        signature=['3D depth is the rule: perspective ground (Mode 7 style) at any pitch, terraced heightfield with lit / shaded risers, '
                   'cast shadows, layered depth and a camera that keeps moving forward (one single camera per short)',
                   'form, not content: a pixel-art look for explainers, kids, history and narrated shorts, not a video-game or flight '
                   'theme (no score, no game element; HUD and cockpit optional and absent from the proofs)',
                   'indexed palette with quantised shade tables and a 6-step haze towards a very pale blue (#DCEEF5), rendered at 270x480 and scaled x4 nearest-neighbour',
                   'Jersey 15 cartouches on cream with ink border (hook, dates, narrative; one at a time since the A+B+C pass; Jersey 20 reserved), Jersey 10 mentions only; never text on the map or sky',
                   'cut-away section of the ground (ink base, coloured walls) as the on-ground diagram',
                   'dive / climb-back camera move in true perspective as the signature transition',
                   'no phosphor plate (pixel-arcade) and no "ALT ... M" readout (topo-relief)']),
})
CURATION.update({
    'papier-decoupe': dict(audience=['kids', 'teens', 'adults'], confusableWith=['atelier-papier'],
        promiseEn='Every idea is a cut-out paper piece that pops onto a green cutting mat in stop-motion: a craft table where things get explained with scissors.',
        signature=['green graduated cutting mat', 'Dela Gothic One titles on alternately tilted paper strips', 'pieces pop in 4 steps at 12 fps with drop shadow and scissor-cut edges', 'burned-in Kalam captions on a paper strip']),
    'atelier-papier': dict(audience=['teens', 'adults'], confusableWith=['papier-decoupe'],
        promiseEn='The template cut-paper look, warmer: a midnight-blue cutting mat with cream, coral and mustard paper.',
        signature=['midnight-blue graduated cutting mat', 'Dela Gothic One strips in cream / royal blue / coral', 'stop-motion pop at 12 fps', 'Kalam captions on cream strips']),
    'carnet-archives': dict(audience=['teens', 'adults'], confusableWith=['gazette-1900'],
        promiseEn='Opening an archive file: cream papers on kraft, sepia ink, red rubber stamps and typewriter captions.',
        signature=['fibrous brown kraft ground, no grid', 'Abril Fatface titles on cream / ink-blue / stamp-red strips', 'Special Elite typewriter captions and notes', 'sepia palette with stamp red and ochre']),
    'cabinet-curiosites': dict(audience=['teens', 'adults'], confusableWith=['cosmos-doc'],
        promiseEn='Every object becomes a collection piece: midnight-blue ground, cream and gold museum labels, serif lettering.',
        signature=['plain vignetted midnight-blue ground', 'DM Serif Display titles on cream / teal / burgundy strips', 'DM Serif Display italic captions', 'gold accent for notes']),
})
CURATION.update({
    'lyrics-punchy': dict(audience=['teens', 'adults'], confusableWith=['brut-meme'],
        promiseEn='A muted vertical lyric video where every sung word lands on the beat and fills the column exactly, read lines stack up in tints of the background, and a small drawn card illustrates the word that matters.',
        signature=['column justified by the width axis of the variable font Anybody (wdth 50–150), every row exactly 876 px wide',
                   'a wall of past lines stacked above the current one in 3 tints of the background hue (nuit / lagon / braise)',
                   'tilted accent-coloured square card (±4°) with a 3-colour SVG pictogram, one per line at most',
                   'chute-de-pile: the stack falls out of frame while the ground changes tint at each song section',
                   'never black, no gradient, no camera zoom; the song is added in the app (video rendered muted)']),
})
CURATION.update({
    'lyrics-chemin': dict(audience=['teens', 'adults'], confusableWith=['topo-relief', 'atlas-grave'],
        promiseEn='A muted vertical lyric video shot from above: each word is written in yellow ink on a blue architect plan lying on the floor at the moment it is sung, the camera follows the pen tip in a single sequence shot, and a final zoom-out reveals that the lyrics were drawing a picture (a paper boat).',
        signature=['blueprint-blue folded sheet taped on a warm concrete floor, seen straight from above (no perspective)',
                   'one long take: the camera follows the writing tip with glides, beat-timed hairpin turns and one-beat whip pans with real motion blur',
                   'the sung word alone in fresh yellow ink, drying to ivory; fast passages pre-posed in pencil and inked on the syllable',
                   'Barlow Condensed capitals set rigidly along the strokes of a drawing; red-pencil cross, flag and correction loop',
                   'one-bar zoom-out on the chorus revealing the whole picture, chorus written large in the sea']),
})
VOICE_LYRICS = {'provider': None, 'name': None,
                'note': 'no voice-over: muted lyric video, the song itself is added from the app library at publication; short.mp4 carries a silent track for check.py; exception: the two lyrics-chemin « I Fold » shorts (2026-11-22) bake in an AI-generated song (ElevenLabs Music, Google Lyria 3.5) sung on our filler lyrics'}
SHARED = {  # modules identiques (md5) dans les shorts de l'identité — vérifié par ce script
    'swiss-data': ['grille.js'], 'gazette-1900': ['gazette.js', 'post.py'], 'bauhaus-kinetic': ['bk.js'], 'aquarelle-conte': ['aq.js'],
    'atlas-grave': ['atlas.js', 'textures.py'], 'neon-lab': ['field.glsl.js', 'neon_grade.py'], 'brut-meme': ['brut.js'],
    'cosmos-doc': ['cosmos.js'], 'riso-zine': ['riso.js'], 'topo-relief': ['topo.js'],
    'trait-continu': ['traceur.py'], 'carte-meteo': ['meteo.js'], 'survol-pixel': ['survol.py'],
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
                  'accent': c.get('accent') or [], 'success': c.get('success'), 'danger': c.get('danger'),
                  'contrastOnBg': {k: contrast(v, c.get('bg')) for k, v in
                                   [('text', c.get('text')), ('muted', c.get('muted')), ('success', c.get('success')), ('danger', c.get('danger'))]
                                   + [(f'accent{i + 1}', a) for i, a in enumerate(c.get('accent') or [])]
                                   if isinstance(v, str) and v.startswith('#') and isinstance(c.get('bg'), str)},
                  'textSafeOnBg': 'only colours with contrastOnBg >= 4.5 may be used for body text (>= 3 for titles >= 90 px bold); check identity.md palette roles'},
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


def _lum(h):
    h = h.lstrip('#')[:6]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    try:
        la, lb = sorted((_lum(a), _lum(b)), reverse=True)
        return round((la + 0.05) / (lb + 0.05), 2)
    except Exception:
        return None


# Comment le coût de rendu a été mesuré (renderTimeSec) — à lire avant de comparer les identités
COST_NOTE = {
    'riso-zine': 'includes its mandatory OpenCV post pass',
    'gazette-1900': 'browser render only; the mandatory OpenCV post pass adds 21–28 s/100 frames',
    'neon-lab': 'browser/Matplotlib render only; the OpenCV grade pass adds 15–37 s/100 frames',
    'liquid-chrome': 'Taichi short includes simulation + OpenCV shading; three.js/Babylon shorts are browser only',
    'tableau-craie': 'Manim short 19 s/100; the Rough.js short is 309 s/100 because of a full-frame SVG filter (avoidable)',
}
COST_NOTE_LYRICS = {
    'lyrics-punchy': 'browser render (DOM text with variable-font axis + inline SVG, render.mjs with Chrome 157 via playwright-core); measured with other sessions running (load average 4.5–15); the screenshot capture dominates',
    'lyrics-chemin': 'browser render (canvas 2D, render.mjs with Chrome 157 via playwright-core) including real motion blur (up to 64 sub-frames averaged in floats on camera moves, about a third of the frames); measured with other sessions running (see short.json renderNote)',
}
LYRICS_MODULE = {'lyrics-punchy': 'out/shared/lyrics-moteur/', 'lyrics-chemin': 'out/shared/chemin-moteur/'}
COST_NOTE_LOT2 = {
    'trait-continu': 'Python render (shapely path + pycairo + Pillow text, rawvideo pipe to ffmpeg); opensimplex fields computed once (3.8 s) and cached, '
                     'not included; v2 renders after the review measured with both shorts rendering in parallel (load about 3.3); a v1 control render at low load took 2.8 s/100 frames (identical md5)',
    'carte-meteo': 'browser render (canvas 2D, render.mjs), world-atlas decode + projection once (0.3 s) included; mistral measured with the other lot 2 studio running on 4 cores '
                   '(load 1–3.6), heat-record short re-rendered after the review (no wind trails); an empty canvas page costs 13.2 s/100 frames (screenshot capture alone)',
    'survol-pixel': 'Python render on CPU (numpy ray casting at 270x480, 4 rays per pixel with a majority vote + Pillow text, no browser), full engine run timed, '
                    'world build included (6.5 s / 28.6 s), opensimplex fields cached and not included; renders after the A+B+C pass and the Fable retouch '
                    '(2026-11-18: worlds 3x / 2.4x larger, fine colour map around the subject, 6-step haze, relief shadow, safe-step march on block max maps; '
                    'retouch: more and bigger clouds, foam strokes, lighter forest, wider sugarloaf, tighter sky ramp): atoll 63.9 rendered alone '
                    '(1-min load 3.4–3.8; 82.1 in a first run in parallel with Machu Picchu), Machu Picchu 214.4 (load 2.9–5.0, in parallel with the first atoll run '
                    'for about 8 minutes); A+B+C pass before the retouch: 107.18 and 266.29 (both in parallel, load 4.4–10.4); the owner lifted the cost cap, '
                    'so it is now 1.1–3.6x the 60 s/100 frames target of the challenge (detail pass: 19.6 and 63.1). Optional GPU ray march (SURVOL_GPU=1, '
                    'taichi 1.7.2 on Metal) halves the frame time but is not bit-exact; delivered renders are CPU',
}


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


# ---------- briques (schéma 2.0) ----------
NEUTRES = {'fond', 'surface', 'encre', 'vif', 'second', 'decor', 'serie'}
PUBLIC = lambda d: {k: v for k, v in d.items() if not k.startswith('_')}


def section_briques():
    """habillages[], mecaniques[], formats[], recettes[], compatibilite[] et les compteurs, depuis les fiches."""
    H, M, F, R = B.habillages(), B.mecaniques(), B.formats(), B.recettes()
    qa = {r['short']: r for r in json.load(open(OUT / 'report/qa.json'))} if (OUT / 'report/qa.json').exists() else {}
    shorts = sorted(d.name for d in (OUT / 'shorts').iterdir() if d.is_dir())
    bq = {n: B.briques_du_short(n) for n in shorts}
    rec_de = {}                                    # clé de pâte -> recettes
    for rid, r in R.items():
        rec_de.setdefault(B.pate(r['habillage'], r.get('variante')), []).append(rid)
    for k, h in H.items():                         # une famille liste les recettes de ses variantes
        if h.get('type') == 'famille':
            rec_de[k] = sorted({x for v in h.get('variantes') or [] for x in rec_de.get(v, [])})
    top, pates = B.actifs()
    habs = []
    for k, h in H.items():
        e = PUBLIC(h)
        e.update(fichier=h['_fichier'], recettes=sorted(rec_de.get(k, [])),
                 actif=(k in pates or k in top) and h.get('statut') != 'remplacee')
        habs.append(e)
    mecs = []
    for k, m in M.items():
        e = PUBLIC(m)
        e.update(fichier=m['_fichier'], recettes=sorted(rid for rid, r in R.items() if r['mecanique'] == k),
                 pates=sorted({b['pate'] for b in bq.values() if b['mecanique'] == k}))
        mecs.append(e)
    fmts = [{**PUBLIC(f), 'fichier': f['_fichier']} for f in F.values()]
    recs = []
    for rid, r in R.items():
        e = {k: v for k, v in PUBLIC(r).items() if k not in ('verdict',)}
        e.update(fichier=r['_fichier'], pate=B.pate(r['habillage'], r.get('variante')), dansIdentities=(OUT / 'identities' / rid / 'identity.md').exists())
        if r.get('verdict'):
            e['verdict'] = {k: r['verdict'].get(k) for k in ('cle', 'titre')}
        recs.append(e)
    # ---- compatibilite : cases avec une preuve, un adaptateur ou une proposition (matrice creuse)
    cells = {}
    for n, b in bq.items():
        if b['pate'] and b['mecanique']:
            cells.setdefault((b['pate'], b['mecanique'], b['format']), {'preuve': []})['preuve'].append(f'out/shorts/{n}')
    for k, h in H.items():
        if h.get('statut') == 'remplacee' or h.get('type') == 'famille':
            continue
        for mec in h.get('adaptateurs') or {}:
            if not any(c[0] == k and c[1] == mec for c in cells):
                cells.setdefault((k, mec, None), {'preuve': []})
    for c in B.propositions():
        cells.setdefault((B.pate(c['habillage']), c['mecanique'], c.get('format')), {'preuve': []})['prop'] = c
    out = []
    for (pk, mk, fk), v in sorted(cells.items(), key=lambda x: (x[0][1], x[0][0], x[0][2] or '')):
        h, m = H.get(pk) or {}, M.get(mk) or {}
        fam, _, var = pk.partition('/')
        e = {'habillage': fam, 'variante': var or None, 'pate': pk, 'mecanique': mk, 'format': fk}
        prop = v.get('prop')
        if v['preuve']:
            ok = [d for d in v['preuve'] if (qa.get(d.split('/')[-1]) or {}).get('ok')]
            rids = sorted({bq[d.split('/')[-1]]['recette'] for d in v['preuve']})
            e.update(etat='teste' if ok else 'a-controler', preuve=v['preuve'], recette=rids[0] if len(rids) == 1 else rids,
                     statut=(R.get(rids[0]) or {}).get('statut'))
            if not ok:
                e['raison'] = 'short présent mais pas encore OK dans out/report/qa.json (relancer check.py --all)'
            case = next((R[r].get('case') for r in rids if R.get(r, {}).get('case')), None)
            if case:
                e['case'] = case
        elif prop and prop.get('etat') == 'incompatible':
            e.update(etat='incompatible', raison=prop.get('raison') or '(raison manquante)', case=prop['case'])
        else:
            adapt = (h.get('adaptateurs') or {}).get(mk)
            fold = OUT / 'habillages' / pk.split('/')[0]
            image = (fold / 'planche.jpg').exists()
            req = m.get('requiert') or {}
            miss = [x for x in (req.get('palette') or []) if x in NEUTRES and not (h.get('palette') or {}).get(x)]
            proj_m = req.get('projection')
            proj_h = str((h.get('contraintes') or {}).get('projection') or '')
            alerte = []
            cn = h.get('contraintes') or {}
            if cn.get('cadence') and mk != 'pop-papier-12ips':
                alerte.append(f"cadence imposée par l'habillage ({cn['cadence']}) sur une mécanique fluide (proposition.md § 6)")
            if cn.get('grillePixel') and mk not in ('survol-terrain', 'simulation-deterministe'):
                alerte.append(f"grille pixel de l'habillage ({cn['grillePixel']})")
            if proj_m and proj_h and not proj_h.startswith(proj_m):
                miss.append(f'projection {proj_m} (habillage : {proj_h})')
            if adapt and image:
                e.update(etat='compatible', adaptateur=adapt)
            elif not miss:
                e.update(etat='a-tester', raison=('adaptateur sans image fixe : ' + adapt) if adapt else "rôles exigés par la mécanique présents dans la fiche ; pas d'adaptateur")
            else:
                e.update(etat='inconnu', raison='besoins non remplis : ' + ', '.join(miss))
            if alerte:
                e['alerte'] = alerte
            if prop:
                e['case'] = prop['case']
        if prop:
            e.update({k: prop[k] for k in ('question', 'cout') if prop.get(k)})
        out.append(e)
    counts = {'recettes': len(R), 'recettesParStatut': {s: sum(1 for r in R.values() if r.get('statut') == s) for s in ('validee', 'essai', 'abandonnee')},
              'habillages': len(top), 'pates': len(pates), 'familleshabillage': len(B.familles()),
              'mecaniques': len(M), 'formats': len(F), 'shorts': len(shorts),
              'shortsHorsIdentites': sum(1 for n in shorts if not (OUT / 'identities' / n.split('__')[0]).exists()),
              'cases': {s: sum(1 for c in out if c['etat'] == s) for s in ('teste', 'compatible', 'a-tester', 'incompatible', 'inconnu', 'a-controler')}}
    return {'habillages': habs, 'mecaniques': mecs, 'formats': fmts, 'recettes': recs, 'compatibilite': out}, counts


def main():
    recog = json.load(open(OUT / 'report/recognition.json')) if (OUT / 'report/recognition.json').exists() else {}
    nn = {r['short']: r for r in recog.get('rows', [])}
    ids = []
    for rank, s in enumerate(ORDER, 1):
        base = OUT / 'identities' / s
        t = json.load(open(base / 'tokens.json'))
        md = (base / 'identity.md').read_text()
        # promesse = premier paragraphe de la section (une promesse peut tenir sur plusieurs lignes, ex. survol-pixel)
        promise = ' '.join(md.split('## Promesse', 1)[1].split('\n', 1)[1].strip().split('\n\n')[0].split('\n')).strip('« »"').replace('**', '')
        shorts, costs = [], []
        for d in sorted(glob.glob(str(OUT / 'shorts' / f'{s}__*'))):
            n = os.path.basename(d)
            j = json.load(open(os.path.join(d, 'short.json')))
            fr = round(j['duration'] * 30)
            cost = round(j['renderTimeSec'] / fr * 100, 1) if j.get('renderTimeSec') else None
            if cost:
                costs.append(cost)
            r = nn.get(n, {})
            shorts.append({'dir': f'out/shorts/{n}', 'family': j['family'], **({'declinaison': j['declinaison']} if j.get('declinaison') else {}), 'title': j['title'], 'durationSec': j['duration'],
                           'libraries': j['libraries'], 'renderCostSecPer100Frames': cost, 'loopable': bool(j.get('loopable')),
                           'voiced': bool((j.get('sound') or {}).get('voice')),
                           'recognitionNearestShort': r.get('nearest'), 'recognitionSameIdentity': r.get('sameIdentity')})
        shared = []
        for f in SHARED.get(s, []):
            files = sorted(glob.glob(str(OUT / 'shorts' / f'{s}__*' / 'src' / f)))
            if len(files) >= 2 and len({md5(x) for x in files}) == 1:
                shared.append(f'out/shorts/{os.path.basename(os.path.dirname(os.path.dirname(files[0])))}/src/{f}')
        cur = CURATION[s]
        fam = FAMILIES.get(s)
        ids.append({
            'id': s, 'name': t.get('name'), 'rank': rank,
            'variantOf': VARIANT_OF.get(s),
            **({'variants': fam['variants'], 'variantAxis': {'sharedEngine': fam['sharedEngine'], 'shared': fam['shared'],
                                                             'varies': fam['varies'], 'axisFr': fam['axisFr']}} if fam else {}),
            'status': 'added' if s in ADDED else ('rehabilitated' if s in REHAB else 'selected'),  # rehabilitated = set aside in Phase 1 to avoid topic overlap, produced later; same evidence level
            'promiseFr': promise, 'promiseEn': cur['promiseEn'],
            'familiesProven': sorted({x['family'] for x in shorts}),
            'libraries': [re.sub(r'\s+v?\d+(\.\d+)+', '', re.sub(r'\s+\d+(\.\d+)*$', '', l)).strip() for l in (t.get('libraries') or [])],
            'renderCostNote': ('Python cut-paper engine (Pillow/OpenCV, 4 parallel slices) including voice mix and mastering; measured alone on 4 cores'
                               if s in PAPIER else COST_NOTE_LOT2[s] if s in LOT2 | SURVOL else COST_NOTE_LYRICS[s] if s in LYRICS else
                               COST_NOTE.get(s, 'browser render only (renderTimeSec)') + '; measured with up to 10 renders sharing 4 cores: expect ~2–3x faster on a dedicated machine'),
            'renderCostSecPer100Frames': {'min': min(costs), 'max': max(costs), 'measuredUnderLoad': s not in PAPIER} if costs else None,
            'sharedModule': ([PAPIER_MODULE] if s in PAPIER else [LYRICS_MODULE[s]] if s in LYRICS else shared) or None,
            'voiceUsed': VOICE_SURVOL if s in SURVOL else VOICE_ADDED if s in PAPIER else (VOICE_LOT2 if s in LOT2 else VOICE_LYRICS if s in LYRICS else VOICE),
            'paths': {'identityMd': f'out/identities/{s}/identity.md', 'tokens': f'out/identities/{s}/tokens.json',
                      'recipes': sorted(f'out/identities/{s}/recipes/{os.path.basename(x)}' for x in glob.glob(str(base / 'recipes' / '*.md'))),
                      'poster': f'out/identities/{s}/poster.jpg', 'contactSheet': f'out/identities/{s}/contact-sheet.jpg',
                      'phase1Poster': None if s in ADDED else f'out/report/posters/{s}.jpg'},
            'shorts': shorts,
            'coreTokens': core_tokens(t),
            'curation': {'by': 'orchestrator judgment, not measured', 'audience': cur['audience'],
                         'signatureToPreserve': cur['signature'], 'confusableWith': cur['confusableWith']},
        })
    # confusableWith symétrique
    conf = {i['id']: set(i['curation']['confusableWith']) for i in ids}
    for a, bs in list(conf.items()):
        for b in bs:
            conf.setdefault(b, set()).add(a)
    # les dérivations d'une même racine sont des sœurs voulues, pas un défaut de confusion : on les sort de confusableWith
    family_of = lambda x: VARIANT_OF.get(x, x if x in FAMILIES else None)
    for i in ids:
        sibs = sorted(x['id'] for x in ids if x['id'] != i['id'] and family_of(x['id']) and family_of(x['id']) == family_of(i['id']))
        i['curation']['confusableWith'] = sorted(c for c in conf[i['id']] if c not in sibs)
        if sibs:
            i['curation']['deliberateSiblings'] = sibs
    for i in ids:   # briques de la recette du même id (schéma 2.0) ; les champs existants ne changent pas
        r = B.recettes().get(i['id'])
        if r:
            i.update(recette=r['id'], habillage=r['habillage'], variante=r.get('variante'), mecanique=r['mecanique'], formats=r.get('formats') or [])
    briq, bcounts = section_briques()
    n_var = len(VARIANT_OF)
    n_roots = len(ids) - n_var
    n_shorts = sum(len(i['shorts']) for i in ids)
    index = {
        'schemaVersion': '2.0',
        'description': (f'Machine index of the {n_roots} visual identities for 9:16 shorts ({len(ids)} declinations: {n_var} of them are derivations of a root identity, see variantOf). Use it to shortlist identities, then read each '
                        "identity's identity.md (16 sections, French) and tokens.json. coreTokens is a normalised subset "
                        '(seconds, pixels on a 1080x1920 canvas, @fontsource slugs); the original tokens.json is authoritative for '
                        'everything else. curation.* is orchestrator judgment. See AGENTS.md.'),
        'generatedBy': 'out/tools/build_index.py',
        'counts': {'identities': n_roots, 'derivations': n_var, 'declinations': len(ids), 'shorts': n_shorts, 'briques': bcounts},
        'families': [{'root': r, 'name': next(i['name'] for i in ids if i['id'] == r), 'variants': f['variants'],
                      'sharedEngine': f['sharedEngine'], 'axis': f['axisFr']} for r, f in FAMILIES.items()],
        'fieldNotes': {'variantOf': 'id of the root identity when this entry is a derivation (same engine, only ground / palette / fonts change), else null. A root lists its derivations in variants and what is shared / what varies in variantAxis. Derivations stay ranked, right after their root; counts.identities counts roots only, counts.declinations counts every entry. curation.deliberateSiblings = derivations of the same root, deliberately close and therefore not listed in confusableWith. A new identity that reuses an existing engine and only changes ground / palette / fonts must be registered as a derivation, not as a new identity',
                       'status': 'selected = kept in Phase 1; rehabilitated = set aside in Phase 1 only to avoid topic overlap with a neighbour, then produced on request with the same rules and evidence level; added = added after the campaign: (a) the cut-paper identity from the StudioGabarit template, papier-decoupe, and its 3 derivations (atelier-papier, carnet-archives, cabinet-curiosites), rendered by the shared Python engine out/shared/papier-moteur/, appended after the ranked identities and not part of the ranking or the blind visual judge; (b) lot 2 of the identity factory (trait-continu, carte-meteo, 2026-11-05: scouting + adversarial challenge + studio + review), ranked with the others, blind visual judge on 8 identities (lot 2 + 6 neighbours, 8/8 pure groups, out/report/notes/revue-2026-11-05.md), voice-over Gemini Sulafat like the cut-paper family (owner decision: Fish Audio credits ran out before Arnold could be recorded); (c) survol-pixel (2026-11-18, same skill, style taken from a source pixel-art flight video), ranked with the others, voice-over Gemini Sulafat (owner decision 2026-11-18, API v1beta), blind visual judge on 6 identities during its review (survol-pixel + pixel-arcade, carte-meteo, topo-relief, pastel-diorama, trait-continu; 6/6 pure groups, 24/24 images, recognition.json blindJudgeSurvol); (d) lyrics-punchy and lyrics-chemin (2026-11-19), the two identities of the new content family `paroles` (muted lyric video, no voice-over), unranked, appended last, one proof short each rendered with filler lyrics (real lyrics and audio stay outside the repository); lyrics-chemin later got narrated and sung declinations, among them two « I Fold » shorts (2026-11-22) whose AI-generated song, sung on our filler lyrics, is baked into short.mp4',
                       'voiceUsed': 'voice actually mixed into short.mp4 (Fish Audio Arnold for the 31 campaign shorts, Gemini Sulafat for the 8 cut-paper, 4 lot 2 and 2 survol-pixel shorts, i.e. 31 Arnold + 14 Sulafat; see shorts[].voiced)',
                       'coreTokens.motion.staggerSec': "the identity's default stagger as written in its tokens.json; meaning varies (per-item stagger for most, spacing between beats/captions for atlas-grave 1.5 and liquid-chrome 1.55, title-to-body delay for neon-lab 0.8)",
                       'coreTokens.motion.durationSec.slow': 'longest standard duration; for gazette-1900 it is one page (6 beats at 128 bpm)',
                       'coreTokens.color.contrastOnBg': 'WCAG contrast ratio against bg, computed; muted/accent colours are often decorative (e.g. gazette-1900 muted = engraving fill, 1.07:1) and must not carry text',
                       'renderCostSecPer100Frames': 'see renderCostNote: what is included differs per identity'},
        'rankingCriteria': 'durability/industrialisability: measured render cost 25%, templatability 25%, editorial breadth 20%, recognisability 15%, production risk 15% (out/report/comparison.md §5)',
        'recognition': {'blindJudge14': (recog.get('blindJudge14') or {}).get('pureGroups'), 'blindJudgeGroups': 14,
                        'blindJudgeLot2': (recog.get('blindJudgeLot2') or {}).get('pureGroups'), 'blindJudgeLot2Groups': (recog.get('blindJudgeLot2') or {}).get('groups'),
                        'blindJudgeSurvol': (recog.get('blindJudgeSurvol') or {}).get('pureGroups'), 'blindJudgeSurvolGroups': (recog.get('blindJudgeSurvol') or {}).get('groups'),
                        'blindJudgeGlobal': (recog.get('blindJudgeGlobal') or {}).get('pureGroups'), 'blindJudgeGlobalGroups': (recog.get('blindJudgeGlobal') or {}).get('groups'),
                        # un short seul de son identité (sansPair, recognition.py) n'a pas de voisin possible : ni réussite ni échec
                        'measuredTop1': f"{sum(1 for r in recog.get('rows', []) if r.get('sameIdentity'))}/{sum(1 for r in recog.get('rows', []) if not r.get('sansPair'))}"},
        'identities': ids,
        'briquesNote': ('Composition model (2026-11-19/20, out/report/notes/composition/proposition.md): video = habillage (look) x mecanique '
                        '(motion) x format (+ son); a named, validated combination is a recette (same id as the identity it comes from). '
                        'Sections below are read from out/habillages, out/mecaniques, out/formats, out/recettes by out/tools/briques.py. '
                        'compatibilite[] is a sparse matrix; etat is computed (teste / compatible / a-tester / incompatible with a written raison / inconnu). '
                        'niveau: executable = an adapter exists and the engine applies it; declare = values recorded, scene code hard-codes them.'),
        **briq,
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
    print(f"briques : {bcounts}")


if __name__ == '__main__':
    main()
