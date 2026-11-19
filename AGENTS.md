# AGENTS.md — how to use this repository to define your own visual identity

## What this repository is

An **exploratory study of visual and cinematic identities for vertical short videos** (TikTok, Reels, Shorts; 1080×1920, 30 fps, 12–19 s).
It contains **19 identities, 22 declinations** (the 14 of the original campaign, the cut-paper identity « Papier découpé » with its 3 derivations added on 2026-11-04 and the 2 identities of
lot 2 of the identity factory added on 2026-11-05, and `lyrics-punchy` and `lyrics-chemin` added on 2026-11-19, see below), each documented as a design system and **proven by 2–3 real shorts rendered by code** (47 shorts in total),
plus the open-source rendering toolkit that made them.

**It is a menu with evidence, not a finished brand.** You are expected to read it and then **define your own identity**:
adopt one identity, blend several, or adapt one to your audience, language and content. Nothing here is a production channel identity.

Most prose is in **French** (identity.md, recipes, reports, tool docstrings). JSON keys are English; many JSON *values* are French.
`out/identities/index.json` gives an English summary of every identity so you can shortlist without reading French first.

## Where this repository fits

- **Choosing a visual identity** is what this repository is for: 19 proven styles (22 declinations), their design systems and their evidence.
- **Running a production channel** needs more than a style: writing, validation, voice, review, publishing and scheduling. Two ways:
  - you already have a studio template (for the owner of this repository, the private **StudioGabarit**, which runs on the Mac and is piloted from Notion): use this repository at its *design system* phase to pick 2–3 candidate styles, then port the chosen signature into that template's own render engine;
  - you don't: `bootstrap_studio.py` below gives a lightweight studio (identity + scene templates + render toolkit) to prototype a style and produce episodes by hand.
