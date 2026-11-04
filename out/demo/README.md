# Vidéo démo « 14 styles »

- `demo_16x9.mp4` (1920×1080) et `demo_9x16.mp4` (1080×1920) : 60,6 s, son, voix off anglaise Fish Audio « Energetic Male » (`drama-3`).
- `demo_preview.gif` : 12 premières secondes, muettes, pour le README.

Déroulé : accroche (0–3,2 s, mur de templates identiques « Everyone's video looks the same. ») → les 14 identités réelles →
cinq cycles où l'on entend 1, 2, 3, 5 puis 12 vidéos à la fois, chacune avec sa propre voix
(12 voix Fish Audio différentes, en français, japonais, espagnol, allemand et anglais, sur la musique du short) : un brouhaha en crescendo → silence et « too many choices? » chuchoté →
un agent tape le prompt, le studio produit l'épisode 1 → « 14 styles · 31 videos · open source » → écran de fin.

Fabrication (depuis la racine du dépôt) : `.venv/bin/python out/demo/build.py all` — mosaïque ffmpeg des vraies vidéos
(`base`), calque animé transparent `overlay.html` rendu par `out/tools/render.mjs --alpha`, mix audio par paliers (`audio`),
assemblage (`final`), GIF (`gif`). Géométrie et minutage : `layout.json` (écrit par `build.py`). Voix : `narration.json`, `voice_en/` (narrateur), `brouhaha/` (les 12 voix des tuiles).
