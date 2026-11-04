# Reproduire « Le pendule de Newton chromé qui ne s'arrête jamais » (Chrome Liquide · abstrait)

Babylon.js 9.33 (UMD), scène sans état, boucle parfaite de 12 s (T = 2,4 s × 5). Texte HTML (Syne 800 / Inter 500). Graine 3.

```bash
node out/tools/render.mjs out/shorts/liquid-chrome__abstrait__pendule-de-newton-chrome/src/index.html --out /tmp/svi/liquid-c/video.mp4 --duration 12 && .venv/bin/python out/tools/sound.py out/shorts/liquid-chrome__abstrait__pendule-de-newton-chrome/src/sound.json /tmp/svi/liquid-c/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/liquid-c/video.mp4 --music /tmp/svi/liquid-c/music.wav --out out/shorts/liquid-chrome__abstrait__pendule-de-newton-chrome/short.mp4
```

Fichiers : `index.html` (scène, environnement procédural par ReflectionProbe, GlowLayer, DefaultRenderingPipeline), `sound.json` (pad + clic/verre à chaque choc, t = k·1,2 s).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/liquid-chrome__abstrait__pendule-de-newton-chrome --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
