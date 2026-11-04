#!/usr/bin/env python3
"""
bootstrap_studio.py — crée un NOUVEAU projet de studio de shorts à partir de ce dépôt d'exploration.

USAGE (depuis la racine de ce dépôt ; stdlib uniquement)
  python3 out/tools/bootstrap_studio.py ../mon-studio --channel-id labo-ados --name "Labo Ados" \
      --from neon-lab [--blend bauhaus-kinetic,tableau-craie] --families explicatif,engagement \
      [--language fr] [--audience teens] [--git]

CE QUE ÇA PRODUIT (dans ../mon-studio)
  AGENTS.md / README.md        manuel du studio (boucle de production, règles, commandes) — généré
  studio.json                  configuration de la chaîne (nom, langue, public, familles, identités sources, voix, format)
  out/identities/<channel-id>/ VOTRE identité : identity.md + tokens.json + recipes/ copiés de --from, marqués BROUILLON,
                               à adapter (nom, public, langue, voix) — c'est le livrable de la phase « marque »
  templates/<famille>/         une scène de départ par famille : le code (src/), narration.json, short.json d'un short de preuve
                               de l'identité source (ou d'une identité --blend qui a prouvé cette famille)
  out/tools/                   la boîte à outils de rendu (render.mjs, lib/svi.js, sound.py, assemble.py, textpng.py, check.py,
                               tts.py, slot.sh, recognition.py, templates/) + new_episode.py
  reference/                   copie en lecture seule des identités sources (identity.md, tokens.json, contact-sheet.jpg)
                               et de leur entrée dans index.json, + l'URL de ce dépôt
  out/shorts/                  vos épisodes (créés par out/tools/new_episode.py) ; out/report/ (QA)
  package.json, .gitignore     dépendances JS (toutes celles de ce dépôt ; élaguez si besoin)

ENSUITE (dans le studio) : voir le AGENTS.md généré — en bref :
  npm i ; uv venv --python 3.11 .venv ; (paquets Python) ; puis
  python3 out/tools/new_episode.py explicatif pourquoi-la-mer-est-salee --title "Pourquoi la mer est salée ?"
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out'
REPO_URL = 'https://github.com/killerwolf/StudioVisualIdentity'
TOOLS = ['render.mjs', 'sound.py', 'assemble.py', 'textpng.py', 'check.py', 'tts.py', 'slot.sh', 'recognition.py']
SKIP_SRC = {'short.mp4', 'short_novo.mp4', 'short_vo.mp4', 'voice.wav', 'voice_report.json'}


def die(msg):
    print('ERREUR :', msg, file=sys.stderr)
    sys.exit(2)


def load_index():
    p = OUT / 'identities' / 'index.json'
    if not p.exists():
        die('out/identities/index.json absent — lancer python3 out/tools/build_index.py')
    return {i['id']: i for i in json.load(open(p))['identities']}


def pick_template(family, sources, idx):
    """Premier short de preuve de cette famille dans l'ordre des identités sources (--from puis --blend)."""
    for s in sources:
        for sh in idx[s]['shorts']:
            if sh['family'] == family:
                return s, ROOT / sh['dir']
    return None, None


