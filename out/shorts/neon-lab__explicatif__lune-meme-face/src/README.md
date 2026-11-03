# Reproduire (depuis la racine du dépôt)

```
node out/tools/render.mjs out/shorts/neon-lab__explicatif__lune-meme-face/src/index.html --out /tmp/svi/neon-lab-exp/raw.mp4 --duration 16 && .venv/bin/python out/shorts/neon-lab__explicatif__lune-meme-face/src/neon_grade.py /tmp/svi/neon-lab-exp/raw.mp4 /tmp/svi/neon-lab-exp/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/neon-lab__explicatif__lune-meme-face/src/sound.json /tmp/svi/neon-lab-exp/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/neon-lab-exp/video.mp4 --music /tmp/svi/neon-lab-exp/music.wav --out out/shorts/neon-lab__explicatif__lune-meme-face/short.mp4
```

Fichiers : `index.html` (scène three.js + UnrealBloom, texte DOM/SVG), `field.glsl.js` (champ de force GLSL partagé avec le short abstrait, ici en ShaderMaterial), `neon_grade.py` (post OpenCV identique à l'abstrait), `sound.json`. Graine 7 (étoiles).
