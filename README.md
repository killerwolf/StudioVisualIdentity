# StudioVisualIdentity

Recherche exploratoire d'identités visuelles et cinématiques pour des shorts verticaux 9:16 (TikTok / Reels / Shorts) :
10 identités, 20 shorts rendus par code (three.js, Matter.js, p5.js, GSAP, D3.js, Manim, A-Frame, Taichi, …), design systems machine-lisibles.

**Point d'entrée : [`out/report/README.md`](out/report/README.md)** (index des identités, recommandation, mode d'emploi pour agents).

- `out/identities/<id>/` — design system (identity.md, tokens.json, recettes, poster, planche-contact)
- `out/shorts/<id>__<famille>__<sujet>/` — short.mp4, short.json, narration.json, stills, src
- `out/library-cards/` — une carte par librairie (coûts mesurés, pièges)
- `out/tools/` — harnais de rendu, son, assemblage, QA, voix off Gemini (`tts.py`)
