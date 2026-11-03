# Reproduire (depuis la racine du dépôt)

```
out/tools/slot.sh .venv/bin/python out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/src/render.py --out /tmp/svi/neon-lab-pend/raw.mp4 && out/tools/slot.sh .venv/bin/python out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/src/neon_grade.py /tmp/svi/neon-lab-pend/raw.mp4 /tmp/svi/neon-lab-pend/video.mp4 && .venv/bin/python out/tools/sound.py out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/src/sound.json /tmp/svi/neon-lab-pend/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/neon-lab-pend/video.mp4 --music /tmp/svi/neon-lab-pend/music.wav --out out/shorts/neon-lab__explicatif__effet-papillon-double-pendule/short.mp4
```

Fichiers : `render.py` (Matplotlib Agg : une figure réutilisée, artistes mis à jour, pipe ffmpeg ; champ de force = portage numpy de `field.glsl.js`), `pendulum.py` (équations du double pendule, RK4 pas fixe 1/1800 s, m = 1 kg, L = 1 m, g = 9,81 m/s² ; A : θ1 = θ2 = 1,8 rad ; B : θ1 + 0,001 rad ; ω = 0), `neon_grade.py` (post OpenCV identique aux autres shorts Labo Néon), `sound.json`. Graine 3 (bruit du fond uniquement ; la physique est sans aléa). Stills de contrôle : `render.py --stills 0.5,6,9.5,13.5 --dir /tmp/x`.
