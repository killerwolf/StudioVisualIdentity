# Reproduire — swiss-data · geographie · « Où vivent les 8 milliards d'humains ? »

```
node out/tools/render.mjs out/shorts/swiss-data__geographie__ou-vivent-8-milliards/src/index.html --out /tmp/svi/swiss-geo/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/swiss-data__geographie__ou-vivent-8-milliards/src/sound.json /tmp/svi/swiss-geo/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/swiss-geo/video.mp4 --music /tmp/svi/swiss-geo/music.wav --out out/shorts/swiss-data__geographie__ou-vivent-8-milliards/short.mp4
```

- `index.html` : scène (D3 7.9 construit le SVG — échelles, grille 12 col., unit chart, barres ; GSAP 3.15 timeline seekée).
- `grille.js` : système partagé de l'identité (tokens, en-tête, wipeLine, volet rouge) — copie identique dans le short evenements.
- `sound.json` : spec son (généré par `mksound.py`, événements calés sur la timeline). `mksound.py` régénère les sound.json des deux shorts.
