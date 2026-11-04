# cosmos-doc__evenements__voyager-1-a-un-jour-lumiere

Reproduire (depuis la racine du dépôt) :

```
node out/tools/render.mjs out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/src/index.html --out /tmp/svi/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/src/sound.json /tmp/svi/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/video.mp4 --music /tmp/svi/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/music.wav --out out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/short.mp4
```

`cosmos.js` = module commun de l'identité cosmos-doc (identique dans les deux shorts). Stills : `node out/tools/render.mjs out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere/src/index.html --stills 0.5,3,6.5,10.5,14.2 --stills-dir /tmp/st`.

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/cosmos-doc__evenements__voyager-1-a-un-jour-lumiere --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
