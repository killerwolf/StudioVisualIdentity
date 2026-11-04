# Reproduire — swiss-data · evenements · « J-272 : l'éclipse totale du 2 août 2027 »

```
node out/tools/render.mjs out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/src/index.html --out /tmp/svi/swiss-ecl/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/src/sound.json /tmp/svi/swiss-ecl/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/swiss-ecl/video.mp4 --music /tmp/svi/swiss-ecl/music.wav --out out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/short.mp4
```

- `index.html` : scène (D3 7.9 : SVG, échelles, d3-geo projection équirectangulaire + graticule, d3.line catmull-rom pour la bande ; GSAP 3.15 timeline seekée : compteurs, tracé stroke-dashoffset, volets).
- `grille.js` : système partagé de l'identité (copie identique de celle du short geographie).
- `sound.json` : généré par `mksound.py` (instants des ticks/pops calculés depuis les easings et la géométrie du tracé).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027 --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
