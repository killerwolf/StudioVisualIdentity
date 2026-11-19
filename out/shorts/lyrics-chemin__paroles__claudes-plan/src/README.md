# Reproduire (depuis la racine du dépôt)

Prérequis : `npm i` (dont `@fontsource/barlow-condensed` 5.3.0 et `@fontsource/jetbrains-mono`), ffmpeg, un Chromium : Playwright, ou
`npm i --no-save playwright-core` plus un Chrome installé donné par `SVI_CHROME` (cas de ce Mac :
`SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`, node dans `~/.nvm/versions/node/v22.23.3/bin`).
Aucun paquet Python.

```bash
D=out/shorts/lyrics-chemin__paroles__claudes-plan
# 1. contrôle sans rendu : zones sûres, corps, cadrages, départs après 60 %, vitesse au repos, chevauchements (doit dire « aucune »)
node out/tools/chemin_audit.mjs $D/src/scene.html
# 2. rendu muet, puis piste silencieuse et yuv420p (render.mjs sort du yuvj420p que check.py refuse)
node out/tools/render.mjs $D/src/scene.html --duration 32.62 --out $D/tmp/video.mp4
ffmpeg -y -i $D/tmp/video.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 64k -shortest -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.2,4.6,6.4,7.7,24.9,30.3,32.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

`?guides=1` à la fin de l'adresse de la scène : zones sûres en surimpression.

## Avec les vraies paroles (hors dépôt)

Les paroles réelles et l'audio vivent dans `~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/` et n'entrent jamais dans le dépôt.
`chemin.paroles.json` y reprend exactement les temps et cadrages du remplissage, avec les mots réels. Le serveur de `render.mjs` ne
sert que le dépôt : on passe par un lien symbolique dans `tmp/` (ignoré par git).

```bash
S=~/git/StudioVisualIdentity-sources/lyrics-claudes-plan
mkdir -p $D/tmp && ln -sf $S/chemin.paroles.json $D/tmp/paroles.reelles.json
node out/tools/chemin_audit.mjs $D/src/scene.html --query data=../tmp/paroles.reelles.json
node out/tools/render.mjs $D/src/scene.html --query data=../tmp/paroles.reelles.json --duration 32.62 --out $D/tmp/reel.mp4
ffmpeg -y -i $D/tmp/reel.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a aac -b:a 64k -shortest $S/chemin-paroles-muette.mp4
ffmpeg -y -i $D/tmp/reel.mp4 -i $S/claudes-plan.wav -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k -t 32.62 $S/apercu_chemin_avec_son.mp4
```

## Fichiers

- `scene.html` : la scène ; lit `?data=` (par défaut `paroles.remplissage.json`).
- `paroles.remplissage.json` : jeu de REMPLISSAGE (« Monday's draft », nos mots, en anglais comme le morceau), calé sur les temps réels
  du morceau test : lignes → arêtes du dessin, unités `[texte, début, fin]`, cadrages, transitions (en temps), annotations, respiration,
  zoom arrière, refrain.
- Moteur partagé : `out/shared/chemin-moteur/chemin.js` ; dessin : `out/shared/chemin-moteur/dessins/bateau.json`.
- Maquette d'origine (direction artistique de Fable) : `out/report/notes/lyrics-chemin/proto/scene.html`.
