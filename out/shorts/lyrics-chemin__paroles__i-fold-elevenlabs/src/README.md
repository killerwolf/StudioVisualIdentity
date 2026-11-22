# Reproduire (depuis la racine du dépôt)

Version chantée de « Monday's Draft » sur un morceau généré par **ElevenLabs Music**. Même scène, même dessin (bateau) et même
habillage (plan-bleu) que `lyrics-chemin__paroles__claudes-plan` ; seuls les temps changent. Le mp3 du morceau reste hors dépôt
(il suit les conditions d'ElevenLabs) : sans lui, on peut refaire le calage et le rendu muet, pas le son.

Prérequis : ceux de `out/shorts/lyrics-chemin__paroles__claudes-plan/src/README.md` (node, `npm i`, ffmpeg, Chromium ou `SVI_CHROME`),
plus `uv` pour faster-whisper (étape `transcrire` seulement).

```bash
D=out/shorts/lyrics-chemin__paroles__claudes-plan          # la scène partagée
Q=data=../../lyrics-chemin__paroles__i-fold-elevenlabs/src/chemin.json
# 1. contrôle sans rendu (3 cadrages tenus moins de 0,5 s : voir short.json, qualityChecks.audit)
node out/tools/chemin_audit.mjs $D/src/scene.html --query $Q
# 2. tout refaire avec le morceau (transcription, calage, rendu, son, mux, planche) ; sortie dans ../tmp/
bash out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/src/refaire.sh elevenlabs <elevenlabs.mp3> --bpm 152 \
  --cut-in 5.87 --cut-out 34.70 --zoom-beats 8 --fix and#0=16.05 --fix of#0=21.57 --fix wrong#1=21.71 --fix folds#0=22.08
# 3. version du dépôt (maître crf 18 -> ~14 Mo), puis contrôle
ffmpeg -i out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/tmp/i-fold_elevenlabs.mp4 -c:v libx264 -preset slow -crf 26 \
  -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/short.mp4
python3 out/tools/check.py out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs
```

L'étape `caler` seule (`--etape caler`) n'a pas besoin du mp3 si on donne `--cut-out` : il suffit d'un chemin dans un dossier qui existe,
le fichier peut manquer (son nom n'entre que dans `note`, nommez-le `elevenlabs.mp3`). Elle relit `src/mots_*.json` et redonne
`src/chemin.json` et `src/align.txt` à l'identique (vérifié le 22/11/2026, avec `refaire.sh` sur la version Lyria).

## Fichiers

- `chemin.json` : le fichier lu par la scène (`?data=`) : lignes → arêtes du bateau, unités `[texte, début, fin]`, cadrages,
  transitions, respiration, zoom arrière. Temps recalculés sur ce morceau.
- `align.txt` : pour chaque mot chanté, son temps dans les trois passes de transcription, l'écart et le temps retenu (médiane ou `--fix`).
- `mots_small.json`, `mots_medium.json`, `mots_sans_amorce.json` : mots horodatés par faster-whisper (temps de l'extrait).
- `audit.json` : sortie de `chemin_audit.mjs` sur `chemin.json`.
- `refaire.sh` : la chaîne complète (sert aussi à la version Lyria) ; `outils/` :
  `fw.py` (une passe faster-whisper), `gen_chemin.py` (mots horodatés -> `chemin.json`, à partir du remplissage de claudes-plan),
  `audio.sh` (extrait, fondus, pré-roulé, −14 LUFS / −1,5 dBTP), `planche.py` (planche de 6 images).
