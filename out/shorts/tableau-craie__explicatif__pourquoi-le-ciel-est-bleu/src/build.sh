#!/usr/bin/env bash
# Reproduction complète du short « Pourquoi le ciel est bleu ? » (à lancer depuis la racine du dépôt).
# usage : bash out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu/src/build.sh [fps]   (fps=6 -> prévisualisation)
set -euo pipefail
D=out/shorts/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu
FPS=${1:-30}
T=/tmp/svi/tableau-craie__explicatif__pourquoi-le-ciel-est-bleu
mkdir -p $T/assets
.venv/bin/python $D/src/chalk_assets.py $T/assets > /dev/null
# le chrono démarre APRÈS l'obtention du slot CPU (temps de rendu Manim réel, sans l'attente de file)
out/tools/slot.sh bash -c "S=\$(date +%s.%N); SVI_ASSETS=$T/assets SVI_FPS=$FPS .venv/bin/manim render $D/src/scene.py Sky --media_dir $T/media_$FPS --disable_caching --progress_bar none -v WARNING && E=\$(date +%s.%N) && echo \"{\\\"manimSeconds\\\": \$(echo \"\$E - \$S\" | bc)}\" > $T/render_time_$FPS.json"
VID=$(find $T/media_$FPS/videos -name Sky.mp4 | head -1)
cp "$VID" $T/video_$FPS.mp4
cat $T/render_time_$FPS.json
.venv/bin/python out/tools/sound.py $D/src/sound.json $T/music.wav
# overlays (grain + textes) composités frame par frame, puis mux son via assemble.py
.venv/bin/python $D/src/composite.py $T/video_$FPS.mp4 $T/assets/overlays.txt $T/video_comp_$FPS.mp4 16.5 $FPS
if [ "$FPS" = "30" ]; then OUT=$D/short.mp4; else OUT=$T/preview.mp4; fi
.venv/bin/python out/tools/assemble.py mux --video $T/video_comp_$FPS.mp4 --music $T/music.wav --out $OUT
echo "$OUT"
