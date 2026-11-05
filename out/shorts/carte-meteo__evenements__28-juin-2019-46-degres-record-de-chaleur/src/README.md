# Reproduire — carte-meteo · evenements · « 28 juin 2019 : 46 °C, record de chaleur en France »

```
node out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/src/precompute.js && node out/tools/render.mjs out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/src/index.html --out /tmp/svi/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/src/sound.json /tmp/svi/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/video.mp4 --music /tmp/svi/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/music.wav --out out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur/short.mp4
```

- `index.html` : scène (canvas 2D unique, `window.renderAt(t)` sans état). Charge `d3.min.js` et `topojson-client.min.js` (UMD) depuis `/node_modules`.
- `meteo.js` : système partagé de l'identité, copie identique de celui du short geographie (mistral).
- `precompute.js` -> `wind.json` : lignes de courant d'un flux de sud schématique, intégrées en Node (graine 28).
- `sound.json` : musique `pad` + SFX calés sur les fronts chauds et les pastilles.
- Voix off (non générée ici) : `narration.json`, Fish Audio « Arnold » ; une fois `voice_lines/NN.mp3` produits : `.venv/bin/python out/tools/tts.py out/shorts/carte-meteo__evenements__28-juin-2019-46-degres-record-de-chaleur --engine files --replace`.
