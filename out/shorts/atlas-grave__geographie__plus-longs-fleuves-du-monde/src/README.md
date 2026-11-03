# Reproduire (depuis la racine du dépôt)

```
.venv/bin/python out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/src/textures.py out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/src/assets && node out/tools/render.mjs out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/src/index.html --out /tmp/svi/atlas-geo/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/src/sound.json /tmp/svi/atlas-geo/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/atlas-geo/video.mp4 --music /tmp/svi/atlas-geo/music.wav --out out/shorts/atlas-grave__geographie__plus-longs-fleuves-du-monde/short.mp4
```

Fichiers : `index.html` (scène D3 + GSAP, contrat renderAt), `atlas.js` (noyau partagé de l identité : palette, polices, côtes dessinées à la main, couches de planche), `textures.py` (pycairo -> `assets/*.png`), `sound.json` (sound.py).
