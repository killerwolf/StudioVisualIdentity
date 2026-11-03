#!/usr/bin/env bash
# slot.sh — exécute une commande en réservant un slot CPU parmi nproc (mêmes verrous que render.mjs).
# usage : out/tools/slot.sh python scene.py ...
N=${SVI_SLOTS:-$(nproc)}; D=/tmp/svi-slots; mkdir -p $D
while :; do
  for i in $(seq 0 $((N-1))); do
    if mkdir "$D/slot$i" 2>/dev/null; then
      echo $$ > "$D/slot$i/pid"; trap 'rm -rf "$D/slot'$i'"' EXIT INT TERM
      "$@"; exit $?
    elif [ -f "$D/slot$i/pid" ] && ! kill -0 "$(cat $D/slot$i/pid)" 2>/dev/null; then rm -rf "$D/slot$i"; fi
  done; sleep 1.5
done
