# Quelle couleur conquiert l'écran ? — Arcade Pixel / engagement (PixiJS)

Reproduire (depuis la racine du dépôt) :

```
node out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/src/simulate.cjs --seed 175 && node out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/src/make_sound.cjs && node out/tools/render.mjs out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/src/index.html --out /tmp/svi/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/video.mp4 --duration 15.5 && .venv/bin/python out/tools/sound.py out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/src/sound.json /tmp/svi/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/video.mp4 --music /tmp/svi/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/music.wav --out out/shorts/pixel-arcade__engagement__quelle-couleur-conquiert-l-ecran/short.mp4
```

Fichiers :
- `conquest.js` — automate de territoire 4 couleurs (111×154 cellules), entiers + mulberry32 uniquement, partagé Node/navigateur.
- `simulate.cjs` — pré-simulation Node ; `--scan 1 300` (78 s) liste les graines valides ; `--seed 175` écrit `trace.json`.
- `index.html` — PixiJS 8.22 : `Application.init({preserveDrawingBuffer:true, autoStart:false})` attendu dans `window.ready`, ticker arrêté ; 17 094 `Particle` 2×2 dans un `ParticleContainer` (couleur dynamique), monde rendu dans une `RenderTexture` 270×480 nearest affichée ×4 ; pixel-mosaic = RenderTexture 1/k ; `app.renderer.render(app.stage)` dans `renderAt`. `window.SEQUENTIAL = true`. `?verify=1` -> SIM OK.
- `make_sound.cjs` — `sound.json` (chiptune 125 bpm, blip du leader sur chaque temps, pops de poussée, coins aux changements de leader).
- `package.json` — `{"type":"commonjs"}` pour `require()` sous la racine ESM.