- **Shared skills** for any studio (sound design, Gemini voices, Notion piloting) live in [killerwolf/skills](https://github.com/killerwolf/skills).

## Starting a shorts studio from this repository (bootstrap)

Do **not** fork this repository to produce your channel: it is the exploration. Create a separate studio project from it
with one command, then make the brand yours and produce episodes there.

```bash
git clone https://github.com/killerwolf/StudioVisualIdentity && cd StudioVisualIdentity   # or: from the root of your checkout
python3 out/tools/bootstrap_studio.py ../my-studio --channel-id my-channel --name "My Channel" \
    --from <identity> [--blend <id>,<id>] --families <family>,<family> --language fr --audience teens --git
```

- `--from`: the identity whose **signature** you keep (choose it with the sections below). `--blend`: identities that lend a
  *template* for a family the source never proved (it warns you when a family has no template and lists who proved it).
- The studio gets: `AGENTS.md` (its own operating manual), `studio.json` (channel config), `out/identities/<channel-id>/` (**your
  identity**, a BROUILLON copy of the source to adapt), `templates/<family>/` (one proof short's scene code per family, paths
  replaced by `{{SHORT_DIR}}`), `reference/` (read-only source identities + their index entries), `out/tools/` (the render toolkit
  + `new_episode.py`), `package.json`.
- Then, in the studio: `npm i` and a Python 3.11 venv (see its AGENTS.md); **phase 1** — edit the draft identity (name, promise,
  audience/language values, voice) keeping the signature, and restyle the templates (scene code hard-codes colours, fonts and
  French strings); **phase 2, per episode** — `python3 out/tools/new_episode.py <family> <slug> --title "…"`, write the content and
  `narration.json`, render stills, run `short.json.reproduce` (render → sound → mux → voice-over), then `out/tools/check.py`.
- Tested end to end (2026-11-04): a studio bootstrapped from bauhaus-kinetic (+ neon-lab for `abstrait`) rendered a 14 s episode in
  42 s on an idle 4-core machine (10 s / 100 frames), mixed its voice-over and passed `check.py`.

## The cut-paper identity and its 3 derivations (added 2026-11-04, status `added`)

**One identity, three derivations** (decision 2026-11-05): `papier-decoupe` is the root; `atelier-papier`, `carnet-archives` and `cabinet-curiosites` are its derivations (`variantOf: "papier-decoupe"` in `index.json`). They run on the same engine and only change ground, palette and fonts. Directories, ids and slugs are unchanged. A new identity that reuses an existing engine and only changes ground/palette/fonts must be registered as a derivation, not as a new identity. Counting: 17 identities, 20 declinations, 43 shorts.

The cut-paper design system of the **StudioGabarit** template (channels AI Reboot, P'tits Savants, Motion de Culture) and its three
variants from the Un Jour Une Histoire studio, so they can be found and reused like the others:

| Identity | Look | Theme file |
|---|---|---|
| `papier-decoupe` (root) | the template's original: green graduated cutting mat, Dela Gothic One strips, Kalam captions | none (engine defaults) |
| `atelier-papier` | same, warmer: midnight-blue mat, cream / coral / mustard paper | `themes/atelier-papier.json` |
| `carnet-archives` | archive file: kraft ground, Abril Fatface, typewriter captions (Special Elite), sepia + stamp red | `themes/carnet-archives.json` |
| `cabinet-curiosites` | museum cabinet: plain midnight ground, DM Serif Display, cream / teal / burgundy / gold | `themes/cabinet-curiosites.json` |

- They are **not rendered by `render.mjs`**: their scenes are Python (`src/video.py`) and use the template's engine, copied once in
  **`out/shared/papier-moteur/`** (`pipeline/` + `assets/` + `chaine.json` + `themes/`). `src/THEME` picks the theme; `bash src/build.sh`
  writes `narration.json`, renders the voiced short (the engine mixes voice, music and SFX and masters to −14 LUFS, captions burned in)
  and the stills. No `tts.py` step. `bootstrap_studio.py` copies the engine into a studio made from one of them.
- Proof shorts (2 per identity, same text, only the theme changes): `<id>__histoire__la-fourchette-a-fait-scandale`,
  `<id>__explicatif__d-ou-vient-le-mot-sandwich`. Voice: Gemini « Sulafat », reused from the Un Jour Une Histoire studio.
- Not part of the ranking or the blind visual judge; they are appended after rank 16 in `index.json` (ranks 17–20). They are in the
  measured recognition test since 2026-11-05 (each short's nearest neighbour is its sibling).

## Lot 2 of the identity factory (added 2026-11-05, status `added`, ranked)

Made with the `fabrique-identites` skill (`.claude/skills/fabrique-identites/`): scouting from `out/library-cards/catalogue.md`,
adversarial challenge, one studio per identity, integration, review (`out/report/decisions.md` § « Lot 2 »,
`out/report/notes/directions-2026-11-05.md`, `challenge-2026-11-05.md`).

| Identity | Look | Libraries | Rank |
|---|---|---|---|
| `carte-meteo` | light weather map: pale sky-blue sea, tender green land, isobars, dark wind trails, temperature pills, a diagonal weather front as the only transition | D3.js, topojson-client, world-atlas 2.0.2 (Natural Earth) | 5 |
| `trait-continu` | one graphite stair-stepped line never lifted, on a grey plate over a full-bleed orange ground, two rulers with cursors, plate advance in steps | shapely, opensimplex, pycairo, Pillow (Python, no browser) | 9 |

- **Voice-over: Gemini « Sulafat »** (owner decision, 2026-11-05), the cut-paper voice. Fish Audio « Arnold » was planned, but the
  free plan's credits covered 1 line of 20. One Gemini call per short (`gemini-3.8-flash-tts`, lines joined by `<long pause>`, style
  sent as an annotation so it is not read aloud), split into `voice_lines/NN.mp3` in `narration.json` order, mixed by
  `tts.py --engine files --replace` (`short_novo.mp4` = music + SFX). The silence-only split of the gemini-voices skill cut inside a line
  (« Il grandit : ») — the split used word timestamps (faster-whisper) + silences. Log: `out/report/notes/voix-lot2.md`.
- Evidence: a blind visual judge on 8 identities (lot 2 + 6 neighbours, 32 images) made 8/8 pure groups; in the measured test each
  identity's two shorts are each other's nearest neighbour. Render cost measured with the two studios sharing 4 cores (load 1–5.5,
  `measuredUnderLoad: true`). Since the review, carte-meteo's heat-record short has no wind trails: wind is shown only when it is the subject.

## Lyrics punchy (added 2026-11-19, status `added`, unranked)

`lyrics-punchy` opens the content family **`paroles`**: a muted vertical lyric video (the song is added in the app at publication) where every
row is justified to the 876 px column by the width axis of the variable font Anybody, past lines stack into a wall in tints of the
background, and a tilted card illustrates one word per line. Lyrics are always shown in the song's language, never translated (Arabic:
Noto Sans Arabic, right to left, specified but not yet coded). Engine: `out/shared/lyrics-moteur/` (a new episode = a new `lyrics.json`);
tools: `out/tools/lyrics_align.py` (lyrics + word timestamps -> `lyrics.json`, readability rules) and `out/tools/lyrics_audit.mjs`
(frame-by-frame safe-area check). Real lyrics and audio never enter this repository: the proof short uses English filler words.
`render.mjs` also runs with `playwright-core` and an installed Chrome given by `SVI_CHROME`.

## Lyrics chemin (added 2026-11-19, status `added`, unranked)

`lyrics-chemin` is the second `paroles` identity, designed without looking at `lyrics-punchy`: the lyrics are written flat on a blue
architect plan lying on the floor, each word in yellow ink at the moment it is sung, while a top-down camera (translation, rotation, scale,
no perspective) follows the pen tip in one long take — glides, beat-timed turns and one-beat whip pans with real motion blur — and a
one-bar zoom-out on the chorus reveals that the lines were drawing a picture (a paper boat). Engine: `out/shared/chemin-moteur/`
(`chemin.js` + `dessins/<id>.json`; an episode = a lyrics file mapping lines to the drawing's edges); check without rendering:
`out/tools/chemin_audit.mjs` (safe area, sizes, framing, camera speed, overlaps in the final picture). The proof short runs 32.6 s (to the
first chorus): `check.py` accepts up to 60 s for the `paroles` family. Filler lyrics in the repository, real ones outside.

## Read in this order (≈ 10 minutes)

1. **`out/identities/index.json`** — one entry per identity, ranked. For each: English promise, proven content families, libraries,
   measured render cost, `coreTokens` (normalised colours, fonts with @fontsource slugs, durations in seconds, safe areas in px),
   `curation.audience` (kids 6–10 / teens 13–17 / adults), `curation.signatureToPreserve`, `curation.confusableWith`, and paths to everything else.
   `curation.*` is the orchestrator's judgment, not a measurement.
2. **`out/report/directions-contact-sheet.jpg`** and **`out/identities/<id>/contact-sheet.jpg`** — look before you read.
3. For your 2–4 candidates: **`out/identities/<id>/identity.md`** (always the same 16 sections, in this order: name, promise, mood & genre
   references, palette roles, typography, shapes & materials, motion language, camera language, transitions, short structure,
   safe areas, recommended libraries, suitable / unsuitable content families, proof shorts, voice-over placement, risks & limits)
   and **`out/identities/<id>/recipes/<family>.md`** (how to open, structure and close a short of that family in that identity).
4. **Watch the proof shorts**: `out/shorts/<id>__<family>__<topic>/short.mp4` (voiced), with `short.json` (structure, timings, hook,
   engagement mechanic, cost) and `narration.json` (timed voice-over lines).
5. **`out/report/comparison.md`** — side-by-side table, the identity × family × library matrix, blind recognition tests, and the ranking rationale.
6. Before building: **`out/report/facts.md`** (verified technical facts and pitfalls), **`out/library-cards/catalogue.md`** (every
   library and tool considered, used or not, and where; the base for new identities) and **`out/library-cards/<lib>.json`**.

## Where to start, by content family

The global ranking (`rank`, `out/report/comparison.md` §5) is for a *generic durable channel* (cost, templatability, breadth);
it does **not** depend on content family. For a given family, start from the identities that actually proved it (global rank in brackets):

| Family | Proven by |
|---|---|
| `explicatif` (explainer / science) | bauhaus-kinetic (6), tableau-craie (7), neon-lab (14), cosmos-doc (15); cut-paper family (added) |
| `histoire` (history) | gazette-1900 (2), topo-relief (11), atlas-grave (12), aquarelle-conte (13); cut-paper family (added) |
| `geographie` (geography) | swiss-data (1), carte-meteo (5), riso-zine (8), trait-continu (9), topo-relief (11), atlas-grave (12) |
| `evenements` (on this day / countdowns) | swiss-data (1), gazette-1900 (2), brut-meme (4), carte-meteo (5), riso-zine (8), cosmos-doc (15) |
| `engagement` (quiz / vote / bet) | pixel-arcade (3), brut-meme (4), bauhaus-kinetic (6), pastel-diorama (10), liquid-chrome (16) |
| `enfants` (kids) | tableau-craie (7), trait-continu (9), pastel-diorama (10), aquarelle-conte (13) |
| `abstrait` (satisfying / loops) | pixel-arcade (3), neon-lab (14), liquid-chrome (16) |
| `paroles` (lyric video, muted) | lyrics-punchy, lyrics-chemin (added 2026-11-19, unranked) |

**Episode effort** (how much code a new topic needs): *data-driven* — swiss-data (new dataset in the same 4-screen grammar), brut-meme
(new words/numbers), pixel-arcade (new seed / new rules), carte-meteo (mostly: the real map comes from world-atlas; a new topic =
camera framings, pressure centres, a schematic wind field in `precompute.js` and the pills, in the shared `meteo.js`); *new scene per
topic* — most others (neon-lab, cosmos-doc, topo-relief, tableau-craie, atlas-grave, aquarelle-conte, pastel-diorama, gazette-1900
engravings, trait-continu: one hand-designed single-line path per topic in the shared `traceur.py`, contours typed by hand). Tokens are documentation: scene code hard-codes
the values, it does not read `tokens.json`.

## Adapting to an audience (orchestrator judgment, not measured)

The 31 campaign shorts use the same French male storyteller voice and ≈ 2.6 words/s (cut-paper and lot 2: Gemini Sulafat, a warm
female voice; trait-continu is written at 2.2 words/s for kids and measured at ≈ 2.3 words/s once voiced); no short was made specifically for teens.
Suggested starting deltas, to validate with your own tests:

| Audience | Beat length | Voice pace | On-screen words per beat | Voice casting | Hook / CTA |
|---|---|---|---|---|---|
| kids 6–10 | 3–4 s | 2.0–2.3 words/s | ≤ 4 | warm, gentle, recurring character | a child's question; no pressure CTA |
| teens 13–17 | 2–3 s | 2.6–3.0 words/s | ≤ 6, keywords only | younger, energetic, conversational | question in the viewer's own words, challenge or bet in comments |
| adults | 3–4 s | 2.4–2.8 words/s | ≤ 8 | documentary or neutral | a surprising fact; open question |

## How to define your own identity from this work

1. **Write your brief**: audience (age, language), content families, cadence, budget per short (render time), voice.
2. **Shortlist** in `index.json` by `curation.audience`, `familiesProven` and `renderCostSecPer100Frames`.
   Content families used throughout: `abstrait` (abstract/satisfying), `enfants` (kids), `explicatif` (explainer/science),
   `histoire` (history), `geographie` (geography), `evenements` (events/on-this-day/countdowns), `engagement` (quiz/vote/bet).
3. **Decide: adopt, blend or adapt.**
   - *Adopt*: copy the identity's `tokens.json` and `identity.md`, rename, change content.
   - *Blend*: keep **one** identity's `signatureToPreserve` intact (its type pair, palette core and signature transition — that is what
     makes it recognisable, as the blind tests showed). Borrow from others only *structure* (recipes, beat grids, engagement mechanics)
     and *tooling*. Mixing two signatures produces a generic look.
   - *Adapt*: change audience-dependent values (pace, text size, voice, colour temperature — see the table above) but keep the signature.
   - `status` in the index: `selected` = kept in Phase 1; `rehabilitated` = set aside in Phase 1 only to avoid topic overlap, then produced
     with the same rules — same evidence level; `added` = added after the campaign (cut-paper family, unranked; lot 2, ranked, voiced with Gemini Sulafat).
4. **Avoid confusion with neighbours**: check `curation.confusableWith` (e.g. dark identities neon-lab / cosmos-doc / liquid-chrome,
   or the cream flat styles swiss-data / bauhaus-kinetic). If your channel will sit next to one of them, push your palette or type further apart.
5. **Write your design system in the same format**: an `identity.md` with the same 16 sections, and a `tokens.json` whose core follows
   `out/identities/core-tokens.schema.json` (seconds, px on 1080×1920, @fontsource slugs, four-sided safe area). Keep extra blocks
   (`sound`, `layout`, `post`…) if you need them; several identities do.
6. **Prove it**: build 2 shorts from the closest proof short's `src/` (each `src/README.md` and `short.json.reproduce` give the exact
   command). When you copy a proof-short folder, **delete `short_novo.mp4`, `voice_lines/` and `voice_report.json` first**: `tts.py` uses
   `short_novo.mp4` as its video source when present. Shared modules contain French UI strings (e.g. the masthead "LE PETIT CRIEUR" in
   `gazette.js`, `lang="fr"`): grep for them when localising. Check one short with `out/tools/check.py out/shorts/<dir>` (`--all` rewrites
   `out/report/qa.json`); `out/tools/recognition.py` measures that your shorts look more alike than they look like the existing identities,
   but it rewrites `out/report/recognition.json` — run it on a copy if you want to keep the original report.

