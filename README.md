# StudioVisualIdentity

Recherche exploratoire d'identités visuelles et cinématiques pour des shorts verticaux 9:16 (TikTok / Reels / Shorts) :
**14 identités**, chacune documentée en design system et prouvée par **31 shorts** rendus par code (three.js, Matter.js, p5.js, GSAP, D3.js,
Manim, A-Frame, Taichi, PixiJS, Babylon.js, Matplotlib…), tous voisés (Fish Audio « Arnold »).

**À qui ça sert** : à des agents (ou des humains) qui doivent **définir leur propre identité visuelle** de chaîne de shorts — en reprenant
une identité, en combinant plusieurs, ou en en adaptant une à leur public et à leur langue. Ce n'est pas une identité de marque finie.

**Lancer son propre studio de shorts** (ne pas forker ce dépôt : c'est l'exploration) :

```bash
python3 out/tools/bootstrap_studio.py ../mon-studio --channel-id ma-chaine --name "Ma Chaîne" \
    --from <identité> [--blend <id>,<id>] --families explicatif,engagement --language fr --audience teens --git
```

Cela crée un projet séparé avec : votre identité en brouillon (copie de l'identité source à adapter), un template de scène par
famille de contenu, la boîte à outils de rendu, `studio.json` et un `AGENTS.md` qui décrit la boucle de production
(adapter la marque une fois, puis `new_episode.py` → contenu + narration → stills → rendu → son → voix off → `check.py`).
Détails et choix de l'identité source : [`AGENTS.md`](AGENTS.md).

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
