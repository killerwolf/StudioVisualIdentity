# Reproduire (depuis la racine du dépôt)

```
node out/tools/render.mjs out/shorts/neon-lab__abstrait__champ-de-force-lucioles/src/index.html --out /tmp/svi/neon-lab-abs/raw.mp4 --duration 12 && .venv/bin/python out/shorts/neon-lab__abstrait__champ-de-force-lucioles/src/neon_grade.py /tmp/svi/neon-lab-abs/raw.mp4 /tmp/svi/neon-lab-abs/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/neon-lab__abstrait__champ-de-force-lucioles/src/sound.json /tmp/svi/neon-lab-abs/music36.wav && .venv/bin/python out/shorts/neon-lab__abstrait__champ-de-force-lucioles/src/loopslice.py /tmp/svi/neon-lab-abs/music36.wav /tmp/svi/neon-lab-abs/music.wav 12 24 && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/neon-lab-abs/video.mp4 --music /tmp/svi/neon-lab-abs/music.wav --out out/shorts/neon-lab__abstrait__champ-de-force-lucioles/short.mp4
```

Fichiers : `index.html` (scène twgl.js), `field.glsl.js` (champ de force GLSL partagé avec le short explicatif), `neon_grade.py` (post OpenCV : glow + aberration chromatique radiale + vignette), `sound.json` + `loopslice.py` (son en boucle parfaite). Graine 11.
