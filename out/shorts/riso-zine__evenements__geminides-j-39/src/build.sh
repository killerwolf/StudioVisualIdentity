#!/usr/bin/env bash
# build.sh — reproduit short.mp4 depuis la racine du dépôt (rendu p5+GSAP -> passe OpenCV -> son -> mux)
set -e
S=out/shorts/riso-zine__evenements__geminides-j-39; T=/tmp/svi/riso-gem; mkdir -p $T
node out/tools/render.mjs $S/src/index.html --out $T/raw.mp4 --duration 16
out/tools/slot.sh .venv/bin/python $S/src/post.py video $T/raw.mp4 $T/video.mp4 --seed 39
.venv/bin/python out/tools/sound.py $S/src/sound.json $T/music.wav
.venv/bin/python out/tools/assemble.py mux --video $T/video.mp4 --music $T/music.wav --out $S/short.mp4
