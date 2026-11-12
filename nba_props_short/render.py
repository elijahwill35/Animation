"""Render the NBA player-props Short (1080x1920, 30 fps) from the 10 s motion-graphics clip.

Each scene plays its card's build-in animation once at normal speed, then holds on the
fully revealed frame with a slow push-in and drifting embers while the voiceover talks
through the pick. Word-chunk captions sit in the empty space under the cards.

  python3 render.py            -> build/video_silent.mp4 + build/timeline.json
  python3 render.py --preview  -> still frames in build/preview/
"""
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from script import SCENES, caption

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SRC = os.path.join(HERE, "assets", "source.mp4")
W, H, FPS = 1080, 1920, 30
SRC_FPS = 24

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
YELLOW = (255, 214, 64)
WHITE = (255, 255, 255)

GAP = 0.28
LEAD = 0.55          # let the card start building before the voice comes in
TAIL = 0.35
END_TAIL = 1.6
CAPTION_Y = 1700


# ------------------------------------------------------------------ timeline
def wav_dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def chunk_words(words, max_words=3):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w[-1] in ".,?!":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_timeline():
    t = 0.0
    scenes, lines = [], []
    for si, sc in enumerate(SCENES):
        start = t
        t += 0.25 if si == 0 else LEAD
        sents = []
        for i, line in enumerate(sc["lines"]):
            key = f"{sc['id']}_{i}"
            d = wav_dur(os.path.join(BUILD, "vo", key + ".wav"))
            chunks = chunk_words(caption(line).split())
            weights = [sum(len(w) for w in c) + 2 for c in chunks]
            ct, caps = t, []
            for c, wgt in zip(chunks, weights):
                cd = d * wgt / sum(weights)
                caps.append(dict(words=c, start=ct, end=ct + cd))
                ct += cd
            caps[-1]["end"] = t + d + GAP * 0.8
            sents.append(dict(key=key, start=t, dur=d, caps=caps))
            lines.append(dict(key=key, start=t))
            t += d + GAP
        t += (END_TAIL if si == len(SCENES) - 1 else TAIL) - GAP
        scenes.append(dict(id=sc["id"], start=start, end=t, play=sc["play"], sents=sents))
    starts = [s["start"] for s in scenes[1:]]
    return dict(total=t, scenes=scenes, cuts=starts, slams=[s + 0.12 for s in starts], lines=lines)


# ------------------------------------------------------------------ frames
FRAMES = None
TL = None


