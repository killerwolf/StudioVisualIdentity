# Reproduire (depuis la racine du dépôt)

```
mkdir -p /tmp/svi/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour && node out/tools/render.mjs out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/src/index.html --out /tmp/svi/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/src/sound.json /tmp/svi/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/video.mp4 --music /tmp/svi/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/music.wav --out out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour/short.mp4
```

Fichiers : `index.html` (scène, graine 7, 15 s), `aq.js` (moteur partagé de l identité aquarelle-conte : lavis p5, transitions, grain, vecteur aquarelle Paper.js), `sound.json` (music-box + SFX).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/aquarelle-conte__enfants__ou-vont-les-etoiles-le-jour --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
