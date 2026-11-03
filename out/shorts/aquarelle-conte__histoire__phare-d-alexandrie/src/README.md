# Reproduire (depuis la racine du dépôt)

```
mkdir -p /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie && node out/tools/render.mjs out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/src/index.html --out /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/src/sound.json /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/video.mp4 --music /tmp/svi/aquarelle-conte__histoire__phare-d-alexandrie/music.wav --out out/shorts/aquarelle-conte__histoire__phare-d-alexandrie/short.mp4
```

Fichiers : `index.html` (scène, graine 11, 16 s), `aq.js` (moteur partagé de l identité aquarelle-conte, identique à celui du short enfants), `sound.json` (pad + SFX).
