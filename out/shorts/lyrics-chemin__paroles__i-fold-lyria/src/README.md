# Reproduire (depuis la racine du dépôt)

Version chantée de « Monday's Draft » sur un morceau généré par **Google Lyria 3.5** (appelé par treg). Même scène, même dessin
(bateau) et même habillage (plan-bleu) que `lyrics-chemin__paroles__claudes-plan` ; seuls les temps changent. Le mp3 du morceau
reste hors dépôt (il suit les conditions de Google) : sans lui, on peut refaire le calage et le rendu muet, pas le son.

Les outils sont dans le `src/` de la version ElevenLabs : `out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/src/`
(`refaire.sh`, `outils/`, et le README qui les décrit).

```bash
D=out/shorts/lyrics-chemin__paroles__claudes-plan          # la scène partagée
Q=data=../../lyrics-chemin__paroles__i-fold-lyria/src/chemin.json
# 1. contrôle sans rendu (8 cadrages tenus moins de 0,5 s : voir short.json, qualityChecks.audit)
node out/tools/chemin_audit.mjs $D/src/scene.html --query $Q
# 2. tout refaire avec le morceau ; sortie dans ../tmp/
bash out/shorts/lyrics-chemin__paroles__i-fold-elevenlabs/src/refaire.sh lyria <lyria.mp3> --bpm 155 \
  --cut-in 0 --cut-out 18.52 --preroll 1.55 --zoom-beats 4 --tail 1.2 --fix i#0=0.17
# 3. version du dépôt (maître crf 18 -> ~11 Mo), puis contrôle
ffmpeg -i out/shorts/lyrics-chemin__paroles__i-fold-lyria/tmp/i-fold_lyria.mp4 -c:v libx264 -preset slow -crf 26 \
  -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart out/shorts/lyrics-chemin__paroles__i-fold-lyria/short.mp4
python3 out/tools/check.py out/shorts/lyrics-chemin__paroles__i-fold-lyria
```

`--etape caler` redonne `src/chemin.json` et `src/align.txt` à l'identique sans le mp3 (vérifié le 22/11/2026).

## Fichiers

`chemin.json` (lu par la scène), `align.txt`, `mots_*.json` (faster-whisper), `audit.json` : même rôle que dans la version ElevenLabs.
