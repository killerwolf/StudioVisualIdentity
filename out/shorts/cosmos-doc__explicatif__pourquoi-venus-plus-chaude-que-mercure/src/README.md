# cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure

Reproduire (depuis la racine du dépôt) :

```
node out/tools/render.mjs out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/src/index.html --out /tmp/svi/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/src/sound.json /tmp/svi/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/video.mp4 --music /tmp/svi/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/music.wav --out out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/short.mp4
```

`cosmos.js` = module commun de l'identité cosmos-doc (identique dans les deux shorts). Stills : `node out/tools/render.mjs out/shorts/cosmos-doc__explicatif__pourquoi-venus-plus-chaude-que-mercure/src/index.html --stills 0.5,3,6.5,10.5,14.2 --stills-dir /tmp/st`.