def copy_template(src_short, dest, placeholder):
    """Copie src/, narration.json, short.json ; remplace le nom du dossier source par {{SHORT_DIR}} dans le code."""
    name = src_short.name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_short / 'src', dest / 'src', ignore=shutil.ignore_patterns('__pycache__', 'node_modules'))
    for f in ('narration.json', 'short.json'):
        shutil.copy2(src_short / f, dest / f)
    n, others = 0, set()
    for p in list((dest / 'src').rglob('*')) + [dest / 'narration.json', dest / 'short.json']:
        if p.is_file() and p.suffix in ('.html', '.js', '.mjs', '.py', '.sh', '.json', '.md', '.css', '.txt'):
            s = p.read_text(encoding='utf-8', errors='surrogateescape')
            t = s.replace(name, placeholder)
            t = re.sub(r'/tmp/svi/[A-Za-z0-9_.-]+/', '/tmp/svi/' + placeholder + '/', t)   # un dossier temporaire par épisode
            if t != s:
                p.write_text(t, encoding='utf-8', errors='surrogateescape')
                n += 1
            others |= {m for m in re.findall(r'out/shorts/([a-z0-9-]+__[a-z]+__[a-z0-9-]+)', t)}
    # commande de reproduction : mkdir du dossier temporaire
    sj = json.load(open(dest / 'short.json'))
    rp = sj.get('reproduce') or ''
    if rp and not rp.startswith('mkdir -p /tmp/svi/'):
        sj['reproduce'] = f'mkdir -p /tmp/svi/{placeholder} && ' + rp
        json.dump(sj, open(dest / 'short.json', 'w'), ensure_ascii=False, indent=1)
    # README du template : en-tête + étape voix off propre au studio
    rd = dest / 'src' / 'README.md'
    if rd.exists():
        txt = rd.read_text()
        txt = re.split(r'\n## Dernière étape : voix off', txt)[0].rstrip()
        txt = (f"> **Template de studio** issu du short de preuve `{name}` ({REPO_URL}/tree/main/out/shorts/{name}). "
               "Le contenu (titre, données, textes, timings du son) est celui du short d'origine : **à remplacer** pour chaque épisode.\n\n"
               + txt + "\n\n## Dernière étape : voix off\n\nGénérer un fichier audio par ligne de `narration.json` dans `voice_lines/00.mp3, 01.mp3…` "
               "(texte seul, voix de `studio.json`), puis lancer l'étape `tts.py … --engine files --replace` de `short.json.reproduce`. "
               "Voir `AGENTS.md` du studio, phase 2.\n")
        rd.write_text(txt)
    return n, sorted(o for o in others if o != name)


def draft_identity_md(src_md, name, channel_id, source, blend, language, audience):
    s = src_md.read_text()
    head = (f"> **BROUILLON** — identité de la chaîne « {name} » (`{channel_id}`), dérivée de **{source}**"
            + (f" (emprunts de structure à : {', '.join(blend)})" if blend else '')
            + f". Langue : {language}. Public : {audience}.\n"
            "> À faire avant production : remplacer le nom et la promesse, adapter les valeurs liées au public et à la langue "
            "(rythme, débit de voix, quantité de texte, voix off), **garder la signature** de l'identité source "
            "(voir reference/index-entries.json → curation.signatureToPreserve), puis supprimer ce bandeau.\n\n")
    s = re.sub(r'^## Nom\s*\n+[^\n]*', f'## Nom\n\n{name} (dérivée de {source})', s, count=1, flags=re.M)
    return head + s


