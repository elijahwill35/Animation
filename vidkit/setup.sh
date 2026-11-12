#!/usr/bin/env bash
# Install everything the video pipeline needs (idempotent; safe to re-run).
set -euo pipefail
python3 -c "import cv2, piper, PIL, numpy" 2>/dev/null || \
  pip install -q opencv-python-headless piper-tts pillow numpy
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
VOICE_DIR=/root/piper
if [ ! -f "$VOICE_DIR/en-us-ryan-high.onnx" ]; then
  mkdir -p "$VOICE_DIR"
  curl -sSL https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz \
    | tar xz -C "$VOICE_DIR"
fi
ls /usr/share/fonts/opentype/inter/InterDisplay-Black.otf >/dev/null
echo "vidkit setup ok"
