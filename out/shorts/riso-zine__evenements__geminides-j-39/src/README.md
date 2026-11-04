# Reproduire — riso-zine · evenements · « J-39 : les Géminides, la pluie d'étoiles filantes du 13–14 décembre »

    bash out/shorts/riso-zine__evenements__geminides-j-39/src/build.sh
    # = node out/tools/render.mjs out/shorts/riso-zine__evenements__geminides-j-39/src/index.html --out /tmp/svi/riso-gem/raw.mp4 --duration 16 && out/tools/slot.sh .venv/bin/python out/shorts/riso-zine__evenements__geminides-j-39/src/post.py video /tmp/svi/riso-gem/raw.mp4 /tmp/svi/riso-gem/video.mp4 --seed 39 && .venv/bin/python out/tools/sound.py out/shorts/riso-zine__evenements__geminides-j-39/src/sound.json /tmp/svi/riso-gem/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/riso-gem/video.mp4 --music /tmp/svi/riso-gem/music.wav --out out/shorts/riso-zine__evenements__geminides-j-39/short.mp4

Fichiers : `index.html` (scène : p5.js v2 couches d'encre — ciel découpé, étoiles filantes réservées, bâtons de comptage, ville, Phaéton, Terre — + GSAP 3.15 timeline seekée, graine 39), `riso.js` (système partagé de l'identité, identique au short geographie), `post.py` (passe OpenCV, identique au short geographie, graine 39 par défaut), `sound.json` (lofi 90 bpm la penta mineure + SFX ; ticks du compteur calculés depuis l'easing power2.out), `build.sh`.
Compte à rebours : 2026-11-04 -> 2026-12-13 = 26 + 13 = 39 jours.

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/riso-zine__evenements__geminides-j-39 --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
