# Vidéo démo « 14 styles »

- `demo_16x9.mp4` (1920×1080) et `demo_9x16.mp4` (1080×1920) : 51,4 s, son. Narrateur anglais Fish Audio « Energetic Male » (`drama-3`).
- `demo_preview.gif` : 12 premières secondes, muettes, pour le README.

## Déroulé

1. Accroche (0–3,2 s) : un mur de templates identiques, « Everyone's video looks the same. »
2. Les 14 identités réelles.
3. Brouhaha de 10 s : on entend 1, 2, 3, 5 puis 12 vidéos à la fois. Chacune a sa propre voix française (12 voix), sur la musique du short, en crescendo.
4. Silence, puis « too many choices? » chuchoté.
5. Un agent tape le prompt, et le studio produit l'épisode 1 (Swiss Grid, son original). Suivent les épisodes 2 à 4 dans d'autres styles (Cosmos Doc, Brut Meme, Neon Lab), chacun avec une autre voix française qui lit le même texte que la vidéo.
6. « 14 styles · 31 videos · open source », puis l'écran de fin.

## Fabrication

Depuis la racine du dépôt : `.venv/bin/python out/demo/build.py all`. Les étapes :

- `base` : mosaïque ffmpeg des vraies vidéos ;
- `overlay` : calque animé transparent `overlay.html`, rendu par `out/tools/render.mjs --alpha` ;
- `audio` : mix ;
- `final` : assemblage ;
- `gif` : aperçu muet.

La géométrie et le minutage sont dans `layout.json`, écrit par `build.py`. Voix : `narration.json`, `voice_en/` (narrateur), `brouhaha/` (les 12 voix des tuiles, aussi utilisées pour les épisodes 2 à 4).

## Son

Les effets sont encore synthétisés par code (`out/tools/sound.py`). Pour les remplacer par de vrais sons Freesound (CC0), avec `out/tools/freesound.py`, suivre `PROMPT_FREESOUND.md`.