## Facts you should not have to rediscover

- **Canvas and safe areas**: 1080×1920, 30 fps, H.264 yuv420p. Keep anything important out of the top 220 px, bottom 320 px and right
  120 px (TikTok UI); left margin 60–72 px. Body text ≥ 54 px, titles ≥ 90 px, AA contrast. Hook visible within 1 s.
- **Voice-over, state at 43 shorts**: 31 campaign shorts voiced with Fish Audio "Arnold" (below); the 8 cut-paper shorts declare and
  mix the Gemini voice "Sulafat" (mp3 reused from another studio, mixed by the cut-paper engine, not `tts.py`); the **4 lot 2 shorts
  use Sulafat too** (owner decision: Fish Audio credits ran out before Arnold could be recorded): 4 Gemini calls in all, one per short,
  split into `voice_lines/NN.mp3`, mixed by `tts.py --engine files` (see `out/report/notes/voix-lot2.md`). `tts.py --engine files`
  labels the lines `fish-connector` in `voice_report.json` and `short.json.sound.voiceEngine`: fix the label when the audio comes from
  another engine (done for lot 2).
- **Voice-over actually used** for the 31 campaign shorts: Fish Audio "Arnold" (`d704cf8f1216490cbfbed89955f0e938`, model `s2.1-pro`, French male storyteller),
  generated **through the Fish Audio MCP connector**, one call per narration line, saved as `voice_lines/NN.mp3`, then mixed with music
  ducking by `out/tools/tts.py --engine files`. The direct REST engine (`--engine fish`, needs `FISH_API_KEY`, default model
  `s2.1-pro-free`) was **not tested against the real API**. Send only the line text: any style prefix is read aloud. Narration pace ≈ 2.6 words/s; lines must
  not overlap. Gemini voice names that still appear in identity.md / narration.json (`voiceGeminiSuggestion`) are historical casting suggestions
  (Gemini was dropped for the campaign because of free-tier quotas, ~10 requests/day; one call per short instead of one per line made
  it workable for lot 2). For another language, cast a new voice; Arnold is French only.
