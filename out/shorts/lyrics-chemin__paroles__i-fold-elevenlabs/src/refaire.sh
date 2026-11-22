#!/bin/bash
# refaire.sh — une version chantée de « Monday's Draft » (identité lyrics-chemin, dessin du bateau, habillage plan-bleu)
# calée sur un nouvel enregistrement du même texte. Sert aux deux shorts « I Fold » (elevenlabs, lyria).
#
#   bash refaire.sh <nom> <morceau.mp3> --bpm 150 [--cut-in 0] [--cut-out <fin>] [--preroll 0] [--zoom-beats 8] [--tail 1.0]
#                   [--fade-in 0.15] [--fade-out 0.4] [--fix mot#n=t ...] [--etape transcrire|caler|rendre|tout]
#
# <nom> : elevenlabs ou lyria (dossier out/shorts/lyrics-chemin__paroles__i-fold-<nom>/). Le mp3 du morceau reste hors dépôt.
# Étapes (relancer avec --etape caler après avoir lu src/align.txt et ajouté des --fix) :
#   transcrire : trois passes faster-whisper (small.en avec les paroles en amorce, medium.en avec amorce, small.en sans) sur
#                l'extrait ; mots horodatés dans src/mots_*.json (temps de l'extrait = temps du mp3 moins cut-in)
#   caler      : outils/gen_chemin.py -> src/chemin.json (+ align.txt : temps de chaque mot par passe, écart), puis chemin_audit
#   rendre     : rendu muet (render.mjs), audio (extrait, fondus, pré-roulé, -14 LUFS / -1.5 dBTP), mux, planche de 6 images
# Sorties : tmp/i-fold_<nom>.mp4 (maître crf 18) et tmp/planche.jpg dans le dossier du short (tmp/ est ignoré par git).
# Prérequis : node + `npm i` (render.mjs, Chromium ou SVI_CHROME), ffmpeg, uv (faster-whisper, étape transcrire seulement).
set -euo pipefail
OUTILS="$(cd "$(dirname "$0")" && pwd)/outils"
REPO="$(cd "$(dirname "$0")/../../../.." && pwd)"
NOM=$1; MP3=$(cd "$(dirname "$2")" && pwd)/$(basename "$2"); shift 2
BPM=""; CI=0; CO=""; PRE=0; ZB=8; TAIL=1.0; FI=0.15; FO=0.4; FIX=(); ETAPE=tout
while [ $# -gt 0 ]; do case $1 in
  --bpm) BPM=$2;; --cut-in) CI=$2;; --cut-out) CO=$2;; --preroll) PRE=$2;; --zoom-beats) ZB=$2;; --tail) TAIL=$2;;
  --fade-in) FI=$2;; --fade-out) FO=$2;; --fix) FIX+=(--fix "$2");; --etape) ETAPE=$2;; *) echo "option inconnue $1"; exit 2;; esac; shift 2; done
[ -n "$BPM" ] || { echo "--bpm obligatoire (un temps = 60/bpm s ; règle les durées de transition)"; exit 2; }
[ -n "$CO" ] || CO=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP3")
S=out/shorts/lyrics-chemin__paroles__i-fold-$NOM        # le short (relatif au dépôt)
W="$REPO/$S/src"; SORTIE="$REPO/$S/tmp"; mkdir -p "$W" "$SORTIE"; TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
SHIFT=$(python3 -c "print($PRE)")          # les mots sont horodatés sur l'extrait (qui commence à cut-in)
D=out/shorts/lyrics-chemin__paroles__claudes-plan        # scène partagée (lit ?data=, chemin relatif à la scène)
Q="data=../../lyrics-chemin__paroles__i-fold-$NOM/src/chemin.json"

if [ $ETAPE = transcrire ] || [ $ETAPE = tout ]; then
  ffmpeg -v error -y -i "$MP3" -ss "$CI" -to "$CO" -ar 16000 -ac 1 "$TMP/in16.wav"
  FW="uv run --python 3.11 --with faster-whisper python -I $OUTILS/fw.py"
  $FW "$TMP/in16.wav" "$W/mots_small.json" small.en
  $FW "$TMP/in16.wav" "$W/mots_medium.json" medium.en
  $FW "$TMP/in16.wav" "$W/mots_sans_amorce.json" small.en sans
fi
if [ $ETAPE = caler ] || [ $ETAPE = tout ]; then
  EXTRA=$(python3 -c "print($CO-$CI)")
  python3 "$OUTILS/gen_chemin.py" --base "$REPO/$D/src/paroles.remplissage.json" \
    --runs "$W/mots_small.json" "$W/mots_medium.json" "$W/mots_sans_amorce.json" --out "$W/chemin.json" --bpm "$BPM" --shift "$SHIFT" \
    --zoom-beats "$ZB" --tail "$TAIL" --end "$EXTRA" --note "i-fold $NOM : $(basename "$MP3") [$CI, $CO] s, pré-roulé $PRE s" --report "$W/align.txt" ${FIX[@]+"${FIX[@]}"} | tail -1
  (cd "$REPO" && node out/tools/chemin_audit.mjs $D/src/scene.html --query "$Q" --json "$SORTIE/audit.json" | sed -n '/--- transitions/,$p') || true
fi
if [ $ETAPE = rendre ] || [ $ETAPE = tout ]; then
  DUR=$(python3 -c "import json;print(json.load(open('$W/chemin.json'))['duree'])")
  (cd "$REPO" && node out/tools/render.mjs $D/src/scene.html --query "$Q" --duration "$DUR" --out "$TMP/video.mp4" --no-slot)
  bash "$OUTILS/audio.sh" "$MP3" "$TMP/song.wav" "$CI" "$CO" "$PRE" "$DUR" "$FI" "$FO"
  OUT="$SORTIE/i-fold_$NOM.mp4"
  ffmpeg -v error -y -i "$TMP/video.mp4" -i "$TMP/song.wav" -map 0:v -map 1:a -vf "scale=in_range=pc:out_range=tv,format=yuv420p" \
    -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -ar 48000 -t "$DUR" -movflags +faststart "$OUT"
  ffmpeg -hide_banner -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I:|Peak:)' | tail -2
  python3 "$OUTILS/planche.py" "$OUT" "$W/chemin.json" "$SORTIE/planche.jpg"
fi
