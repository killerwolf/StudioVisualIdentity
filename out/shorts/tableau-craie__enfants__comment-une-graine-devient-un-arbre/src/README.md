# Reproduire « Comment une graine devient un arbre ? » (Tableau Craie, Rough.js + GSAP)

Depuis la racine du dépôt :

```
node out/tools/render.mjs out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre/src/index.html --out /tmp/svi/tableau-craie__enfants__comment-une-graine-devient-un-arbre/video.mp4 --duration 15.5 && .venv/bin/python out/tools/sound.py out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre/src/sound.json /tmp/svi/tableau-craie__enfants__comment-une-graine-devient-un-arbre/music.wav && .venv/bin/python out/tools/assemble.py mux --video /tmp/svi/tableau-craie__enfants__comment-une-graine-devient-un-arbre/video.mp4 --music /tmp/svi/tableau-craie__enfants__comment-une-graine-devient-un-arbre/music.wav --out out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre/short.mp4
```

- `index.html` : ardoise canvas + SVG Rough.js (graines fixes) ; GSAP `timeline({paused:true})`, `renderAt = t => tl.seek(t,false)` ; écriture des tracés par `stroke-dashoffset` ; grain de craie = `feImage` (rng 77) en masque `feComposite in`.
- `sound.json` : music-box F majpent 92 bpm + SFX calés sur la timeline (même palette que le short explicatif).

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/tableau-craie__enfants__comment-une-graine-devient-un-arbre --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