- **Factual data** (rule of 2026-11-05, `out/report/decisions.md`): factual geometries, measurements and tables are allowed when their
  licence is public domain, CC0, CC-BY or permissive, when they are distributed by npm or PyPI at an **exact pinned version** (no `^`,
  `==` for pip), **never loaded from the network at render time**, and when their source and licence are written in the identity's
  `identity.md` and in a library card. Images, icons, textures, sounds and any graphic work remain excluded: the visible style is
  generated by code. First use: `world-atlas` 2.0.2 (Natural Earth, public domain; ISC package) for carte-meteo.
- **Captions**: no identity defines burned-in subtitles synced to the voice. Many viewers watch muted; if you need captions, define them
  yourself (inside the safe area, above the bottom 320 px, timings from `narration.json` lines).
- **Photosensitivity (all identities)**: at most 3 flashes per second, no full-frame flash, large luminance swaps ≥ 1.6 s apart
  (rule written for brut-meme; apply it to neon-lab bloom pulses and any flash transition).
- **Colours**: `coreTokens.color.contrastOnBg` gives the computed contrast of each colour; muted/accent colours are often decorative
  (gazette-1900 `muted` is an engraving fill at 1.07:1) — body text needs ≥ 4.5:1.
- **Render costs** in `short.json.renderTimeSec` and in the index were measured with up to 10 renders sharing 4 CPU cores (load 15–23):
  expect roughly 2–3× faster on a dedicated machine. Idle reference: three.js + bloom ≈ 60 s / 100 frames; Manim ≈ 5 s / 100 frames.
  The screenshot capture, not your scene code, dominates browser renders (~0.3 s/frame). What is included differs per identity
  (e.g. riso-zine includes its OpenCV pass, gazette-1900 and neon-lab do not): read `renderCostNote` in the index.
