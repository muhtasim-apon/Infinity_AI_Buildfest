#!/usr/bin/env bash
# Compose the v2 pitch: rendered frames (30 fps) + narration (padded to 180 s) + burned captions.
# Usage: bash compose_v2.sh <build_dir> <out.mp4>
# The v1 video (Kakatarua_pitch.mp4) is never touched.
set -euo pipefail
BUILD="$1"; OUT="$2"
cd "$BUILD"   # libass needs a simple relative subtitle path on Windows
STYLE="FontName=Segoe UI,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H99000000,BorderStyle=4,Outline=1,Shadow=0,MarginV=22,Alignment=2"
ffmpeg -v error -y -framerate 30 -i frames/f_%06d.jpg -i narration.wav \
  -filter_complex "[1:a]apad=whole_dur=180[a]" -map 0:v:0 -map "[a]" -t 180 \
  -vf "format=yuv420p,subtitles=captions.srt:force_style='$STYLE'" \
  -c:v libx264 -preset slow -crf 19 -profile:v high -movflags +faststart \
  -c:a aac -b:a 160k -ar 48000 "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact "$OUT"
