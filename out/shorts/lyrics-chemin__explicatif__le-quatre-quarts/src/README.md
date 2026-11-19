# Reproduire (depuis la racine du dépôt)

Déclinaison A2 de lyrics-chemin : « Le quatre-quarts », short narré. Habillage `ardoise`, dessin `quatre-quarts`.
Direction artistique : `out/report/notes/lyrics-chemin/declinaisons/a2-quatre-quarts.md`.

La voix n'est pas dans le dépôt : `~/git/StudioVisualIdentity-sources/lyrics-chemin-narres/a2-quatre-quarts.elevenlabs.mp3`
(ElevenLabs, voix « Gipsy Paladini », `eleven_multilingual_v2`, une génération, texte dans `a2.txt` au même endroit).

```bash
D=out/shorts/lyrics-chemin__explicatif__le-quatre-quarts
V=~/git/StudioVisualIdentity-sources/lyrics-chemin-narres
# 1. mots horodatés (faster-whisper small, fr) -> a2-mots.json ; les temps de src/narration-chemin.json en sont tirés à la main
uv run -q -p 3.12 --with faster-whisper python $V/mots.py $V/a2-quatre-quarts.elevenlabs.mp3 $V/a2-mots.json $V/a2.txt
# 2. contrôle sans rendu (doit dire « aucune »)
node out/tools/chemin_audit.mjs $D/src/scene.html
# 3. rendu, puis voix posée (le short narré porte son audio), yuv420p
node out/tools/render.mjs $D/src/scene.html --duration 25.6 --out $D/tmp/video.mp4
ffmpeg -y -i $D/tmp/video.mp4 -i $V/a2-quatre-quarts.elevenlabs.mp3 -map 0:v -map 1:a -af "apad,loudnorm=I=-16:TP=-1.5" \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -t 25.6 -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.2,4.6,11.0,13.6,24.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

`mots.py` (hors dépôt, à côté de la voix) : quelques lignes (faster-whisper `small`, `word_timestamps=True`, audio décodé par ffmpeg en 16 kHz) — voir
`out/report/notes/lyrics-chemin/declinaisons/realisation.md`.

## Fichiers

- `scene.html` : la scène ; lit `?data=` (par défaut `narration-chemin.json`).
- `narration-chemin.json` : lignes → arêtes du dessin, unités `[texte écrit au sol, début, fin]` aux temps mesurés de la voix,
  transitions en secondes (`duree`), pas de `bpm` (`temps` : 0,5 s, avance du pré-posé), moule (`moule` : début et fin du tracé),
  zoom arrière, rangs finaux.
- Moteur : `out/shared/chemin-moteur/chemin.js` ; habillage `habillages/ardoise.js` ; dessin `dessins/quatre-quarts.json`.
