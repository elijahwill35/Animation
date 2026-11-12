"""Voiceover with Piper TTS: one clip per key, cached by (text, settings).

Same voice and processing as the original per-project voice.py scripts, but:
  * the ONNX model is loaded once (not once per sentence),
  * unchanged lines are reused from build/vo/cache (editing one sentence re-voices one sentence),
  * the ffmpeg clean-up chain runs in parallel.

Voice: en-us-ryan-high. Set PIPER_VOICE to the .onnx path (default /root/piper/en-us-ryan-high.onnx).
"""
import hashlib
import json
import os
import shutil
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor

VOICE = os.environ.get("PIPER_VOICE", "/root/piper/en-us-ryan-high.onnx")
# trim edges, presence EQ, light compression, 48 kHz mono
FILTER = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,"
          "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=2.0")

_voice = None


def _load():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        _voice = PiperVoice.load(VOICE)
    return _voice


def _tts(text, path, length_scale, sentence_silence):
    """Exactly what `python3 -m piper --length-scale X --sentence-silence Y -f path` does."""
    from piper import SynthesisConfig
    v = _load()
    cfg = SynthesisConfig(length_scale=length_scale)
    silence = bytes(int(v.config.sample_rate * sentence_silence) * 2)
    with wave.open(path, "wb") as w:
        first = True
        for line in text.splitlines() or [text]:
            for i, ch in enumerate(v.synthesize(line, cfg)):
                if first:
                    w.setframerate(ch.sample_rate)
                    w.setsampwidth(ch.sample_width)
                    w.setnchannels(ch.sample_channels)
                    first = False
                if i > 0:
                    w.writeframes(silence)
                w.writeframes(ch.audio_int16_bytes)


def wav_dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def synth(items, out_dir, length_scale=0.9, sentence_silence=0.1, verbose=True):
    """items: list of (key, spoken_text). Writes out_dir/<key>.wav and durations.json."""
    os.makedirs(out_dir, exist_ok=True)
    cache = os.path.join(out_dir, "cache")
    os.makedirs(cache, exist_ok=True)
    tag = f"{os.path.basename(VOICE)}|{length_scale}|{sentence_silence}|{FILTER}"
    jobs, hits = [], 0
    for key, text in items:
        h = hashlib.sha1(f"{tag}|{text}".encode()).hexdigest()[:16]
        cached = os.path.join(cache, h + ".wav")
        if os.path.exists(cached):
            hits += 1
        elif all(c != cached for _, c in jobs):   # same sentence twice -> voice it once
            raw = os.path.join(cache, h + "_raw.wav")
            _tts(text, raw, length_scale, sentence_silence)   # model is not thread-safe: serial
            jobs.append((raw, cached))

    def post(job):
        raw, cached = job
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", FILTER,
                        "-ar", "48000", "-ac", "1", cached], check=True)
        os.remove(raw)

    with ThreadPoolExecutor(os.cpu_count()) as ex:
        list(ex.map(post, jobs))

    durations = {}
    for key, text in items:
        h = hashlib.sha1(f"{tag}|{text}".encode()).hexdigest()[:16]
        dst = os.path.join(out_dir, key + ".wav")
        shutil.copyfile(os.path.join(cache, h + ".wav"), dst)
        durations[key] = wav_dur(dst)
        if verbose:
            print(f"  {key:8s} {durations[key]:5.2f}s  {text}")
    with open(os.path.join(out_dir, "durations.json"), "w") as f:
        json.dump(durations, f, indent=1)
    print(f"voice: {len(items)} clips ({hits} cached, {len(jobs)} new), "
          f"speech total {sum(durations.values()):.2f}s")
    return durations


def scene_lines(scenes, spoken=lambda s: s):
    """The per-sentence keys used by the routine/props videos: <scene id>_<n>."""
    return [(f"{sc['id']}_{i}", spoken(line)) for sc in scenes for i, line in enumerate(sc["lines"])]
