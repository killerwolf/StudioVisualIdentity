# Reproduire (depuis la racine du dépôt)

**Essai C2 de la composition** (`out/report/notes/composition/matrice.md`) : habillage `grille-suisse` (la pâte de Grille
Suisse) × mécanique `trace-chemin` × format `narre-court`. Premier habillage porté sur une deuxième mécanique. Texte et voix
de `swiss-data__geographie__ou-vivent-8-milliards` (Fish Audio Arnold, ses `voice_lines/` lues sur place, aucun nouvel appel).
Fichiers neufs : `out/shared/chemin-moteur/habillages/grille-suisse.js` (habillage) et `dessins/barres-humains.json` (dessin :
barres à la même échelle, filets de section). `chemin.js` n'est pas modifié. Verdict : `out/report/notes/composition/essais.md`.

```bash
D=out/shorts/chemin-grille-suisse__geographie__ou-vivent-8-milliards
python3 $D/src/voix.py /tmp/c2-voix.wav                       # numpy ; placement identique à tts.py --engine files
node out/tools/chemin_audit.mjs $D/src/scene.html             # doit dire « aucune »
node out/tools/render.mjs $D/src/scene.html --duration 15 --out /tmp/c2-video.mp4
ffmpeg -y -i /tmp/c2-video.mp4 -i /tmp/c2-voix.wav -map 0:v -map 1:a -af "apad,loudnorm=I=-16:TP=-1.5" \
  -vf "scale=in_range=pc:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -t 15 -movflags +faststart $D/short.mp4
node out/tools/render.mjs $D/src/scene.html --stills 0.8,4.6,6.6,9.9,14.5 --stills-dir $D/stills
python3 out/tools/check.py $D
```

Temps des mots (`narration-chemin.json`) : débuts et fins de segments par `ffmpeg silencedetect` (−35 dB, 0,08 s) sur la piste
reconstruite, découpage en mots par faster-whisper `small` (fr).
