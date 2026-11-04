#!/usr/bin/env bash
# build.sh — reproduit le short depuis la racine du dépôt : rendu GSAP -> post OpenCV -> son -> mux.
# usage : bash out/shorts/<dossier>/src/build.sh   (depuis la racine du dépôt)
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"; DIR="$(dirname "$SRC")"; NAME="$(basename "$DIR")"
DUR=$(cat "$SRC/DURATION"); FLASH=$(cat "$SRC/FLASH" 2>/dev/null || echo "")
TMP=/tmp/svi/$NAME; mkdir -p "$TMP"
node out/tools/render.mjs "$SRC/index.html" --out "$TMP/raw.mp4" --duration "$DUR" | tee "$TMP/render.json"
out/tools/slot.sh .venv/bin/python "$SRC/post.py" video "$TMP/raw.mp4" "$TMP/video.mp4" --seed 1900 --flash "$FLASH" | tee "$TMP/post.json"
.venv/bin/python out/tools/sound.py "$SRC/sound.json" "$TMP/music.wav"
.venv/bin/python out/tools/assemble.py mux --video "$TMP/video.mp4" --music "$TMP/music.wav" --out "$DIR/short.mp4"
