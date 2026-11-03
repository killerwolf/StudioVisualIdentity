# 1789 en 20 secondes — gazette-1900 / histoire

Reproduire (depuis la racine du dépôt) :

    bash out/shorts/gazette-1900__histoire__1789-en-20-secondes/src/build.sh   # = node out/tools/render.mjs out/shorts/gazette-1900__histoire__1789-en-20-secondes/src/index.html --out /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/raw.mp4 --duration 18.75 && out/tools/slot.sh .venv/bin/python out/shorts/gazette-1900__histoire__1789-en-20-secondes/src/post.py video /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/raw.mp4 /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/video.mp4 --seed 1900 --flash 1.875,4.6875,7.5,10.3125,13.125,15.9375 && .venv/bin/python out/tools/sound.py out/shorts/gazette-1900__histoire__1789-en-20-secondes/src/sound.json /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/video.mp4 --music /tmp/svi/gazette-1900__histoire__1789-en-20-secondes/music.wav --out out/shorts/gazette-1900__histoire__1789-en-20-secondes/short.mp4

Fichiers : `index.html` (scène GSAP, graine 1789), `gazette.js` (système partagé de l'identité), `post.py` (post-traitement OpenCV par frame), `gen_sound.py` -> `sound.json` (musique « pulse » 128 bpm + SFX calés), `build.sh`, `DURATION`, `FLASH` (instants des coupes).
