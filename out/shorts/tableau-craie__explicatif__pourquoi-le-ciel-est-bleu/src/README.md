# Reproduire « Pourquoi le ciel est bleu ? » (Tableau Craie, Manim + overlays craie)

Depuis la racine du dépôt (Manim sous `out/tools/slot.sh`) :

```
bash out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/src/build.sh 30
```

(`build.sh 6` = prévisualisation 6 fps dans /tmp.) Étapes de `build.sh` :
1. `chalk_assets.py` → ardoise `board.png`, grain `grain.png` (pixels de l'ardoise, 26 % de trous), textes Caveat/Nunito avec grain (`txt_*.png`) + `overlays.txt` (d'après `timeline.json` et `tokens.json`).
2. `manim render scene.py Sky` (1080×1920, 30 fps, frame 9×16) : formes à la craie (3 passes tremblées), hachures, ondes, barres, Terre/atmosphère, chiffon, zooms lents.
3. `composite.py` : pose grain + textes frame par frame (numpy) → vidéo crf 14.
4. `sound.py sound.json` puis `assemble.py mux` → `short.mp4`.

## Dernière étape : voix off (Fish Audio « Arnold »)

La commande ci-dessus produit la version **sans voix**. Pour obtenir le `short.mp4` livré (avec voix), lancer ensuite :

```bash
.venv/bin/python out/tools/tts.py out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu --engine files --voice "Fish Audio – Arnold (d704cf8f…)" --replace
```

Les fichiers `voice_lines/NN.mp3` (une ligne de `narration.json` chacun) sont déjà dans le dossier ; pour une nouvelle narration, les générer d'abord (voir `out/report/README.md`, section « Voix off Fish Audio »).
