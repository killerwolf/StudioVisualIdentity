#!/usr/bin/env bash
# build.sh — reproduit ce short avec le moteur papier partagé (out/shared/papier-moteur) : voix déjà dans ../voice_lines/.
# usage : bash out/shorts/<dossier>/src/build.sh   (Python avec pillow, numpy, opencv-python-headless ; ffmpeg)
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"; DIR="$(dirname "$SRC")"
PY="${PY:-python3}"; [ -x "$SRC/../../../../.venv/bin/python" ] && PY="$SRC/../../../../.venv/bin/python"
cd "$SRC"
"$PY" video.py narration
T0=$(date +%s)
JOBS="${JOBS:-4}" "$PY" video.py
echo "{\"renderTimeSec\": $(( $(date +%s) - T0 ))}" > "$SRC/render.json"
cp short.mp4 "$DIR/short.mp4"
mkdir -p "$DIR/stills"; rm -f "$DIR/stills/"*
"$PY" video.py images $(cat "$SRC/STILLS")
for f in out/images/*.png; do "$PY" -c "import sys;from PIL import Image;Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2],quality=88)" "$f" "$DIR/stills/still_$(basename "$f" .png).jpg"; done
rm -rf out short.mp4 short_miniature.png short.srt
