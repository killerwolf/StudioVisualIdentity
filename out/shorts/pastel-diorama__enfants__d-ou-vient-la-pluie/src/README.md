# Reproduire

```
node out/tools/render.mjs out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie/src/index.html --out /tmp/svi/pastel-diorama__enfants__d-ou-vient-la-pluie/video.mp4 --duration 16 && .venv/bin/python out/tools/sound.py out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie/src/sound.json /tmp/svi/pastel-diorama__enfants__d-ou-vient-la-pluie/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/pastel-diorama__enfants__d-ou-vient-la-pluie/video.mp4 --music /tmp/svi/pastel-diorama__enfants__d-ou-vient-la-pluie/music.wav --out out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie/short.mp4
```

Scène : `index.html` (Zdog + GSAP, graine 4, 16 s). Son : `sound.json` (music-box F majpent 96 bpm + SFX calés sur les beats).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/pastel-diorama__enfants__d-ou-vient-la-pluie --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
