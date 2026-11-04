# Reproduire (depuis la racine du dépôt)

```
mkdir -p /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie && node out/tools/render.mjs out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/src/index.html --out /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/src/sound.json /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/video.mp4 --music /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/music.wav --out out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/short.mp4
```

Fichiers : `index.html` (scène, graine 11, 16 s), `aq.js` (moteur partagé de l identité aquarelle-conte, identique à celui du short enfants), `sound.json` (pad + SFX).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/aquarelle-conte__histoire__phare-d-alexandrie --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
