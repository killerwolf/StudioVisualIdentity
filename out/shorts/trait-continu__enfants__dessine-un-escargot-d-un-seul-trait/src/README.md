# Reproduire (depuis la racine du dépôt)

```
out/tools/slot.sh .venv/bin/python out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/src/video.py --out /tmp/svi/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/src/sound.json /tmp/svi/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/video.mp4 --music /tmp/svi/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/music.wav --out out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/short.mp4
```

Prérequis : `.venv` avec shapely 2.2.0 et opensimplex 0.4.5.1 (`/root/.local/bin/uv pip install --python .venv/bin/python shapely==2.2.0 opensimplex==0.4.5.1`), pycairo, Pillow, numpy ; ffmpeg ; polices `node_modules/@fontsource/fredoka`.

Fichiers : `traceur.py` (moteur de l'identité, identique dans les deux shorts : chemin shapely en escalier de 12 px, bruit opensimplex calculé une fois et mis en cache dans `/tmp/svi/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/`, plaque, règles, curseurs, chariot, avance plaque, rendu rawvideo bgra → x264), `video.py` (la scène), `sound.json` (musique music-box + événements générés depuis la scène).
Autres modes : `video.py --stills 4,9 --dir /tmp/x` (stills JPEG + ms/image), `video.py --info` (longueurs, jalons, temps), `video.py --sound-json out/shorts/trait-continu__enfants__dessine-un-escargot-d-un-seul-trait/src/sound.json` (régénère les événements sonores, déterministe).
