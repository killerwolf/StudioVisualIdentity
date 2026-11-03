#!/usr/bin/env bash
# build.sh <slug> — rend l'affiche d'une direction (t=2.0 s) puis applique le post-traitement
# éventuel (src/<slug>/post.py), et écrit out/report/posters/<slug>.jpg (1080×1920).
# Usage depuis la racine du dépôt :  bash out/report/posters/src/build.sh gazette-1900
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
SLUG="$1"
SRC="$ROOT/out/report/posters/src/$SLUG"
OUTD="$ROOT/out/report/posters"
TMPD="$(mktemp -d)"
cd "$ROOT"
node out/tools/render.mjs "$SRC/index.html" --stills 2.0 --stills-dir "$TMPD" --prefix "$SLUG" --quality 95
STILL="$TMPD/${SLUG}_2.00s.jpg"
if [ -f "$SRC/post.py" ]; then
  "$ROOT/.venv/bin/python" "$SRC/post.py" "$STILL" "$OUTD/$SLUG.jpg"
else
  mv "$STILL" "$OUTD/$SLUG.jpg"
fi
rm -rf "$TMPD"
echo "-> $OUTD/$SLUG.jpg"