STUDIO_AGENTS = """# AGENTS.md — studio « {name} » (`{channel_id}`)

This project is a **shorts production studio** bootstrapped from the exploration repository {repo}
(identity source: **{source}**{blend_txt}). It produces vertical shorts (1080×1920, 30 fps, 12–19 s) for one channel.
Configuration: `studio.json`. Language of the channel: **{language}**. Audience: **{audience}**. Families: {families}.

## Phase 1 — make the brand yours (once)

1. Read `reference/` (the source identity: `identity.md`, `tokens.json`, `contact-sheet.jpg`, `index-entries.json`).
2. Edit **`out/identities/{channel_id}/identity.md`** (16 sections) and **`tokens.json`**: new name and promise, audience-dependent
   values (pace, words per beat, text size, voice), language. **Keep the `signatureToPreserve`** listed in `reference/index-entries.json`
   (type pair, palette core, signature transition) — that is what makes the look recognisable. Remove the BROUILLON banner.
3. Cast the voice (`studio.json` → `voice`). The exploration used Fish Audio "Arnold" (French male storyteller); another language or
   audience needs another voice. Only the line text is sent to TTS (a style prefix is read aloud).
4. Update the scene templates in `templates/<family>/src/` so their hard-coded colours, fonts and strings match your tokens
   (scene code does **not** read `tokens.json`; grep the template for the old hex values, font names and French UI strings).

## Phase 2 — produce an episode (each time)

```bash
python3 out/tools/new_episode.py <family> <slug> --title "<title>"      # copies templates/<family>/ to out/shorts/{channel_id}__<family>__<slug>/
```
Then, in the new folder:
1. **Write** `narration.json` (timed lines, ≈ 2.6 words/s, no overlap) and the on-screen content in `src/` (texts, data, beats).
   Update `short.json` (title, hook, structure, engagement, seed). Templates contain the proof short's topic: replace all of it.
   {audience_row}
   The template's `maxDuration` slots and sound events (`src/sound.json`, or the script that generates it) are tuned for the
   proof short's text and beats: re-time them for your own lines.
2. **Stills first**: `node out/tools/render.mjs out/shorts/<dir>/src/index.html --stills 0.5,4,8,12 --stills-dir out/shorts/<dir>/stills`
   — look at them (hook < 1 s, text ≥ 54 px, titles ≥ 90 px, safe areas: top 220 / bottom 320 / right 120 px, AA contrast).
3. **Render, sound, mux**: run the command in `short.json.reproduce` (it was rewritten for this folder; Python scenes use their own script
   in `src/`, see `src/README.md`). Its last step is the voice-over.
4. **Voice-over**: generate one audio file per narration line into `voice_lines/00.mp3, 01.mp3…` (Fish Audio connector or any TTS),
   then `.venv/bin/python out/tools/tts.py out/shorts/<dir> --engine files --voice "<voice name>" --replace`
   (`--engine fish` with `FISH_API_KEY` exists but was never tested against the real API).
5. **QA**: `.venv/bin/python out/tools/check.py out/shorts/<dir>` must be OK (format, 10–20 s, audio, no black frames, 3–5 stills,
   files present) **and its warnings read**: missing voice-over, lines faster than 3.2 words/s, stills not marked reviewed in `short.json`.

## Rules (from the exploration, measured)

- Determinism: scenes expose `window.renderAt(t)`; stateful scenes set `window.SEQUENTIAL = true`; seeds go in `short.json`.
- Photosensitivity: at most 3 flashes/s, no full-frame flash, large luminance swaps ≥ 1.6 s apart.
- Body text needs ≥ 4.5:1 contrast; decorative colours (see `reference/index-entries.json` → `coreTokens.color.contrastOnBg`) never carry text.
- Pitfalls and fixes: `reference/facts.md` ; library notes: `reference/library-cards/` (copied from {repo}).
- Templates borrowed with `--blend` (see `studio.json` → templates[].note) are **structure references** (pace, mechanic), not a
  second signature: restyle them fully with your tokens, or start from a template of your source identity when one fits.
- Render cost of the source identity (measured under heavy load, expect 2–3× faster on a dedicated machine): see `reference/index-entries.json`.

## Set-up

```bash
npm i
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python numpy scipy pillow opencv-python-headless
```
Add `pycairo matplotlib taichi manim` only if your templates need them (Manim: install without manimpango, see facts.md).
Playwright + Chromium and ffmpeg must be installed on the machine.
"""


