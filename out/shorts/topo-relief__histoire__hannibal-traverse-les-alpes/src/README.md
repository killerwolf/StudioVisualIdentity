Reproduire (depuis la racine du dépôt) :

```
mkdir -p /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes && node out/tools/render.mjs out/shorts/topo-relief__histoire__hannibal-traverse-les-alpes/src/index.html --out /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/topo-relief__histoire__hannibal-traverse-les-alpes/src/sound.json /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes/video.mp4 --music /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes/music.wav --out out/shorts/topo-relief__histoire__hannibal-traverse-les-alpes/short.mp4
```

Fichiers : `index.html` (Alpes procédurales, itinéraires, 3 cols candidats, caméra drone), `topo.js` (moteur commun topo-relief, identique à celui du short Everest), `sound.json` (preset drone + pas lourds + SFX calés).
Stills de contrôle : `node out/tools/render.mjs out/shorts/topo-relief__histoire__hannibal-traverse-les-alpes/src/index.html --stills 0.6,4.4,7.3,10.6,14.5 --stills-dir /tmp/svi/topo-relief__histoire__hannibal-traverse-les-alpes/stills`
