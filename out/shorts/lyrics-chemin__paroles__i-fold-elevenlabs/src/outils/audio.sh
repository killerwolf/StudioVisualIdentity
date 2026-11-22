#!/bin/bash
# audio.sh <in.mp3> <out.wav> <cut_in_s> <cut_out_s> <preroll_s> <duree_video_s> [fade_in_s] [fade_out_s]
# extrait [cut_in, cut_out] du morceau, fondu d'entrée / de sortie, pré-roulé muet, complété de silence jusqu'à duree, puis
# normalisation EBU R128 en deux passes, linéaire : -14 LUFS, crête vraie -1.5 dBTP (marge pour l'AAC).
set -e
IN=$1; OUT=$2; CI=$3; CO=$4; PRE=$5; DUR=$6; FI=${7:-0.15}; FO=${8:-0.4}
LEN=$(python3 -c "print($CO-$CI)"); FOST=$(python3 -c "print(max(0,$CO-$CI-$FO))"); PMS=$(python3 -c "print(int($PRE*1000))")
PRE_F="atrim=start=$CI:end=$CO,asetpts=PTS-STARTPTS,afade=t=in:d=$FI,afade=t=out:st=$FOST:d=$FO,adelay=${PMS}|${PMS},apad=whole_dur=$DUR,atrim=end=$DUR"
J=$(ffmpeg -hide_banner -i "$IN" -af "$PRE_F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -af "$PRE_F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true:print_format=json" -ar 48000 -ac 2 "$OUT" 2>&1 | tail -0
ffmpeg -hide_banner -i "$IN" -af "$PRE_F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true:print_format=json" -f null - 2>&1 | grep -E 'normalization_type|output_i|output_tp'
