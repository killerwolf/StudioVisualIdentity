# Reproduire — riso-zine · geographie · « Les 5 plus grands déserts du monde (le n°1 est glacé !) »

    bash out/shorts/riso-zine__geographie__5-plus-grands-deserts/src/build.sh
    # = node out/tools/render.mjs out/shorts/riso-zine__geographie__5-plus-grands-deserts/src/index.html --out /tmp/svi/riso-geo/raw.mp4 --duration 16 && out/tools/slot.sh .venv/bin/python out/shorts/riso-zine__geographie__5-plus-grands-deserts/src/post.py video /tmp/svi/riso-geo/raw.mp4 /tmp/svi/riso-geo/video.mp4 --seed 13 && .venv/bin/python out/tools/sound.py out/shorts/riso-zine__geographie__5-plus-grands-deserts/src/sound.json /tmp/svi/riso-geo/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/riso-geo/video.mp4 --music /tmp/svi/riso-geo/music.wav --out out/shorts/riso-zine__geographie__5-plus-grands-deserts/short.mp4

Fichiers : `index.html` (scène : p5.js v2 couches d'encre + GSAP 3.15 timeline seekée, graine 13), `riso.js` (système partagé de l'identité : trame par encre, multiply, repérage décalé à 12 fps, blobs découpés, révélation au marqueur — copie identique dans le short evenements), `post.py` (passe OpenCV : papier qui ondule on twos, manques d'encre, rouleau, grain, fibres), `sound.json` (lofi 90 bpm ré dorien + SFX), `build.sh`.
Formes des déserts : contours bruités dessinés par code (aucune donnée géographique téléchargée), aire ∝ superficie (r = 330·√(S/14)).
