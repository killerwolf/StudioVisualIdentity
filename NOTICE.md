# Tiers — Third-party notices

Ce dépôt est sous MIT (code) et CC BY 4.0 (contenu propre), voir `LICENSE` et `LICENSE-CONTENT.md`.
Les éléments ci-dessous appartiennent à des tiers et gardent leur propre licence.

## Fichiers de tiers présents dans le dépôt

- **Polices** (`out/shared/papier-moteur/assets/fonts/`) : Abril Fatface, Courier Prime, DM Mono, DM Serif Display,
  Dela Gothic One, Kalam (SIL Open Font License 1.1) et Special Elite (Apache License 2.0). Textes complets avec les
  copyrights dans `out/shared/papier-moteur/assets/fonts/LICENSES/` (copiés depuis https://github.com/google/fonts).
- **Emoji** (`out/shared/papier-moteur/assets/logos/emoji/`) : Twemoji, © Twitter, Inc. et contributeurs, CC BY 4.0,
  https://github.com/twitter/twemoji. Source de chaque fichier : `logos.json`.
- **Bruitages de la démo** (`out/demo/sfx/`) : CC0, auteurs dans `out/demo/sfx/credits.json` (OpenGameArt).
- **Contenu généré par des services d'IA** : voix off (Fish Audio, Google Gemini), musique et bruitages de la démo
  (ElevenLabs, `out/demo/eleven/SOURCES.md`). Fournis tels quels ; leur usage suit les conditions de chaque fournisseur.
- **Audio du moteur papier** (`out/shared/papier-moteur/assets/audio/`) : fichiers d'essai, droits non établis,
  à remplacer avant tout usage public.

Les logos de marques (Anthropic, Claude, Google, ElevenLabs, Notion…) ont été retirés du dépôt le 2026-11-22.
`out/shared/papier-moteur/pipeline/logos.py` peut en télécharger : leur usage relève du droit des marques, sous votre responsabilité.

## Dépendances (non incluses, installées par npm / pip)

Polices `@fontsource/*` (OFL), D3, GSAP, three.js, p5.js, PixiJS, Matter.js, Paper.js, Zdog, A-Frame, Babylon.js,
anime.js, flubber, twgl.js, Rough.js, topojson-client, world-atlas (données Natural Earth, domaine public),
Playwright ; numpy, scipy, Pillow, OpenCV, pycairo, Matplotlib, Manim, Taichi, shapely, opensimplex.
Chacune garde sa licence (voir `package.json`, `out/library-cards/catalogue.md` et le site de chaque projet).
