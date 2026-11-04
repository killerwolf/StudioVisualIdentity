# Reproduire (depuis la racine du dépôt)

```
.venv/bin/python out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/src/textures.py out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/src/assets && node out/tools/render.mjs out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/src/index.html --out /tmp/svi/atlas-hist/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/src/sound.json /tmp/svi/atlas-hist/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/atlas-hist/video.mp4 --music /tmp/svi/atlas-hist/music.wav --out out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522/short.mp4
```

Fichiers : `index.html` (scène D3 + GSAP, contrat renderAt), `atlas.js` (noyau partagé de l identité : palette, polices, côtes dessinées à la main, couches de planche), `textures.py` (pycairo -> `assets/*.png`), `sound.json` (sound.py).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/atlas-grave__histoire__premier-tour-du-monde-1519-1522 --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
