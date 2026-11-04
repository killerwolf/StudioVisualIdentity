# Le test des 3 secondes (Stroop) — brut-meme / engagement

Reproduire (depuis la racine du dépôt) :

```
node out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/src/make_sound.mjs && node out/tools/render.mjs out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/src/index.html --out /tmp/svi/brut-meme__engagement__test-des-3-secondes-stroop/video.mp4 --duration 15.5 && .venv/bin/python out/tools/sound.py out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/src/sound.json /tmp/svi/brut-meme__engagement__test-des-3-secondes-stroop/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/brut-meme__engagement__test-des-3-secondes-stroop/video.mp4 --music /tmp/svi/brut-meme__engagement__test-des-3-secondes-stroop/music.wav --out out/shorts/brut-meme__engagement__test-des-3-secondes-stroop/short.mp4
```

Fichiers : `index.html` (scène PixiJS 8 + GSAP 3, contrat window.ready / renderAt), `brut.js` (moteur partagé de l'identité :
Pixi headless, trame, stickers, caméra punch-in/shake, ajustement des titres), `make_sound.mjs` -> `sound.json` (pulse 120 bpm + SFX sur les cuts).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/brut-meme__engagement__test-des-3-secondes-stroop --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
