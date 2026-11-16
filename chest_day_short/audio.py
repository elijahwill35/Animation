"""Adapted from arm_day_routine/audio.py: synthesize an original beat + whoosh/impact SFX and mix with the voiceover.

Everything here is generated procedurally (no samples, no licensed music).
Output: build/mix.wav
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000
rng = np.random.default_rng(7)

tl = json.load(open(os.path.join(BUILD, "timeline.json")))
TOTAL = tl["total"]
N = int(TOTAL * SR) + SR


def read_wav(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
    return x


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # short buffers only
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


# ------------------------------------------------------------------ drums
def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.16) * 0.95 + np.sin(ph * 2) * env(n, 0.001, 0.02) * 0.2


def clap():
    n = int(0.25 * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    bp = noise - lowpass(noise, 900)
    bp = lowpass(bp, 5200)
    e = np.zeros(n, np.float32)
    for off in (0, 0.009, 0.018):
        k = int(off * SR)
        e[k:] += env(n - k, 0.001, 0.012 if off < 0.018 else 0.09)
    return bp * e * 0.55


def hat(open_=False):
    n = int((0.16 if open_ else 0.05) * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    hp = noise - lowpass(noise, 7000)
    return hp * env(n, 0.0005, 0.05 if open_ else 0.012) * 0.22


def bass_note(freq, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    x = np.tanh(x * 1.6)
    return x * env(n, 0.005, length * 0.6) * 0.42


def stab(freqs, length=0.22):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * 1.005 * t) for f in freqs)
    x = lowpass(x.astype(np.float32), 2400)
    return x * env(n, 0.003, 0.08) * 0.07


BPM = 124
beat = 60 / BPM
music = np.zeros(N, np.float32)
K, C, Hc, Ho = kick(), clap(), hat(), hat(True)
# A minor-ish progression: Am - F - C - G (bass roots)
roots = [55.0, 43.65, 65.41, 49.0]
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
nbeats = int(TOTAL / beat) + 2
for b in range(nbeats):
    t = b * beat
    bar = b // 4
    intro = t < 2.0   # the opening stays lighter
    add(music, K, t)
    if b % 4 in (1, 3) and not intro:
        add(music, C, t)
    add(music, Hc, t + beat / 2)
    if not intro:
        add(music, Hc * 0.6, t + beat * 0.75)
        if b % 8 == 7:
            add(music, Ho, t + beat / 2)
    r = roots[bar % 4]
    add(music, bass_note(r, beat * 0.9), t)
    if b % 2 == 0 and not intro:
        add(music, stab(chords[bar % 4]), t + beat * 0.5)

# sidechain pump from the kick
pump = np.ones(N, np.float32)
for b in range(nbeats):
    i = int(b * beat * SR)
    n = int(beat * SR)
    seg = 1 - 0.55 * np.exp(-np.arange(n) / SR / 0.09)
    pump[i:i + n] = seg[: max(0, min(n, N - i))]
music *= pump


# ------------------------------------------------------------------ sfx
def whoosh(length=0.32):
    n = int(length * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    acc = 0.0
    for i in range(n):  # sweeping one-pole lowpass
        c = 600 + 7000 * (t[i] / length) ** 1.5
        a = np.exp(-2 * np.pi * c / SR)
        acc = (1 - a) * noise[i] + a * acc
        out[i] = acc
    shape = np.sin(np.pi * np.clip(t / length, 0, 1)) ** 2
    return out * shape * 0.5


def impact():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = 40 + 90 * np.exp(-t / 0.06)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.25)
    noise = rng.standard_normal(n).astype(np.float32) * env(n, 0.0005, 0.03) * 0.4
    return (boom + noise) * 0.8


def pop_sfx():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 + 1400 * t / 0.08) * t) * env(n, 0.001, 0.025) * 0.35


sfx = np.zeros(N, np.float32)
W = whoosh()
for c in tl["cuts"]:
    add(sfx, W * 0.55, max(0.0, c - 0.16))
for s in tl["slams"]:
    add(sfx, impact() * 0.6, s)
    add(sfx, pop_sfx(), s + 0.02)

# ------------------------------------------------------------------ voice
voice = np.zeros(N, np.float32)
for ln in tl["lines"]:
    x = read_wav(os.path.join(BUILD, "vo", f"{ln['key']}.wav"))
    add(voice, x, ln["start"] + 0.04)

# duck music under the voice
vo_env = np.abs(voice)
win = int(0.12 * SR)
vo_env = np.convolve(vo_env, np.ones(win) / win, mode="same")
duck = 1 - 0.45 * np.clip(vo_env / 0.05, 0, 1)

mix = voice * 1.0 + music * 0.42 * duck + sfx * 0.5
# fade out the tail
fade = int(0.8 * SR)
end = int(TOTAL * SR)
mix[end - fade:end] *= np.linspace(1, 0, fade)
mix[end:] = 0
mix = mix[:end]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 1.25) / np.tanh(1.25) * 0.93

out = os.path.join(BUILD, "mix.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{len(mix)/SR:.2f}s")
