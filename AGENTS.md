# AGENTS.md — how to use this repository to define your own visual identity

## What this repository is

An **exploratory study of visual and cinematic identities for vertical short videos** (TikTok, Reels, Shorts; 1080×1920, 30 fps, 12–19 s).
It contains **14 identities**, each documented as a design system and **proven by 2–3 real shorts rendered by code** (31 shorts in total),
plus the open-source rendering toolkit that made them.

**It is a menu with evidence, not a finished brand.** You are expected to read it and then **define your own identity**:
adopt one identity, blend several, or adapt one to your audience, language and content. Nothing here is a production channel identity.

Most prose is in **French** (identity.md, recipes, reports, tool docstrings). JSON keys are English; many JSON *values* are French.
`out/identities/index.json` gives an English summary of every identity so you can shortlist without reading French first.

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
6. Before building: **`out/report/facts.md`** (verified technical facts and pitfalls) and **`out/library-cards/<lib>.json`**.

## Where to start, by content family

The global ranking (`rank`, `out/report/comparison.md` §5) is for a *generic durable channel* (cost, templatability, breadth);
it does **not** depend on content family. For a given family, start from the identities that actually proved it (global rank in brackets):

| Family | Proven by |
|---|---|
| `explicatif` (explainer / science) | bauhaus-kinetic (5), tableau-craie (6), neon-lab (12), cosmos-doc (13) |
| `histoire` (history) | gazette-1900 (2), topo-relief (9), atlas-grave (10), aquarelle-conte (11) |
| `geographie` (geography) | swiss-data (1), riso-zine (7), topo-relief (9), atlas-grave (10) |
| `evenements` (on this day / countdowns) | swiss-data (1), gazette-1900 (2), brut-meme (4), riso-zine (7), cosmos-doc (13) |
| `engagement` (quiz / vote / bet) | pixel-arcade (3), brut-meme (4), bauhaus-kinetic (5), pastel-diorama (8), liquid-chrome (14) |
| `enfants` (kids) | tableau-craie (6), pastel-diorama (8), aquarelle-conte (11) |
| `abstrait` (satisfying / loops) | pixel-arcade (3), neon-lab (12), liquid-chrome (14) |

**Episode effort** (how much code a new topic needs): *data-driven* — swiss-data (new dataset in the same 4-screen grammar), brut-meme
(new words/numbers), pixel-arcade (new seed / new rules); *new scene per topic* — most others (neon-lab, cosmos-doc, topo-relief,
tableau-craie, atlas-grave, aquarelle-conte, pastel-diorama, gazette-1900 engravings). Tokens are documentation: scene code hard-codes
the values, it does not read `tokens.json`.

## Adapting to an audience (orchestrator judgment, not measured)

All proof shorts use the same French male storyteller voice and ≈ 2.6 words/s; no short was made specifically for teens.
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
     with the same rules — same evidence level.
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
- **Voice-over actually used** for all 31 shorts: Fish Audio "Arnold" (`d704cf8f1216490cbfbed89955f0e938`, model `s2.1-pro`, French male storyteller),
  generated **through the Fish Audio MCP connector**, one call per narration line, saved as `voice_lines/NN.mp3`, then mixed with music
  ducking by `out/tools/tts.py --engine files`. The direct REST engine (`--engine fish`, needs `FISH_API_KEY`, default model
  `s2.1-pro-free`) was **not tested against the real API**. Send only the line text: any style prefix is read aloud. Narration pace ≈ 2.6 words/s; lines must
  not overlap. Gemini voice names that still appear in identity.md / narration.json (`voiceGeminiSuggestion`) are historical casting suggestions
  (Gemini was dropped because of free-tier quotas). For another language, cast a new voice; Arnold is French only.
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
| `out/identities/index.json` | machine index of the 14 identities (start here) — generated by `out/tools/build_index.py` |
| `out/identities/core-tokens.schema.json` | JSON schema of the normalised `coreTokens` |
| `out/identities/<id>/` | design system: `identity.md`, `tokens.json` (original, richer, not normalised), `recipes/`, `poster.jpg`, `contact-sheet.jpg` |
| `out/shorts/<id>__<family>__<topic>/` | proof short: `short.mp4` (voiced), `short_novo.mp4` (no voice), `short.json`, `narration.json`, `voice_lines/`, `stills/`, `src/` |
| `out/library-cards/<lib>.json` | per-library notes merged from the studios: best/avoid, measured costs (under load), gotchas, code paths. Verbose; `_drafts/` holds the raw per-studio drafts |
| `out/report/` | campaign report (French): `README.md`, `comparison.md`, `facts.md`, `failures.md`, `decisions.md`, JSON data (`campaign.json`, `matrix.json`, `recognition.json`, `qa.json`, `selection.json`), Phase 1 `posters/` |
| `out/report/notes/`, `out/report/history/` | studio logs and past session prompts — provenance only, do not follow |
| `out/tools/` | toolkit: `render.mjs` (HTML scene → mp4/stills), `lib/svi.js` (scene helpers), `sound.py`, `textpng.py`, `assemble.py`, `check.py`, `tts.py`, `recognition.py`, `aggregate.py`, `build_index.py`, `templates/`; `STUDIO_BRIEF.md` is the historical brief given to the studios |
| `out/showcase/` | source of the visual showcase page (`build.py` regenerates it) |

## Set-up (only if you render)

From the repository root: `npm i` (libraries + @fontsource fonts from `package.json`); `uv venv --python 3.11 .venv`, then install
numpy, scipy, pillow, opencv-python-headless, pycairo, matplotlib, taichi, and Manim without manimpango (see `out/report/facts.md`);
Playwright + Chromium and ffmpeg must be available. `node_modules/` and `.venv/` are not versioned.
