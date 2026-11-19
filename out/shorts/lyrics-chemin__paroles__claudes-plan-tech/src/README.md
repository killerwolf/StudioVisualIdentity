# Reproduire (depuis la racine du dépôt)

Déclinaison B de lyrics-chemin : « Claude's Plan », version tech. Habillage `editeur`, dessin `cargo`, mêmes temps que
`lyrics-chemin__paroles__claudes-plan` (154,5 BPM). Direction artistique : `out/report/notes/lyrics-chemin/declinaisons/b-claudes-plan-tech.md`.

Prérequis : comme le short plan bleu (`npm i`, ffmpeg, Chrome par `SVI_CHROME` avec `playwright-core`, node dans `~/.nvm`).

```bash
D=out/shorts/lyrics-chemin__paroles__claudes-plan-tech
# 1. contrôle sans rendu (doit dire « aucune ») ; imprime aussi le corps de chaque ligne dans l'image finale
node out/tools/chemin_audit.mjs $D/src/scene.html
# 2. rendu muet, piste silencieuse, yuv420p
node out/tools/render.mjs $D/src/scene.html --duration 32.62 --out $D/tmp/video.mp4
ffmpeg -y -i $D/tmp/video.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 64k -shortest -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.2,4.3,14.5,24.9,32.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

## Avec les vraies paroles (hors dépôt)

`~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/chemin-tech.paroles.json` : mêmes temps, cadrages et arêtes, mots réels.

```bash
S=~/git/StudioVisualIdentity-sources/lyrics-claudes-plan
ln -sf $S/chemin-tech.paroles.json $D/tmp/paroles.reelles.json
node out/tools/chemin_audit.mjs $D/src/scene.html --query data=../tmp/paroles.reelles.json
node out/tools/render.mjs $D/src/scene.html --query data=../tmp/paroles.reelles.json --duration 32.62 --out $D/tmp/reel.mp4
ffmpeg -y -i $D/tmp/reel.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
  -c:v libx264 -crf 20 -c:a aac -b:a 64k -shortest $S/chemin-tech-paroles-muette.mp4
ffmpeg -y -i $D/tmp/reel.mp4 -i $S/claudes-plan.wav -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
  -c:v libx264 -crf 20 -c:a aac -b:a 192k -t 32.62 $S/apercu_tech_avec_son.mp4
```

## Fichiers

- `scene.html` : la scène ; lit `?data=` (par défaut `paroles.remplissage.json`).
- `paroles.remplissage.json` : jeu de REMPLISSAGE (« Monday's draft »), mêmes temps que le short plan bleu. Chaque ligne de couplet
  est répartie sur les deux rangs d'un conteneur (`c1a`/`c1b`…) ; 4ᵉ valeur d'une unité = classe de coloration (`kw`, `str`, `num`).
- Moteur : `out/shared/chemin-moteur/chemin.js` ; habillage `habillages/editeur.js` ; dessin `dessins/cargo.json`.
