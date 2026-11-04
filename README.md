# StudioVisualIdentity

Recherche exploratoire d'identités visuelles et cinématiques pour des shorts verticaux 9:16 (TikTok / Reels / Shorts) :
**14 identités**, chacune documentée en design system et prouvée par **31 shorts** rendus par code (three.js, Matter.js, p5.js, GSAP, D3.js,
Manim, A-Frame, Taichi, PixiJS, Babylon.js, Matplotlib…), tous voisés (Fish Audio « Arnold »).

**À qui ça sert** : à des agents (ou des humains) qui doivent **définir leur propre identité visuelle** de chaîne de shorts — en reprenant
une identité, en combinant plusieurs, ou en en adaptant une à leur public et à leur langue. Ce n'est pas une identité de marque finie.

**Par où commencer**
- Agents : **[`AGENTS.md`](AGENTS.md)** (en anglais) — ordre de lecture, méthode pour définir sa propre identité, pièges connus.
- Index machine des identités : [`out/identities/index.json`](out/identities/index.json) (tokens normalisés, public conseillé, signature à préserver, chemins).
- Rapport complet (en français) : [`out/report/README.md`](out/report/README.md) et [`out/report/comparison.md`](out/report/comparison.md).

| Dossier | Contenu |
|---|---|
| `out/identities/<id>/` | design system : `identity.md` (16 sections), `tokens.json`, recettes par famille, poster, planche-contact |
| `out/shorts/<id>__<famille>__<sujet>/` | short de preuve : `short.mp4` (voisé), `short.json`, `narration.json`, `stills/`, `src/` (code + commande de reproduction) |
| `out/library-cards/` | une carte par librairie (coûts mesurés, pièges) |
| `out/tools/` | harnais : rendu, son, assemblage, QA, voix off (`tts.py`), index (`build_index.py`) |
| `out/report/` | rapport, données JSON, faits vérifiés, échecs, décisions |
