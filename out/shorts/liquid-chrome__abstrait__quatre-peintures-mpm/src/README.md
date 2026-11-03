# Reproduire « Quatre peintures tombent et se mélangent » (Chrome Liquide · abstrait)

Taichi MLS-MPM (ti.cpu, 1 thread) + ombrage OpenCV -> vidéo muette ; overlays texte PIL (Syne/Inter @fontsource) ; son sound.py ; mux assemble.py. Graine 11.

```bash
out/tools/slot.sh .venv/bin/python out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/mpm_paint.py --out /tmp/svi/liquid-a/video.mp4 --duration 14 && .venv/bin/python out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/overlays.py /tmp/svi/liquid-a/ov && .venv/bin/python out/tools/sound.py out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/sound.json /tmp/svi/liquid-a/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/liquid-a/video.mp4 --music /tmp/svi/liquid-a/music.wav --overlay /tmp/svi/liquid-a/ov/o1.png:0:4.3:0.45 --overlay /tmp/svi/liquid-a/ov/o2.png:6.6:10.9:0.45 --overlay /tmp/svi/liquid-a/ov/o3.png:11.3:14:0.45 --out out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/short.mp4
```

Fichiers : `mpm_paint.py` (simulation + rendu, `--until/--stills` pour les aperçus), `overlays.py` (cartons texte), `sound.json` (musique pad + SFX calés sur les impacts).
