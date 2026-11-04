Reproduire (depuis la racine du dépôt) :
`mkdir -p /tmp/svi/bauhaus-kinetic__engagement__trouve-l-intrus && node out/tools/render.mjs out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus/src/index.html --out /tmp/svi/bauhaus-kinetic__engagement__trouve-l-intrus/video.mp4 --duration 14 && .venv/bin/python out/tools/sound.py out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus/src/sound.json /tmp/svi/bauhaus-kinetic__engagement__trouve-l-intrus/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/bauhaus-kinetic__engagement__trouve-l-intrus/video.mp4 --music /tmp/svi/bauhaus-kinetic__engagement__trouve-l-intrus/music.wav --out out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus/short.mp4`

Fichiers : `index.html` (scène : Paper.js + flubber + timeline anime.js v4 en pause seekée à t), `bk.js` (noyau de l'identité bauhaus-kinetic : tokens, grille 6×10, géométrie, transition grid-wipe — identique dans les deux shorts), `sound.json` (musique pluck-arp 120 bpm + SFX calés sur les beats).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/bauhaus-kinetic__engagement__trouve-l-intrus --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
