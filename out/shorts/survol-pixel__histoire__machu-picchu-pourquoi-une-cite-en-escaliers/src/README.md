# Reproduire (depuis la racine du dépôt)

```
export SURVOL_CACHE=/private/tmp/survol-pixel/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers
SVI_SLOTS=4 out/tools/slot.sh .venv/bin/python out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/src/video.py --out $SURVOL_CACHE/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/src/sound.json $SURVOL_CACHE/music.wav && .venv/bin/python out/tools/assemble.py mux --video $SURVOL_CACHE/video.mp4 --music $SURVOL_CACHE/music.wav --out out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/short.mp4 && cp out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/short.mp4 out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/short_novo.mp4
```

Prérequis : `.venv` Python 3.11 avec numpy, scipy, Pillow ≥ 10 (lit les .woff2), opensimplex==0.4.5.1, fontTools (test) ; ffmpeg ; `npm i` pour `@fontsource/jersey-10`, `jersey-15`, `jersey-20` **5.3.0** (épinglées exactement dans package.json). Sur macOS, `nproc` n'existe pas : passer `SVI_SLOTS=4` à `slot.sh` (sinon il boucle).
`SURVOL_CACHE` reçoit le cache du bruit opensimplex (.npy, calculé une fois) et les fichiers intermédiaires ; jamais dans le dépôt.

Fichiers :
- `survol.py` : moteur de l'identité, **copie identique dans chaque short** (même md5) : caméra sténopé unique interpolée en PCHIP, lancer de **4 rayons par pixel** sur carte de hauteurs en terrasses avec **vote majoritaire** sur l'indice de palette, marche à pas sûrs sur des cartes de maxima par blocs (128/32/8/2) puis 8 bissections, plan z = 0 en forme close, carte de couleurs fine sur la fenêtre du sujet, ombre portée du relief, ombres et **brume en 6 paliers** par tables d'indices, ciel en 7 paliers, nuages en tas de boules de coton (hachure, liseré bleuté, ombres), arbres en grappes (ombre portée), moucheture des contremarches et murs appareillés, panneaux jamais agrandis, cartouches Jersey avec assertions de largeur (≤ 214 px natifs) et de zone sûre, rendu rgb24 → x264. État : passe A+B+C du 18/11/2026.
- `survol_gpu.py` : marche des rayons sur GPU, **facultative et expérimentale** (voir plus bas), même fichier dans les deux shorts.
- `video.py` : la scène (monde, caméra, cartouches, épingles, objets).
- `sound.json` : musique `pad` lydian + souffles, swell, pop, chime (sound.py).
- `test_jersey_grid.py` : test de grille des polices Jersey (C8), sortie non nulle en cas d'écart.
- `dive/` : série du piqué à 90/70/50/30/15° avec le même moteur (preuve C1), régénérée après la passe A+B+C.

Autres modes : `video.py --stills 0.5,5,10 --dir <d> [--native]` (JPEG + ms/image + nombre de couleurs), `video.py --bench 60` (s/100 images), `video.py --preflight` (caméra au-dessus du relief sur toutes les images), `video.py --dive --dir out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/src/dive`.

Voix : la commande ci-dessus produit `short.mp4` sans voix ; la voix (`voice_lines/`, Gemini Sulafat, déjà enregistrée) est
mixée ensuite par `.venv/bin/python out/tools/tts.py out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers --engine files --replace` (voir `short.json.reproduce`).
Stills de `stills/` : `video.py --stills 0.5,7.0,12.4,17.5 --dir <d>`, puis renommés comme les fichiers présents.

## Marche sur GPU (facultatif, expérimental)

```
export SURVOL_CACHE=/private/tmp/survol-pixel/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers
SURVOL_GPU=1 .venv/bin/python out/shorts/survol-pixel__histoire__machu-picchu-pourquoi-une-cite-en-escaliers/src/video.py --stills 0.5 --dir /tmp/x
```

- Dépendance : `taichi==1.7.2` dans le `.venv` (dernière version avec une roue macOS x86_64 ; la campagne utilisait 1.7.4
  sous Linux), backend **Metal**. Sans `SURVOL_GPU=1`, sans taichi ou sans Metal, le rendu reste sur le **CPU** (défaut et
  secours ; un échec GPU en cours de rendu rebascule sur le CPU).
- Seule la marche des rayons (`Renderer._march`) passe sur le GPU ; le sol, la brume, les arbres, les nuages et les textes
  restent en numpy. Gain mesuré : marche 0,2–0,5 s → ~0,1 s ; image 1,5–1,9 s → 0,7–0,8 s.
- Carte utilisée : celle que Metal choisit par défaut, sur ce Mac l'**AMD Radeon Pro 560** (l'Intel HD 630 est la carte
  basse consommation).
- **Parité non garantie au bit près** : sur 6 images de l'atoll, 0 pixel d'écart sur l'indice de palette, mais 0 à 0,2 % des
  rayons diffèrent de 1–2 ulp sur la distance d'impact. La division Metal n'est pas arrondie au plus proche (29 % des
  quotients diffèrent de numpy) ; `div_rn` la corrige (exacte seule sur 16 millions de cas), les quotients B/dxy viennent de
  numpy, mais un écart d'1 ulp subsiste sur `(pz − bm) / ndz` dans le noyau compilé. Les commentaires du code qui annoncent
  un résultat « au bit près » sont donc optimistes. Règle du propriétaire : GPU seulement si la parité est à 0 pixel ;
  le bit près n'étant pas garanti (un ulp peut faire basculer un pixel sur d'autres images), **les rendus livrés sont sur
  CPU**. Toute modification de `Renderer._march` doit être reportée dans
  `survol_gpu.py`, puis la parité re-mesurée.
