# Quelle bille gagne la course ? — Arcade Pixel / engagement

Reproduire (depuis la racine du dépôt) :

```
node out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/simulate.js --seed 17 && node out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/make_sound.cjs && node out/tools/render.mjs out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/index.html --out /tmp/svi/pixel-arcade__engagement__quelle-bille-gagne-la-course/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/src/sound.json /tmp/svi/pixel-arcade__engagement__quelle-bille-gagne-la-course/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/pixel-arcade__engagement__quelle-bille-gagne-la-course/video.mp4 --music /tmp/svi/pixel-arcade__engagement__quelle-bille-gagne-la-course/music.wav --out out/shorts/pixel-arcade__engagement__quelle-bille-gagne-la-course/short.mp4
```

Fichiers :
- `course.js` — monde Matter.js partagé Node/navigateur (rampes, picots, hélices, grille, anti-blocage 1,2 s, journal de collisions).
- `simulate.js` — pré-simulation Node pure ; `--scan 1 600` liste les meilleures graines ; `--seed 17` écrit `trace.json`.
- `index.html` — rendu p5.js v2 (270×480 ×4 nearest), `window.SEQUENTIAL = true`, 4 pas Matter de 8,33 ms par frame. `?verify=1` affiche SIM OK si la course du navigateur = trace Node.
- `make_sound.cjs` — `sound.json` (chiptune 125 bpm + blips sur les collisions de `trace.json`).
- `package.json` — `{"type":"commonjs"}` pour que `require()` marche sous la racine `"type":"module"`.