def load_frames():
    cap = cv2.VideoCapture(SRC)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return np.stack(out)


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def back_out(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def frame_bg(sc, t):
    a, b = sc["play"]
    lt = t - sc["start"]
    pos = lt * SRC_FPS
    play_len = b - a
    if pos < play_len:
        i0 = int(pos)
        fr = pos - i0
        img = FRAMES[a + i0].astype(np.float32) * (1 - fr) + FRAMES[min(a + i0 + 1, b)].astype(np.float32) * fr
        zoom = 1.0
    else:
        img = FRAMES[b].astype(np.float32)
        hold_t = (pos - play_len) / SRC_FPS
        hold_len = max(0.5, sc["end"] - sc["start"] - play_len / SRC_FPS)
        zoom = 1 + 0.045 * ease_in_out(hold_t / hold_len)
    sh, sw = img.shape[:2]
    s = W / sw * zoom
    # push in toward the upper-middle, where the card is
    cx, cy = sw * 0.5, sh * 0.42
    # keep the anchor point (cx, cy) fixed on screen while zooming
    M = np.float32([[s, 0, W / 2 - cx * s], [0, s, cy * W / sw - cy * s]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# embers: deterministic particles drifting upward over the whole video
rng = np.random.default_rng(11)
NP = 70
P_X = rng.uniform(0, W, NP)
P_Y = rng.uniform(0, H, NP)
P_V = rng.uniform(40, 140, NP)          # px/s upward
P_R = rng.uniform(1.5, 5.0, NP)
P_PH = rng.uniform(0, 2 * np.pi, NP)
P_SW = rng.uniform(10, 40, NP)          # sideways sway


def embers(t):
    layer = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(NP):
        y = (P_Y[i] - t * P_V[i]) % (H + 40) - 20
        x = P_X[i] + math.sin(t * 1.3 + P_PH[i]) * P_SW[i]
        # brighter near the bottom, like the sparks in the source
        a = (0.35 + 0.65 * (y / H)) * (0.6 + 0.4 * math.sin(t * 5 + P_PH[i] * 3))
        r = P_R[i] / 2
        col = (255, int(140 + 60 * (i % 3) / 2), 40, int(200 * max(0.0, a)))
        d.ellipse((x / 2 - r, y / 2 - r, x / 2 + r, y / 2 + r), fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    return layer.resize((W, H), Image.BILINEAR)


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def caption_img(words, hot):
    f = font(FONT_BLACK, 84)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    space = 22
    widths = [tmp.textbbox((0, 0), w, font=f, stroke_width=9)[2] for w in words]
    tw = sum(widths) + space * (len(words) - 1)
    img = Image.new("RGBA", (tw + 40, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 20
    for w, ww in zip(words, widths):
        col = YELLOW if w in hot else WHITE
        d.text((x + 5, 26), w, font=f, fill=(0, 0, 0, 150), stroke_width=9, stroke_fill=(0, 0, 0, 150))
        d.text((x, 20), w, font=f, fill=col, stroke_width=9, stroke_fill=(0, 0, 0))
        x += ww + space
    return img


def draw_caption(base, cap, hot, t):
    img = caption_img(tuple(w.upper() for w in cap["words"]), hot)
    k = back_out((t - cap["start"]) / 0.16)
    sc = 0.75 + 0.25 * k
    if img.width * sc > W - 80:
        sc *= (W - 80) / (img.width * sc)
    im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
    base.alpha_composite(im, (int(W / 2 - im.width / 2), int(CAPTION_Y - im.height / 2)))


def render_frame(fi):
    t = fi / FPS
    si = next((i for i, s in enumerate(TL["scenes"]) if s["start"] <= t < s["end"]), len(TL["scenes"]) - 1)
    sc = TL["scenes"][si]
    bg = frame_bg(sc, t)
    base = Image.fromarray(cv2.cvtColor(bg.astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
    base.alpha_composite(embers(t))
    hot = frozenset(SCENES[si]["hot"])
    for s in sc["sents"]:
        for c in s["caps"]:
            if c["start"] <= t < c["end"]:
                draw_caption(base, c, hot, t)
    arr = np.asarray(base.convert("RGB"))
    total = TL["total"]
    if t > total - 0.5:
        arr = (arr * max(0.0, (total - t) / 0.5)).astype(np.uint8)
    return arr.tobytes()


def init_worker(tl):
    global FRAMES, TL
    FRAMES = load_frames()
    TL = tl


def main():
    tl = build_timeline()
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(tl, f, indent=1)
    print(f"total {tl['total']:.2f}s")
    for s in tl["scenes"]:
        print(f"  {s['id']:6s} {s['start']:6.2f} -> {s['end']:6.2f}")
    nframes = int(round(tl["total"] * FPS))
    if "--preview" in sys.argv:
        init_worker(tl)
        out = os.path.join(BUILD, "preview")
        os.makedirs(out, exist_ok=True)
        times = [float(a.split("=")[1]) for a in sys.argv if a.startswith("--t=")]
        if not times:
            for s in tl["scenes"]:
                times += [s["start"] + 0.4, (s["start"] + s["end"]) / 2, s["end"] - 0.2]
        for tt in times:
            img = np.frombuffer(render_frame(int(tt * FPS)), np.uint8).reshape(H, W, 3)
            Image.fromarray(img).save(os.path.join(out, f"f_{tt:06.2f}.jpg"), quality=85)
        print("previews ->", out)
        return
    out = os.path.join(BUILD, "video_silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=init_worker, initargs=(tl,)) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(nframes), chunksize=8)):
            ff.stdin.write(buf)
            if i % 300 == 0:
                print(f"  frame {i}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
