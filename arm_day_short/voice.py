"""Generate the voiceover per scene with Piper TTS and record durations.

Requires: pip install piper-tts, and the Ryan (high) voice:
  https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz
Set PIPER_VOICE to the .onnx path (default /root/piper/en-us-ryan-high.onnx).
"""
import json
import os
import subprocess
import wave

from script import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "vo")
os.makedirs(OUT, exist_ok=True)
VOICE = os.environ.get("PIPER_VOICE", "/root/piper/en-us-ryan-high.onnx")

durations = {}
for sc in SCENES:
    raw = os.path.join(OUT, f"{sc['id']}_raw.wav")
    out = os.path.join(OUT, f"{sc['id']}.wav")
    subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-c", VOICE + ".json",
                    "--length-scale", "0.86", "--sentence-silence", "0.12", "-f", raw],
                   input=sc["vo"].encode(), check=True, capture_output=True)
    # punchier "YouTube" voice: trim edges, light compression + presence EQ, 48 kHz
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,"
                    "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=2.0",
                    "-ar", "48000", "-ac", "1", out], check=True)
    with wave.open(out) as w:
        durations[sc["id"]] = w.getnframes() / w.getframerate()
    print(f"{sc['id']:6s} {durations[sc['id']]:.2f}s")

with open(os.path.join(OUT, "durations.json"), "w") as f:
    json.dump(durations, f, indent=1)
print("total", round(sum(durations.values()), 2))
