# Reproduire

```
node out/tools/render.mjs out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard/src/index.html --out /tmp/svi/pastel-diorama__engagement__choisis-ta-boite-renard/video.mp4 --duration 15 && .venv/bin/python out/tools/sound.py out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard/src/sound.json /tmp/svi/pastel-diorama__engagement__choisis-ta-boite-renard/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/pastel-diorama__engagement__choisis-ta-boite-renard/video.mp4 --music /tmp/svi/pastel-diorama__engagement__choisis-ta-boite-renard/music.wav --out out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard/short.mp4
```

Scène : `index.html` (A-Frame 1.8 + GSAP, graine 7, 15 s ; géométrie `roundbox` enregistrée dans la page). Son : `sound.json` (music-box F majpent 96 bpm + SFX : whoosh par échange, blips du compte à rebours, riser, coin+chime à la révélation).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/pastel-diorama__engagement__choisis-ta-boite-renard --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
