#!/usr/bin/env bash
# Compose the final pitch video: trim the recorded storyboard, add narration, burn subtitles.
# Usage: bash compose.sh <build_dir> <out.mp4>
set -euo pipefail
BUILD="$1"; OUT="$2"
OFF=$(cat "$BUILD/offset.txt")
TOTAL=$(python -c "import json;print(json.load(open(r'$BUILD/timeline.json'))['total'])")
cd "$BUILD"   # libass needs a simple relative subtitle path on Windows
STYLE="FontName=Segoe UI,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H99000000,BorderStyle=4,Outline=1,Shadow=0,MarginV=22,Alignment=2"
ffmpeg -v error -y -ss "$OFF" -i storyboard.webm -i narration.wav \
  -t "$TOTAL" -map 0:v:0 -map 1:a:0 \
  -vf "fps=30,format=yuv420p,subtitles=captions.srt:force_style='$STYLE'" \
  -c:v libx264 -preset medium -crf 20 -profile:v high -movflags +faststart \
  -c:a aac -b:a 160k -ar 48000 "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact "$OUT"
