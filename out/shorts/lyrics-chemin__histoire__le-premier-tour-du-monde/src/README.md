# Reproduire (depuis la racine du dépôt)

Déclinaison A1 de lyrics-chemin : « Le premier tour du monde », short narré. Habillage `portulan`, dessin `tour-du-monde`.
Direction artistique : `out/report/notes/lyrics-chemin/declinaisons/a1-tour-du-monde.md`.

La voix n'est pas dans le dépôt : `~/git/StudioVisualIdentity-sources/lyrics-chemin-narres/a1-tour-du-monde.elevenlabs.mp3`
(ElevenLabs, voix « Justin Doré », `eleven_multilingual_v2`, une génération, texte dans `a1.txt` au même endroit).

```bash
D=out/shorts/lyrics-chemin__histoire__le-premier-tour-du-monde
V=~/git/StudioVisualIdentity-sources/lyrics-chemin-narres
# 1. mots horodatés (faster-whisper small, fr) -> a1-mots.json ; les temps de src/narration-chemin.json en sont tirés à la main
uv run -q -p 3.12 --with faster-whisper python $V/mots.py $V/a1-tour-du-monde.elevenlabs.mp3 $V/a1-mots.json $V/a1.txt
# 2. contrôle sans rendu (doit dire « aucune »)
node out/tools/chemin_audit.mjs $D/src/scene.html
# 3. rendu, puis voix posée (le short narré porte son audio), yuv420p
node out/tools/render.mjs $D/src/scene.html --duration 45 --out $D/tmp/video.mp4
ffmpeg -y -i $D/tmp/video.mp4 -i $V/a1-tour-du-monde.elevenlabs.mp3 -map 0:v -map 1:a -af "apad,loudnorm=I=-16:TP=-1.5" \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -t 45 -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.2,3.8,7.5,21.4,26.6,44.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

`mots.py` (hors dépôt, à côté de la voix) : quelques lignes (faster-whisper `small`, `word_timestamps=True`, audio décodé par ffmpeg en 16 kHz) — voir
`out/report/notes/lyrics-chemin/declinaisons/realisation.md`.

## Fichiers

- `scene.html` : la scène ; lit `?data=` (par défaut `narration-chemin.json`).
- `narration-chemin.json` : lignes → arêtes du dessin, unités `[texte écrit au sol, début, fin]` aux temps mesurés de la voix,
  transitions en secondes (`duree`), pas de `bpm` (`temps` : 0,5 s, avance du pré-posé), reculs muets (`respirations`, en secondes), fin de la route (`routeFin`),
  zoom arrière, rangs finaux.
- Moteur : `out/shared/chemin-moteur/chemin.js` ; habillage `habillages/portulan.js` ; dessin `dessins/tour-du-monde.json`.
