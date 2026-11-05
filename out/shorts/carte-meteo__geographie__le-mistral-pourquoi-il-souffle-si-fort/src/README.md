# Reproduire — carte-meteo · geographie · « Le mistral : pourquoi il souffle si fort »

```
node out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/src/precompute.js && node out/tools/render.mjs out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/src/index.html --out /tmp/svi/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/src/sound.json /tmp/svi/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/video.mp4 --music /tmp/svi/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/music.wav --out out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort/short.mp4
```

- `index.html` : scène (canvas 2D unique, `window.renderAt(t)` sans état). Charge `d3.min.js` et `topojson-client.min.js` (UMD) depuis `/node_modules`.
- `meteo.js` : système partagé de l'identité (copie identique dans le short evenements) : décodage world-atlas + filtrage DROM + découpe Europe, caméra, isobares `d3.contours`, vent, passage du front, cartouches, pastilles, pictogrammes.
- `precompute.js` -> `wind.json` : lignes de courant du mistral intégrées en Node (graine 11). Le navigateur ne fait que relire.
- `probe.html` : premier still de preuve de l'identité (France, côte, isobares, 3 pastilles factices, front froid) ; `?prof=1` imprime le coût JS par image.
- `sound.json` : musique `pad` + SFX calés sur les fronts et les pastilles.
- Voix off (non générée ici) : `narration.json`, Fish Audio « Arnold » ; une fois `voice_lines/NN.mp3` produits : `.venv/bin/python out/tools/tts.py out/shorts/carte-meteo__geographie__le-mistral-pourquoi-il-souffle-si-fort --engine files --replace`.
