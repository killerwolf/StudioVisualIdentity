# La balle peut-elle s'échapper du cercle ? — Arcade Pixel / abstrait

Reproduire (depuis la racine du dépôt) :

```
node out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/simulate.cjs --seed 1007 && node out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/make_sound.cjs && node out/tools/render.mjs out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/index.html --out /tmp/svi/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/src/sound.json /tmp/svi/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/video.mp4 --music /tmp/svi/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/music.wav --out out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper/short.mp4
```

Fichiers :
- `ring.js` — physique maison (gravité 420 px/s², pas 1/240 s, 8 sous-pas/frame), anneau de 72 tuiles à brèche de 9 tuiles tournant d'une tuile / 3 frames, balle +0,4 px par rebond. Pas d'atan2/hypot dans la boucle -> identique Node / Chromium (vérifié : évasion 11,825 s, 45 rebonds des deux côtés).
- `simulate.cjs` — `--scan 1 1500` cherche une évasion entre 11,4 et 12,4 s avec ≥ 24 rebonds ; `--seed 1007` écrit `trace.json`.
- `index.html` — rendu p5.js v2 (270×480 ×4 nearest), SEQUENTIAL ; `?verify=1` affiche SIM OK.
- `make_sound.cjs` — `sound.json` (chiptune 125 bpm, blip ascendant par rebond, riser + glass + coin à l'évasion).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/pixel-arcade__abstrait__la-balle-peut-elle-s-echapper --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
