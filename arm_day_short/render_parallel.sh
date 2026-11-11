#!/usr/bin/env bash
# Render in N parallel chunks, then concatenate losslessly.
set -e
cd "$(dirname "$0")"
N=${1:-4}
for k in $(seq 0 $((N-1))); do python3 render.py --range=$k/$N > build/render_$k.log 2>&1 & done
wait
: > build/parts.txt
for k in $(seq 0 $((N-1))); do echo "file 'part$k.mp4'" >> build/parts.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i build/parts.txt -c copy build/video_silent.mp4
echo "render done"
