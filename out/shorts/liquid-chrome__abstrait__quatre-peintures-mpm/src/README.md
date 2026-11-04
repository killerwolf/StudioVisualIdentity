# Reproduire « Quatre peintures tombent et se mélangent » (Chrome Liquide · abstrait)

Taichi MLS-MPM (ti.cpu, 1 thread) + ombrage OpenCV -> vidéo muette ; overlays texte PIL (Syne/Inter @fontsource) ; son sound.py ; mux assemble.py. Graine 11.

```bash
out/tools/slot.sh .venv/bin/python out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/mpm_paint.py --out /tmp/svi/liquid-a/video.mp4 --duration 14 && .venv/bin/python out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/overlays.py /tmp/svi/liquid-a/ov && .venv/bin/python out/tools/sound.py out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/src/sound.json /tmp/svi/liquid-a/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/liquid-a/video.mp4 --music /tmp/svi/liquid-a/music.wav --overlay /tmp/svi/liquid-a/ov/o1.png:0:4.3:0.45 --overlay /tmp/svi/liquid-a/ov/o2.png:6.6:10.9:0.45 --overlay /tmp/svi/liquid-a/ov/o3.png:11.3:14:0.45 --out out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm/short.mp4
```

Fichiers : `mpm_paint.py` (simulation + rendu, `--until/--stills` pour les aperçus), `overlays.py` (cartons texte), `sound.json` (musique pad + SFX calés sur les impacts).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/liquid-chrome__abstrait__quatre-peintures-mpm --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
