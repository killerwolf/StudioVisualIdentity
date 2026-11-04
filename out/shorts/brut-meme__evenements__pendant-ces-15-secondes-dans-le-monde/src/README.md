# Pendant ces 15 secondes, dans le monde… — brut-meme / evenements

Reproduire (depuis la racine du dépôt) :

```bash
node out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/src/make_sound.mjs && \
  node out/tools/render.mjs out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/src/index.html --out /tmp/svi/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/video.mp4 --duration 16 && \
  .venv/bin/python out/tools/sound.py out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/src/sound.json /tmp/svi/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/music.wav && \
  .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/video.mp4 --music /tmp/svi/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/music.wav --out out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde/short.mp4
```

Fichiers : `index.html` (scène PixiJS 8 + GSAP 3, compteurs = débit × t), `brut.js` (moteur partagé de l'identité, identique à celui du short engagement),
`make_sound.mjs` -> `sound.json` (pulse 120 bpm, impact par cut, blip par naissance, thud par battement).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/brut-meme__evenements__pendant-ces-15-secondes-dans-le-monde --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
