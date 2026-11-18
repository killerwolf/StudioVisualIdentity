# Reproduire (depuis la racine du dépôt)

```
export SURVOL_CACHE=/private/tmp/survol-pixel/survol-pixel__explicatif__comment-nait-un-atoll
SVI_SLOTS=4 out/tools/slot.sh .venv/bin/python out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/src/video.py --out $SURVOL_CACHE/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/src/sound.json $SURVOL_CACHE/music.wav && .venv/bin/python out/tools/assemble.py mux --video $SURVOL_CACHE/video.mp4 --music $SURVOL_CACHE/music.wav --out out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/short.mp4 && cp out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/short.mp4 out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/short_novo.mp4
```

Prérequis : `.venv` Python 3.11 avec numpy, scipy, Pillow ≥ 10 (lit les .woff2), opensimplex==0.4.5.1, fontTools (test) ; ffmpeg ; `npm i` pour `@fontsource/jersey-10`, `jersey-15`, `jersey-20` **5.3.0** (épinglées exactement dans package.json). Sur macOS, `nproc` n'existe pas : passer `SVI_SLOTS=4` à `slot.sh` (sinon il boucle).
`SURVOL_CACHE` reçoit le cache du bruit opensimplex (.npy, calculé une fois) et les fichiers intermédiaires ; jamais dans le dépôt.

Fichiers :
- `survol.py` : moteur de l'identité, **copie identique dans chaque short** (même md5) : caméra sténopé unique, lancer de rayon par pixel sur carte de hauteurs en terrasses, plan z = 0 en forme close, cartes réduites par vote majoritaire, brume et ombres par tables d'indices, nuages en piles de disques, panneaux jamais agrandis, cartouches Jersey avec assertions de largeur (≤ 214 px natifs) et de zone sûre, rendu rgb24 → x264.
- `video.py` : la scène (monde, caméra, cartouches, épingles, objets).
- `sound.json` : musique `pad` lydian + souffles, swell, pop, chime (sound.py).
- `test_jersey_grid.py` : test de grille des polices Jersey (C8), sortie non nulle en cas d'écart.
- `dive/` : série du piqué à 90/70/50/30/15° avec le même moteur (preuve C1).

Autres modes : `video.py --stills 0.5,5,10 --dir <d> [--native]` (JPEG + ms/image + nombre de couleurs), `video.py --bench 60` (s/100 images), `video.py --preflight` (caméra au-dessus du relief sur toutes les images), `video.py --dive --dir out/shorts/survol-pixel__explicatif__comment-nait-un-atoll/src/dive`.
