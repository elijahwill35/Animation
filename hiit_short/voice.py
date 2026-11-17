"""Voiceover: one Piper TTS clip per line, same voice and processing as the other videos.

Writes build/vo/<key>.wav and build/vo/durations.json.
Set PIPER_VOICE to the .onnx path (default /root/piper/en-us-ryan-high.onnx).
"""
import json
import os
import subprocess
import wave

from script import HOOK_LINES, MOVES, OUTRO_LINES, OVERVIEW_LINES, SPOKEN

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "vo")
os.makedirs(OUT, exist_ok=True)
VOICE = os.environ.get("PIPER_VOICE", "/root/piper/en-us-ryan-high.onnx")


def all_lines():
    for i, t in enumerate(HOOK_LINES):
        yield f"hook_{i}", t
    for i, t in enumerate(OVERVIEW_LINES):
        yield f"overview_{i}", t
    for m in MOVES:
        for i, t in enumerate(m[4]):
            yield f"{m[0]}_{i}", t
    for i, t in enumerate(OUTRO_LINES):
        yield f"outro_{i}", t


if __name__ == "__main__":
    durations = {}
    for key, text in all_lines():
        raw = os.path.join(OUT, key + "_raw.wav")
        out = os.path.join(OUT, key + ".wav")
        subprocess.run(["python3", "-m", "piper", "-m", VOICE, "-c", VOICE + ".json",
                        "--length-scale", "0.86", "--sentence-silence", "0.1", "-f", raw],
                       input=SPOKEN.get(key, text).encode(), check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,"
                        "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=2.0",
                        "-ar", "48000", "-ac", "1", out], check=True)
        with wave.open(out) as w:
            durations[key] = w.getnframes() / w.getframerate()
        print(f"{key:11s} {durations[key]:.2f}s  {text}")
    with open(os.path.join(OUT, "durations.json"), "w") as f:
        json.dump(durations, f, indent=1)
    print("speech total", round(sum(durations.values()), 2))
