# Journal des décisions (sans validation humaine)

Format : `HH:MM (UTC) — décision — raison`. Début de campagne : 20:27.

- 20:27 — Sortie dans `out/` à la racine du dépôt, `node_modules/` et `.venv/` à la racine (gitignorés) — le serveur de rendu sert la racine, donc toute scène importe `/node_modules/...` et `/out/tools/lib/...` avec des chemins stables.
- 20:28 — Polices : 23 familles @fontsource installées d'emblée — évite les installations concurrentes par les sous-agents.
- 20:30 — Python 3.11 via `uv venv` ; Manim installé `--no-deps` + stub manimpango (Pango absent) ; pas de LaTeX -> ni `Text()` ni `MathTex` : texte en overlays PIL (`textpng.py`).
- 20:31 — L'utilisateur demande en cours de route d'ajouter une voix off Gemini (`GEMINI_API_KEY`). La variable est **absente** du conteneur (API -> 403) et la doc `aistudio.google.com` est bloquée par le réseau. Décision : écrire `out/tools/tts.py` (Gemini TTS, calé sur `narration.json`, ducking de la musique) prêt à l'emploi, continuer la mission sans voix, signaler à l'utilisateur comment ajouter la clé. Aucun faux audio ne remplace la voix.
- 20:35 — `render.mjs` : sémaphore de slots CPU (= nproc = 4) partagé par tous les rendus, pour que 10 studios parallèles ne dépassent jamais 4 rendus simultanés (règle §0).
- 20:45 — Pipelines validés par 3 clips de test de 3 s (three.js, Manim, Taichi) + still A-Frame ; voir `facts.md`.
- 20:50 — 14 directions rédigées (`directions.json`). Les 14 posters sont rendus par 2 sous-agents (7 chacun) via un workflow — écart assumé au « Phase 1 orchestrateur seul » pour gagner du temps mural ; la sélection reste faite par l'orchestrateur.
- 20:50 — Le moteur de workflow plafonne à 2 agents concurrents sur cette machine (4 CPU − 2). Pour la Phase 2 (10 studios), décision : lancer les 10 studios comme sous-agents d'arrière-plan indépendants (outil Agent) plutôt qu'un workflow, sinon 5 vagues successives ; la contrainte réelle (CPU) est tenue par les slots de rendu.
- 20:50 — Poids : le test three.js (particules + bloom) pèse 9,3 Mo pour 3 s en crf 14 (≈ 25 Mb/s). 20+ shorts en crf 14 ≈ 1 Go dans git. Décision : le rendu intermédiaire reste en crf 14 (fait §4) dans /tmp, le livrable `short.mp4` est ré-encodé par `assemble.py mux` en crf 20 plafonné à 8 Mb/s (3,8 Mo pour le même test de 3 s).
- 21:05 — Phase 1 : 14 posters rendus (planche `directions-contact-sheet.jpg`). **Sélection de 10** (`selection.json`) : neon-lab, pastel-diorama, atlas-grave, tableau-craie, swiss-data, pixel-arcade, liquid-chrome, gazette-1900, bauhaus-kinetic, aquarelle-conte. Écartées : cosmos-doc (doublon visuel et thématique de neon-lab), brut-meme (doublon d'usage de pixel-arcade), riso-zine (même format que swiss-data et même sujet qu'atlas-grave), topo-relief (géographie déjà couverte ; première réserve). Couverture : chaque famille ≥ 2, chaque lib A ≥ 1, 8 libs B.
- 21:05 — Sujets assignés par l'orchestrateur à chaque studio pour éviter les doublons de sujets entre identités (ex. la Lune reste à neon-lab, les fleuves à atlas-grave).
- 21:06 — Phase 2/3 : 10 sous-agents studio lancés en parallèle (un par identité), brief commun `out/tools/STUDIO_BRIEF.md`.
