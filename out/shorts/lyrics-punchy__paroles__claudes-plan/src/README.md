# Reproduire (depuis la racine du dépôt)

Prérequis : `npm i` (dont `@fontsource-variable/anybody` 5.3.0), ffmpeg, un Chromium : Playwright, ou `npm i --no-save playwright-core`
plus un Chrome installé donné par `SVI_CHROME` (cas de ce Mac : `SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`,
node dans `~/.nvm/versions/node/v22.23.3/bin`). Aucun paquet Python : `lyrics_align.py` n'utilise que la bibliothèque standard.

```bash
D=out/shorts/lyrics-punchy__paroles__claudes-plan
# 1. paroles + horaires -> lyrics.json (ici le REMPLISSAGE ; horaires écrits à la main, source « main »)
python3 out/tools/lyrics_align.py --paroles $D/src/paroles.remplissage.txt --mots $D/src/mots.remplissage.json \
  --out $D/src/lyrics.remplissage.json --bpm 154.5 --t0 0 --duree 19.5 --titre "LYRICS PUNCHY" \
  --titre-morceau "FILLER (our own words, not the song's lyrics)" --langue en --source main
# 2. contrôle image par image (zones sûres, tailles, carton sur le mur)
node out/tools/lyrics_audit.mjs $D/src/scene.html
# 3. rendu muet, puis piste silencieuse et yuv420p (render.mjs sort du yuvj420p que check.py refuse)
node out/tools/render.mjs $D/src/scene.html --out $D/tmp/video.mp4
ffmpeg -y -i $D/tmp/video.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 64k -shortest -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.4,5.4,11.3,14.2,19.3 --stills-dir $D/stills
python3 out/tools/check.py $D
```

## Avec les vraies paroles (hors dépôt)

Les paroles réelles et l'audio vivent dans `~/git/StudioVisualIdentity-sources/lyrics-claudes-plan/` et n'entrent jamais dans le dépôt.
Le serveur de `render.mjs` ne sert que le dépôt : on passe par un lien symbolique dans `tmp/` (ignoré par git).

```bash
S=~/git/StudioVisualIdentity-sources/lyrics-claudes-plan
python3 out/tools/lyrics_align.py --paroles $S/paroles-brouillon.txt --mots $S/transcription-mots.json --out $S/lyrics.json \
  --bpm 154.5 --duree 19.5 --titre "CLAUDE'S PLAN" --artiste "Jeff Guo" --langue en
mkdir -p $D/tmp && ln -sf $S/lyrics.json $D/tmp/lyrics.json
node out/tools/render.mjs $D/src/scene.html --query data=../tmp/lyrics.json --out $S/video-paroles-muette.mp4
ffmpeg -y -i $S/video-paroles-muette.mp4 -i $S/claudes-plan.wav -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k -t 19.5 $S/apercu_avec_son.mp4
```

## Fichiers

- `scene.html` : la scène (`window.renderAt(t)`), lit `?data=` (par défaut `lyrics.remplissage.json`), `?debug` affiche les zones sûres.
- Moteur partagé de l'identité : `out/shared/lyrics-moteur/` (`lyrics.js` lecteur et mise en page, `dessins.js` pictogrammes SVG,
  `triggers.json` bibliothèque de déclencheurs). Un nouvel épisode = un nouveau `lyrics.json`, sans code.
- `paroles.remplissage.txt`, `mots.remplissage.json`, `lyrics.remplissage.json` : jeu de REMPLISSAGE (nos mots, en anglais : les paroles s'affichent toujours dans la langue du morceau).
- Outils : `out/tools/lyrics_align.py` (étapes 3–7 de la chaîne + validation), `out/tools/lyrics_audit.mjs` (contrôle image par image).