NEW_EPISODE = r'''#!/usr/bin/env python3
"""
new_episode.py — crée un épisode à partir d'un template de famille (généré par bootstrap_studio.py).

USAGE (depuis la racine du studio) :
  python3 out/tools/new_episode.py <famille> <slug> [--title "Titre"]
-> out/shorts/<channel-id>__<famille>__<slug>/ (src/, narration.json, short.json) ; les chemins {{SHORT_DIR}} du template
   sont remplacés par le nom du dossier, short.reproduce est réécrit, les sorties de l'épisode source ne sont pas copiées.
"""
import argparse, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('family'); ap.add_argument('slug'); ap.add_argument('--title', default=None)
    a = ap.parse_args()
    cfg = json.load(open(ROOT / 'studio.json'))
    tpl = ROOT / 'templates' / a.family
    if not tpl.exists():
        sys.exit(f"pas de template pour la famille '{a.family}' (disponibles : {', '.join(sorted(p.name for p in (ROOT / 'templates').iterdir()))})")
    slug = re.sub(r'[^a-z0-9-]+', '-', a.slug.lower()).strip('-')
    name = f"{cfg['channelId']}__{a.family}__{slug}"
    dest = ROOT / 'out' / 'shorts' / name
    if dest.exists():
        sys.exit(f'existe déjà : {dest}')
    shutil.copytree(tpl, dest)
    for p in dest.rglob('*'):
        if p.is_file() and p.suffix in ('.html', '.js', '.mjs', '.py', '.sh', '.json', '.md', '.css', '.txt'):
            s = p.read_text(encoding='utf-8', errors='surrogateescape')
            if '{{SHORT_DIR}}' in s:
                p.write_text(s.replace('{{SHORT_DIR}}', name), encoding='utf-8', errors='surrogateescape')
    sj = json.load(open(dest / 'short.json'))
    sj['identity'] = cfg['channelId']; sj['family'] = a.family
    sj['templateFrom'] = sj.get('templateFrom') or 'templates/' + a.family
    if a.title:
        sj['title'] = a.title
    sj['renderTimeSec'] = None
    sj['qualityChecks'] = {'stillsReviewed': False, 'textMinPx': None, 'safeAreaOk': None}
    sj['notes'] = 'TODO'
    sj['TODO'] = 'remplacer hook, structure, engagement, seed et notes (hérités du short de preuve) ; renseigner renderTimeSec et qualityChecks après rendu'
    sj['loopable'] = sj.get('loopable', False)
    sj.setdefault('sound', {})['voice'] = False
    v = cfg.get('voice', {})
    if sj.get('reproduce'):
        sj['reproduce'] = re.sub(r'--voice "[^"]*"', f'--voice "{v.get("displayName", "VOIX")}"', sj['reproduce'])
    json.dump(sj, open(dest / 'short.json', 'w'), ensure_ascii=False, indent=1)
    nj = json.load(open(dest / 'narration.json'))
    nj['language'] = cfg.get('language', nj.get('language'))
    nj['voiceUsed'] = {k: v.get(k) for k in ('provider', 'name', 'reference_id', 'model')}
    nj['TODO'] = 'remplacer les lignes (texte + t + maxDuration) par la narration de cet épisode ; ≈ 2,6 mots/s ; pas de chevauchement'
    nj.pop('voiceGeminiSuggestion', None)
    json.dump(nj, open(dest / 'narration.json', 'w'), ensure_ascii=False, indent=1)
    (dest / 'stills').mkdir(exist_ok=True)
    print(f'épisode créé : out/shorts/{name}')
    print('1) éditer src/ (contenu), narration.json, short.json  2) stills :')
    print(f'   node out/tools/render.mjs out/shorts/{name}/src/index.html --stills 0.5,4,8,12 --stills-dir out/shorts/{name}/stills')
    print('3) rendu + son + mux + voix : commande short.json.reproduce   4) QA :')
    print(f'   .venv/bin/python out/tools/check.py out/shorts/{name}')


if __name__ == '__main__':
    main()
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target')
    ap.add_argument('--channel-id', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--from', dest='source', required=True, help='identité source (son signature sera conservée)')
    ap.add_argument('--blend', default='', help='identités dont on emprunte des templates/recettes, séparées par des virgules')
    ap.add_argument('--families', required=True, help='familles de contenu, séparées par des virgules')
    ap.add_argument('--language', default='fr')
    ap.add_argument('--audience', default='adults', choices=['kids', 'teens', 'adults'])
    ap.add_argument('--git', action='store_true', help='git init + premier commit')
    a = ap.parse_args()

    idx = load_index()
    cid = re.sub(r'[^a-z0-9-]+', '-', a.channel_id.lower()).strip('-')
    blend = [b.strip() for b in a.blend.split(',') if b.strip()]
    for s in [a.source] + blend:
        if s not in idx:
            die(f"identité inconnue '{s}' (connues : {', '.join(idx)})")
    if cid in idx:
        die(f"--channel-id '{cid}' est déjà le nom d'une identité d'exploration : choisissez un nom propre à votre chaîne")
    families = [f.strip() for f in a.families.split(',') if f.strip()]
    target = Path(a.target).resolve()
    if target.exists() and any(target.iterdir()):
        die(f'{target} existe et n’est pas vide')
    target.mkdir(parents=True, exist_ok=True)

    # 1. boîte à outils
    tdst = target / 'out' / 'tools'
    (tdst / 'lib').mkdir(parents=True)
    for f in TOOLS:
        shutil.copy2(OUT / 'tools' / f, tdst / f)
    shutil.copy2(OUT / 'tools' / 'lib' / 'svi.js', tdst / 'lib' / 'svi.js')
    shutil.copytree(OUT / 'tools' / 'templates', tdst / 'templates')
    (tdst / 'new_episode.py').write_text(NEW_EPISODE)
    # identités « papier » (papier-decoupe et ses déclinaisons) : leurs scènes Python utilisent le moteur partagé du gabarit
    srcs = [a.source] + [b.strip() for b in (a.blend or '').split(',') if b.strip()]
    if any('papier-moteur' in (OUT / 'identities' / s / 'tokens.json').read_text() for s in srcs if (OUT / 'identities' / s / 'tokens.json').exists()):
        shutil.copytree(OUT / 'shared' / 'papier-moteur', target / 'out' / 'shared' / 'papier-moteur', ignore=shutil.ignore_patterns('__pycache__'))
    (target / 'out' / 'shorts').mkdir(parents=True)
    (target / 'out' / 'report').mkdir(parents=True)
    pk = json.load(open(ROOT / 'package.json'))
    pk['name'] = cid
    pk['description'] = f'Studio de shorts « {a.name} » — amorcé depuis {REPO_URL} (identité source : {a.source}) ; élaguer les dépendances inutiles'
    json.dump(pk, open(target / 'package.json', 'w'), ensure_ascii=False, indent=2)
    if (ROOT / 'package-lock.json').exists():
        shutil.copy2(ROOT / 'package-lock.json', target / 'package-lock.json')
    (target / '.gitignore').write_text('node_modules\n.venv\n__pycache__/\n*.part.mp4\nout/shorts/*/voice.wav\nout/shorts/*/short_vo.mp4\n')

    # 2. identité de la chaîne (brouillon)
    src_id = OUT / 'identities' / a.source
    bdst = target / 'out' / 'identities' / cid
    (bdst / 'recipes').mkdir(parents=True)
    (bdst / 'identity.md').write_text(draft_identity_md(src_id / 'identity.md', a.name, cid, a.source, blend, a.language, a.audience))
    tok = json.load(open(src_id / 'tokens.json'))
    tok.update({'id': cid, 'name': a.name, 'version': '0.1-draft', 'derivedFrom': {'identity': a.source, 'blend': blend,
                'repo': REPO_URL, 'note': 'brouillon : adapter puis passer en 1.0'}, 'language': a.language, 'audience': a.audience})
    json.dump(tok, open(bdst / 'tokens.json', 'w'), ensure_ascii=False, indent=1)

    # 3. templates + recettes par famille
    report = []
    for fam in families:
        sid, sdir = pick_template(fam, [a.source] + blend, idx)
        if not sid:
            proven = sorted(i for i, e in idx.items() if fam in e['familiesProven'])
            print(f"ATTENTION : aucune identité source n'a prouvé la famille '{fam}' — ajoutez --blend avec l'une de : {', '.join(proven)}")
            continue
        n, others = copy_template(sdir, target / 'templates' / fam, '{{SHORT_DIR}}')
        sj = json.load(open(target / 'templates' / fam / 'short.json'))
        sj['templateFrom'] = f'{REPO_URL}/tree/main/out/shorts/{sdir.name}'
        json.dump(sj, open(target / 'templates' / fam / 'short.json', 'w'), ensure_ascii=False, indent=1)
        rec = OUT / 'identities' / sid / 'recipes' / f'{fam}.md'
        if rec.exists():
            shutil.copy2(rec, bdst / 'recipes' / f'{fam}.md')
        report.append({'family': fam, 'templateFrom': sdir.name, 'identity': sid, 'pathRewrites': n,
                       'referencesOtherShorts': others or None,
                       'note': None if sid == a.source else (f'template emprunté à {sid} : référence de STRUCTURE (rythme, mécanique), '
                                                             f'pas de signature — à restyler entièrement avec vos tokens')})

    # 4. référence
    ref = target / 'reference'
    ref.mkdir()
    entries = {}
    for s in [a.source] + blend:
        d = ref / s
        d.mkdir()
        for f in ('identity.md', 'tokens.json', 'contact-sheet.jpg', 'poster.jpg'):
            if (OUT / 'identities' / s / f).exists():
                shutil.copy2(OUT / 'identities' / s / f, d / f)
        entries[s] = idx[s]
    json.dump(entries, open(ref / 'index-entries.json', 'w'), ensure_ascii=False, indent=1)
    # faits vérifiés + cartes des librairies utilisées (lisibles hors ligne)
    shutil.copy2(OUT / 'report' / 'facts.md', ref / 'facts.md')
    (ref / 'library-cards').mkdir()
    libs = {re.sub(r'[^a-z0-9]+', '-', l.lower()).strip('-') for s in [a.source] + blend for l in (idx[s]['libraries'] or [])}
    for card in (OUT / 'library-cards').glob('*.json'):
        if card.stem in libs:
            shutil.copy2(card, ref / 'library-cards' / card.name)
    (ref / 'README.md').write_text(f'# Référence (lecture seule)\n\nIdentités sources copiées depuis {REPO_URL} (out/identities/).\n'
                                   f'Ne pas modifier : votre identité est dans `out/identities/{cid}/`.\n')

    # 5. configuration + manuel
    voice = {'provider': 'Fish Audio', 'name': 'Arnold', 'reference_id': 'd704cf8f1216490cbfbed89955f0e938', 'model': 's2.1-pro',
             'displayName': 'Fish Audio – Arnold (d704cf8f…)',
             'note': "voix de l'exploration (FR, conteur masculin) — à remplacer si autre langue ou autre public"}
    missing = [f for f in families if f not in {r['family'] for r in report}]
    studio = {'channelId': cid, 'name': a.name, 'language': a.language, 'audience': a.audience,
              'families': [r['family'] for r in report], 'familiesWithoutTemplate': missing,
              'identity': f'out/identities/{cid}/', 'derivedFrom': {'identity': a.source, 'blend': blend, 'repo': REPO_URL},
              'format': {'width': 1080, 'height': 1920, 'fps': 30, 'durationSec': [12, 19],
                         'safeAreaPx': idx[a.source]['coreTokens']['safeAreaPx']},
              'voice': voice, 'templates': report}
    json.dump(studio, open(target / 'studio.json', 'w'), ensure_ascii=False, indent=1)
    blend_txt = f'; structure borrowed from {", ".join(blend)}' if blend else ''
    AUD = {'kids': 'Audience **kids 6–10** (judgment, not measured): beats 3–4 s, 2.0–2.3 words/s, ≤ 4 on-screen words per beat, warm gentle voice.',
           'teens': 'Audience **teens 13–17** (judgment, not measured): beats 2–3 s, 2.6–3.0 words/s, ≤ 6 on-screen words per beat (keywords), younger energetic voice, CTA = challenge/bet in comments.',
           'adults': 'Audience **adults** (judgment, not measured): beats 3–4 s, 2.4–2.8 words/s, ≤ 8 on-screen words per beat, documentary or neutral voice.'}
    (target / 'AGENTS.md').write_text(STUDIO_AGENTS.format(name=a.name, channel_id=cid, repo=REPO_URL, source=a.source, blend_txt=blend_txt,
                                                           language=a.language, audience=a.audience, families=', '.join(r['family'] for r in report),
                                                           audience_row=AUD[a.audience]))
    (target / 'README.md').write_text(f'# {a.name}\n\nStudio de shorts verticaux (chaîne `{cid}`), amorcé depuis {REPO_URL} '
                                      f'(identité source : {a.source}). Mode d’emploi : `AGENTS.md`. Configuration : `studio.json`.\n')
    if a.git:
        subprocess.run(['git', 'init', '-q'], cwd=target, check=True)
        subprocess.run(['git', 'add', '-A'], cwd=target, check=True)
        subprocess.run(['git', 'commit', '-qm', f'Bootstrap du studio {a.name} depuis StudioVisualIdentity ({a.source})'], cwd=target)
    print(f'studio créé : {target}')
    for r in report:
        print(f"  template {r['family']:<11} <- {r['templateFrom']}" + (f"  ({r['note']})" if r['note'] else ''))
    print('suite : lire AGENTS.md dans le studio (npm i, .venv, puis out/tools/new_episode.py)')


if __name__ == '__main__':
    main()
