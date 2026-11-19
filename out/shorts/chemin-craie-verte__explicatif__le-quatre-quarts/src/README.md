# Reproduire (depuis la racine du dépôt)

**Essai C1 de la composition** (`out/report/notes/composition/matrice.md`) : habillage `craie-verte` (la pâte de Tableau Craie)
× mécanique `trace-chemin` × format `narre-long`. Même dessin (`quatre-quarts`), mêmes temps et même voix que
`lyrics-chemin__explicatif__le-quatre-quarts` (habillage `ardoise`) ; seuls changent l'habillage
(`out/shared/chemin-moteur/habillages/craie-verte.js`, fichier neuf) et la casse du texte écrit au sol (minuscules, écriture
Caveat comme Tableau Craie). Question posée : `craie-verte` et `ardoise` sont-ils un doublon ? Verdict :
`out/report/notes/composition/essais.md`.

La voix n'est pas dans le dépôt (comme pour le short d'origine) : `~/git/StudioVisualIdentity-sources/lyrics-chemin-narres/a2-quatre-quarts.elevenlabs.mp3`
(ElevenLabs, « Gipsy Paladini », générée le 19/11 pour le quatre-quarts ; aucun nouvel appel).

```bash
D=out/shorts/chemin-craie-verte__explicatif__le-quatre-quarts
V=~/git/StudioVisualIdentity-sources/lyrics-chemin-narres
node out/tools/chemin_audit.mjs $D/src/scene.html            # doit dire « aucune »
node out/tools/render.mjs $D/src/scene.html --duration 25.6 --out /tmp/c1-video.mp4
ffmpeg -y -i /tmp/c1-video.mp4 -i $V/a2-quatre-quarts.elevenlabs.mp3 -map 0:v -map 1:a -af "apad,loudnorm=I=-16:TP=-1.5" \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -t 25.6 -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.2,4.6,11.0,13.6,24.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

`render.mjs` avec Chrome installé : `SVI_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.

## Fichiers

- `scene.html` : la scène ; lit `narration-chemin.json`.
- `narration-chemin.json` : copie de celle du quatre-quarts (mêmes temps), `habillage: craie-verte`, texte en minuscules.
