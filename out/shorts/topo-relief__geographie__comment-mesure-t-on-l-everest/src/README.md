Reproduire (depuis la racine du dépôt) :

```
mkdir -p /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest && node out/tools/render.mjs out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/src/index.html --out /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/src/sound.json /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest/video.mp4 --music /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest/music.wav --out out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/short.mp4
```

Fichiers : `index.html` (scène, beats, caméra drone), `topo.js` (moteur commun de l'identité topo-relief : heightfield ridged, d3.contours -> textures, maquette three.js + shader « courbes qui s'allument »), `sound.json` (preset drone + SFX calés sur les beats).
Stills de contrôle : `node out/tools/render.mjs out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest/src/index.html --stills 0.5,7.2,9.2,11.6,14.5 --stills-dir /tmp/svi/topo-relief__geographie__comment-mesure-t-on-l-everest/stills`

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/topo-relief__geographie__comment-mesure-t-on-l-everest --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