- **Determinism**: every scene exposes `window.renderAt(t)` and is rendered frame by frame (`out/tools/render.mjs`); seeds are in `short.json`.
- **Pitfalls with measured fixes** are in `out/report/facts.md` (e.g. GSAP `tl.seek()` must not be returned, A-Frame geometry as strings,
  `Math.atan2` differs between Node and Chromium for pre-simulated physics, p5 v2 style cache after save/restore, Matplotlib cannot read
  `.woff2`). `out/report/failures.md` lists what failed and why.

## Repository map

| Path | What it is |
|---|---|
| `out/identities/index.json` | machine index of the 19 identities / 22 declinations (start here; `variantOf` links the 3 derivations to `papier-decoupe`) — generated by `out/tools/build_index.py` (ranking and curation are in that script) |
| `out/identities/core-tokens.schema.json` | JSON schema of the normalised `coreTokens` |
| `out/identities/<id>/` | design system: `identity.md`, `tokens.json` (original, richer, not normalised), `recipes/`, `poster.jpg`, `contact-sheet.jpg` |
| `out/shorts/<id>__<family>__<topic>/` | proof short: `short.mp4` (voiced), `short_novo.mp4` (no voice), `short.json`, `narration.json`, `voice_lines/`, `stills/`, `src/` |
| `out/shared/papier-moteur/` | the cut-paper engine (Python) shared by the cut-paper identity and its 3 derivations |
| `out/library-cards/catalogue.md` | catalogue of every library and tool considered (3D, 2D, animation, SVG/data, video frameworks, Python, audio, encoding, services): status, used or not, where — the base to iterate on for new identities |
| `out/library-cards/<lib>.json` | per-library notes merged from the studios: best/avoid, measured costs (under load), gotchas, code paths. Verbose; `_drafts/` holds the raw per-studio drafts |
| `out/report/` | campaign report (French): `README.md`, `comparison.md`, `facts.md`, `failures.md`, `decisions.md`, JSON data (`campaign.json`, `matrix.json`, `recognition.json`, `qa.json`, `selection.json`), Phase 1 `posters/` |
| `out/report/notes/`, `out/report/history/` | studio logs and past session prompts — provenance only, do not follow |
| `out/tools/` | toolkit: `bootstrap_studio.py` (creates a studio project, see above), `render.mjs` (HTML scene → mp4/stills), `lib/svi.js` (scene helpers), `sound.py`, `textpng.py`, `assemble.py`, `check.py`, `tts.py`, `recognition.py`, `aggregate.py`, `build_index.py`, `catalogue_scan.py` (rescans the code against `catalogue.md`), `templates/`; `STUDIO_BRIEF.md` is the historical brief given to the studios |
| `out/showcase/` | source of the visual showcase page (`build.py` regenerates it; `--videos-for <id>` re-encodes one identity's previews) |
| `.claude/skills/fabrique-identites/` | the identity-factory skill: orchestrates scouting, adversarial challenge, studios, integration and review of new identities |

## Set-up (only if you render)

From the repository root: `npm i` (libraries + @fontsource fonts from `package.json`); `uv venv --python 3.11 .venv`, then install
numpy, scipy, pillow, opencv-python-headless, pycairo, matplotlib, taichi, shapely==2.2.0, opensimplex==0.4.5.1, and Manim without
manimpango (see `out/report/facts.md`); `package.json` pins `world-atlas` 2.0.2 exactly and includes `@fontsource/atkinson-hyperlegible`;
Playwright + Chromium and ffmpeg must be available. `node_modules/` and `.venv/` are not versioned.
