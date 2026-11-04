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
   - *Adapt*: change audience-dependent values (pace, text size, voice, colour temperature) but keep the signature.
4. **Avoid confusion with neighbours**: check `curation.confusableWith` (e.g. dark identities neon-lab / cosmos-doc / liquid-chrome,
   or the cream flat styles swiss-data / bauhaus-kinetic). If your channel will sit next to one of them, push your palette or type further apart.
5. **Write your design system in the same format**: an `identity.md` with the same 16 sections, and a `tokens.json` whose core follows
   `out/identities/core-tokens.schema.json` (seconds, px on 1080×1920, @fontsource slugs, four-sided safe area). Keep extra blocks
   (`sound`, `layout`, `post`…) if you need them; several identities do.
6. **Prove it**: build 2 shorts from the closest proof short's `src/` (each `src/README.md` and `short.json.reproduce` give the exact
   command), run `out/tools/check.py`, and optionally `out/tools/recognition.py` to measure that your two shorts look more alike than
   they look like the existing identities.

## Facts you should not have to rediscover

- **Canvas and safe areas**: 1080×1920, 30 fps, H.264 yuv420p. Keep anything important out of the top 220 px, bottom 320 px and right
  120 px (TikTok UI); left margin 60–72 px. Body text ≥ 54 px, titles ≥ 90 px, AA contrast. Hook visible within 1 s.
- **Voice-over actually used** for all 31 shorts: Fish Audio "Arnold" (`d704cf8f1216490cbfbed89955f0e938`, model `s2.1-pro`, French male storyteller),
  one API call per narration line, mixed with music ducking by `out/tools/tts.py --engine files`. Narration pace ≈ 2.6 words/s; lines must
  not overlap. Gemini voice names that still appear in identity.md / narration.json (`voiceGeminiSuggestion`) are historical casting suggestions
  (Gemini was dropped because of free-tier quotas). For another language, cast a new voice; Arnold is French only.
- **Render costs** in `short.json.renderTimeSec` and in the index were measured with up to 10 renders sharing 4 CPU cores (load 15–23):
  expect roughly 2–3× faster on a dedicated machine. Idle reference: three.js + bloom ≈ 60 s / 100 frames; Manim ≈ 5 s / 100 frames.
  The screenshot capture, not your scene code, dominates browser renders (~0.3 s/frame).
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
