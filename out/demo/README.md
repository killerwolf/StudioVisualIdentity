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

Le sound design utilise de vrais sons CC0 (domaine public) venus d'OpenGameArt : packs Kenney, bart, pyranostudios, Hazmat Harry, Cassie-OrbitGames, rubberduck et wobbleboxx.

- Les sons sont dans `sfx/`, avec auteurs et liens dans `sfx/credits.json`.
- `build.py` (`sfx_samples()`) les pose sur chaque apparition de texte, chaque transition, la frappe clavier, les ✓ et les slams.
- Les quelques événements sans échantillon, comme les nappes « swell », restent synthétisés par `out/tools/sound.py`.
- Le mix est limité à −1 dBFS.

Pour ajouter ou remplacer des sons : `out/tools/freesound.py` (clé `FREESOUND_API_KEY`), ou le skill [`sound-design`](https://github.com/killerwolf/skills/tree/main/skills/sound-design), qui reprend cette méthode pour n'importe quelle vidéo.
