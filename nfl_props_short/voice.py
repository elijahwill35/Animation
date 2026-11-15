"""Voiceover: one Piper TTS clip per sentence, same voice and processing as the other videos.

Requires: pip install piper-tts, and the Ryan (high) voice:
  https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz
Set PIPER_VOICE to the .onnx path (default /root/piper/en-us-ryan-high.onnx).
Writes build/vo/<scene>_<n>.wav and build/vo/durations.json.
"""
import json
import os
import subprocess
import wave

from script import SCENES, spoken

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "vo")
os.makedirs(OUT, exist_ok=True)
VOICE = os.environ.get("PIPER_VOICE", "/root/piper/en-us-ryan-high.onnx")

durations = {}
for sc in SCENES:
    for i, line in enumerate(sc["lines"]):
        key = f"{sc['id']}_{i}"
        raw = os.path.join(OUT, key + "_raw.wav")
        out = os.path.join(OUT, key + ".wav")
        subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-c", VOICE + ".json",
                        "--length-scale", "0.85", "--sentence-silence", "0.1", "-f", raw],
                       input=spoken(line).encode(), check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,"
                        "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=2.0",
                        "-ar", "48000", "-ac", "1", out], check=True)
        with wave.open(out) as w:
            durations[key] = w.getnframes() / w.getframerate()
        print(f"{key:8s} {durations[key]:.2f}s  {spoken(line)}")

with open(os.path.join(OUT, "durations.json"), "w") as f:
    json.dump(durations, f, indent=1)
print("speech total", round(sum(durations.values()), 2))
