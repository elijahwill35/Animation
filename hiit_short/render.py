"""Render the "No GLP-1 needed" circuit Short (1080x1920, 30 fps) from the 10 s source clip.

Layout follows the "Ozempic Who?" full-body video: blurred footage backdrop, a top label with
elapsed time and a progress bar, then hook slide -> overview list -> one scene per move
(number + body area, title, reps pill, footage in a rounded card, form tip) -> outro grid.
Scene lengths follow the voiceover.

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
from PIL import Image, ImageDraw, ImageFont

from script import (HOOK_LINES, MOVES, OUTRO_LINES, OVERVIEW_LINES, REST, ROUNDS, SEGMENTS,
                    TOPLINE)

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SRC = os.path.join(HERE, "assets", "source.mp4")
W, H, FPS = 1080, 1920, 30
SRC_FPS = 24
SPEED = 0.7

F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GREEN = (190, 242, 60)
ORANGE = (255, 112, 60)
WHITE = (255, 255, 255)
INK = (22, 22, 26)

GAP, LEAD, TAIL = 0.15, 0.3, 0.3
END_TAIL = 1.3
CARD = (140, 450, 940, 1600)          # x0, y0, x1, y1 of the footage card


# ------------------------------------------------------------------ timeline
def wav_dur(key):
    with wave.open(os.path.join(BUILD, "vo", key + ".wav")) as w:
        return w.getnframes() / w.getframerate()


def build_timeline():
    plan = [("hook", "knees", HOOK_LINES), ("overview", "jump", OVERVIEW_LINES)]
    plan += [(m[0], m[0], m[4]) for m in MOVES]
    plan += [("outro", "lunge", OUTRO_LINES)]
    t, scenes, lines = 0.0, [], []
    for si, (sid, seg, texts) in enumerate(plan):
        start = t
        t += 0.15 if si == 0 else LEAD
        sents = []
        for i, _ in enumerate(texts):
            key = f"{sid}_{i}"
            d = wav_dur(key)
            sents.append(dict(key=key, start=t, dur=d))
            lines.append(dict(key=key, start=t))
            t += d + GAP
        t += (END_TAIL if sid == "outro" else TAIL) - GAP
        scenes.append(dict(id=sid, seg=seg, start=start, end=t, sents=sents))
    starts = [s["start"] for s in scenes[1:]]
    slams = [scenes[0]["sents"][1]["start"]] + [s["start"] + 0.1 for s in scenes[2:-1]]
    return dict(total=t, scenes=scenes, cuts=starts, slams=slams, lines=lines)


# ------------------------------------------------------------------ helpers
FRAMES = None
TL = None


def load_frames():
    cap = cv2.VideoCapture(SRC)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    return np.stack(out)


def seg_frame(seg, t, phase=0.0):
    """Ping-pong loop through a segment at SPEED with frame blending (RGB float)."""
    a, b = SEGMENTS[seg]
    L = b - a
    pos = t * SRC_FPS * SPEED + phase * 2 * L
    m = pos % (2 * L)
    p = m if m <= L else 2 * L - m
    i0 = int(p)
    fr = p - i0
    f0 = FRAMES[a + i0].astype(np.float32)
    if fr < 1e-3:
        return f0
    return f0 * (1 - fr) + FRAMES[a + min(i0 + 1, L)].astype(np.float32) * fr


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back_out(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, max(8, int(size)))


def tw(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b[2] - b[0]


@lru_cache(maxsize=None)
def round_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def backdrop(seg, t):
    f = seg_frame(seg, t)
    small = cv2.resize(f, (90, 160), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 3)
    big = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR) * 0.33
    return Image.fromarray(np.clip(big, 0, 255).astype(np.uint8)).convert("RGBA")


def footage_card(base, seg, t, box, k=1.0, radius=40, phase=0.0, border=True):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sc = 0.94 + 0.06 * k
    w2, h2 = int(w * sc), int(h * sc)
    f = seg_frame(seg, t, phase)
    fh, fw = f.shape[:2]
    s = max(w2 / fw, h2 / fh)
    rs = cv2.resize(f, (int(fw * s) + 1, int(fh * s) + 1), interpolation=cv2.INTER_LINEAR)
    oy = (rs.shape[0] - h2) // 2
    ox = (rs.shape[1] - w2) // 2
    crop = np.clip(rs[oy:oy + h2, ox:ox + w2], 0, 255).astype(np.uint8)
    img = Image.fromarray(crop).convert("RGBA")
    a = round_mask(w2, h2, radius)
    if k < 1:
        a = a.point(lambda v: int(v * min(1.0, k * 1.5)))
    img.putalpha(a)
    px, py = x0 + (w - w2) // 2, y0 + (h - h2) // 2
    base.alpha_composite(img, (px, py))
    if border:
        ImageDraw.Draw(base).rounded_rectangle((px, py, px + w2 - 1, py + h2 - 1), radius,
                                               outline=(255, 255, 255, int(70 * k)), width=3)


def pill(d, cx, cy, text, col, size=32, pad=34, h=60):
    f = font(F_BLACK, size)
    w = tw(d, text, f) + pad * 2
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h // 2, fill=col)
    d.text((cx, cy + 1), text, font=f, fill=INK, anchor="mm")


def topbar(base, t):
    d = ImageDraw.Draw(base)
    d.text((44, 50), TOPLINE, font=font(F_BOLD, 26), fill=(255, 255, 255, 210), anchor="lm")
    d.text((W - 44, 50), f"{int(t) // 60}:{int(t) % 60:02d}", font=font(F_BOLD, 26),
           fill=(255, 255, 255, 170), anchor="rm")
    d.rounded_rectangle((44, 78, W - 44, 86), 4, fill=(255, 255, 255, 45))
    x1 = 44 + (W - 88) * min(1.0, t / TL["total"])
    d.rounded_rectangle((44, 78, max(52, x1), 86), 4, fill=GREEN)


def check_icon(d, cx, cy, r=20):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
    d.line((cx - 9, cy + 1, cx - 2, cy + 8, cx + 10, cy - 7), fill=INK, width=5, joint="curve")


# ------------------------------------------------------------------ scenes
def draw_hook(base, sc, t):
    d = ImageDraw.Draw(base)
    s0, s1 = sc["sents"]
    k = back_out((t - sc["start"]) / 0.35)
    d.text((W / 2, 640), "Who needs", font=font(F_BLACK, 120 * (0.6 + 0.4 * k)), fill=WHITE, anchor="mm")
    k2 = back_out((t - sc["start"] - 0.35) / 0.35)
    if t > sc["start"] + 0.35:
        d.text((W / 2, 790), "a GLP-1?", font=font(F_BLACK, 160 * (0.6 + 0.4 * k2)), fill=GREEN,
               anchor="mm")
    if t >= s1["start"]:
        k3 = back_out((t - s1["start"]) / 0.3)
        d.text((W / 2, 1040), "NOT YOU.", font=font(F_BLACK, 170 * (0.5 + 0.5 * k3)), fill=ORANGE,
               anchor="mm")
        k4 = ease_out((t - s1["start"] - 0.4) / 0.3)
        if k4 > 0:
            d.text((W / 2, 1170 + (1 - k4) * 30), "not after this routine", font=font(F_BOLD, 58),
                   fill=(255, 255, 255, int(255 * k4)), anchor="mm")


def draw_overview(base, sc, t):
    d = ImageDraw.Draw(base)
    k = ease_out((t - sc["start"]) / 0.3)
    d.text((W / 2, 300), "THE WORKOUT", font=font(F_BLACK, 40), fill=GREEN, anchor="mm")
    d.text((W / 2, 380 + (1 - k) * 30), f"{len(MOVES)} moves · {ROUNDS} rounds", font=font(F_BLACK, 86),
           fill=WHITE, anchor="mm")
    for i, m in enumerate(MOVES):
        ki = back_out((t - sc["start"] - 0.15 - i * 0.12) / 0.3)
        if t <= sc["start"] + 0.15 + i * 0.12:
            continue
        y = 480 + i * 132
        x0 = 100 + (1 - ki) * 700
        d.rounded_rectangle((x0, y, x0 + 880, y + 110), 28, fill=(255, 255, 255, 240))
        d.text((x0 + 40, y + 42), m[1], font=font(F_BLACK, 44), fill=INK, anchor="lm")
        d.text((x0 + 40, y + 84), m[2], font=font(F_BOLD, 24), fill=(110, 110, 120), anchor="lm")
        col = GREEN if i % 2 == 0 else ORANGE
        f = font(F_BLACK, 28)
        pw = tw(d, m[3], f) + 50
        d.rounded_rectangle((x0 + 840 - pw, y + 30, x0 + 840, y + 80), 25, fill=col)
        d.text((x0 + 840 - pw / 2, y + 56), m[3], font=f, fill=INK, anchor="mm")
    y = 480 + len(MOVES) * 132 + 30
    kr = ease_out((t - sc["start"] - 0.9) / 0.3)
    if kr > 0:
        d.text((W / 2, y), f"Rest {REST} between rounds", font=font(F_BOLD, 40),
               fill=(255, 255, 255, int(255 * kr)), anchor="mm")
        d.text((W / 2, y + 62), "No equipment needed", font=font(F_BLACK, 42),
               fill=GREEN + (int(255 * kr),), anchor="mm")


def draw_move(base, sc, t, i):
    m = MOVES[i]
    col = GREEN if i % 2 == 0 else ORANGE
    d = ImageDraw.Draw(base)
    k = ease_out((t - sc["start"]) / 0.3)
    yoff = (1 - k) * -40
    d.text((W / 2, 225 + yoff), f"{i + 1}/{len(MOVES)}  ·  {m[2]}", font=font(F_BLACK, 34), fill=col,
           anchor="mm")
    size = 96
    while tw(d, m[1], font(F_BLACK, size)) > W - 120:
        size -= 4
    d.text((W / 2, 305 + yoff), m[1], font=font(F_BLACK, size), fill=WHITE, anchor="mm")
    kp = back_out((t - sc["start"] - 0.12) / 0.3)
    if t > sc["start"] + 0.12:
        f = 32 * (0.6 + 0.4 * kp)
        pill(d, W / 2, 392, m[3], col, size=f, pad=34, h=int(60 * (0.6 + 0.4 * kp)))
    footage_card(base, m[0], t - sc["start"], CARD, k=k, phase=0.15 * i)
    tip_line = sc["sents"][1]
    if t >= tip_line["start"] - 0.1:
        kt = back_out((t - tip_line["start"] + 0.1) / 0.3)
        d = ImageDraw.Draw(base)
        f = font(F_BOLD, 36)
        w = tw(d, m[5], f) + 130
        y = 1665 + (1 - kt) * 80
        a = int(245 * min(1.0, kt))
        d.rounded_rectangle((W / 2 - w / 2, y, W / 2 + w / 2, y + 84), 42, fill=(255, 255, 255, a))
        check_icon(d, W / 2 - w / 2 + 50, y + 42)
        d.text((W / 2 - w / 2 + 88, y + 43), m[5], font=f, fill=INK, anchor="lm")


def draw_outro(base, sc, t):
    d = ImageDraw.Draw(base)
    k = back_out((t - sc["start"]) / 0.35)
    d.text((W / 2, 290), f"Do {ROUNDS} rounds", font=font(F_BLACK, 112 * (0.6 + 0.4 * k)), fill=WHITE,
           anchor="mm")
    pill(d, W / 2, 395, f"Rest {REST} between rounds", GREEN, size=30, pad=32, h=58)
    cw, ch, gap = 280, 410, 20
    x0 = (W - 3 * cw - 2 * gap) // 2
    for i, m in enumerate(MOVES):
        ki = ease_out((t - sc["start"] - 0.1 - i * 0.08) / 0.3)
        if ki <= 0:
            continue
        cx = x0 + (i % 3) * (cw + gap)
        cy = 470 + (i // 3) * (ch + gap)
        footage_card(base, m[0], t, (cx, cy, cx + cw, cy + ch), k=ki, radius=24, phase=0.2 * i)
        d = ImageDraw.Draw(base)
        d.ellipse((cx + 12, cy + 12, cx + 56, cy + 56), fill=GREEN if i % 2 == 0 else ORANGE)
        d.text((cx + 34, cy + 35), str(i + 1), font=font(F_BLACK, 28), fill=INK, anchor="mm")
    s1 = sc["sents"][1]
    if t >= s1["start"] - 0.1:
        k2 = ease_out((t - s1["start"] + 0.1) / 0.35)
        d.text((W / 2, 1405 + (1 - k2) * 30), "Save this for your next workout!", font=font(F_BLACK, 50),
               fill=GREEN + (int(255 * k2),), anchor="mm")
        d.text((W / 2, 1475 + (1 - k2) * 30), "Tag the friend who needs it", font=font(F_BOLD, 42),
               fill=(255, 255, 255, int(255 * k2)), anchor="mm")


def render_frame(fi):
    t = fi / FPS
    si = next((i for i, s in enumerate(TL["scenes"]) if s["start"] <= t < s["end"]), len(TL["scenes"]) - 1)
    sc = TL["scenes"][si]
    base = backdrop(sc["seg"], t)
    if sc["id"] == "hook":
        draw_hook(base, sc, t)
    elif sc["id"] == "overview":
        draw_overview(base, sc, t)
    elif sc["id"] == "outro":
        draw_outro(base, sc, t)
    else:
        draw_move(base, sc, t, si - 2)
    topbar(base, t)
    arr = np.asarray(base.convert("RGB"))
    since = t - sc["start"]
    if si > 0 and since < 0.12:   # quick flash on scene change
        arr = (arr + (1 - since / 0.12) * 0.35 * (255 - arr.astype(np.float32))).astype(np.uint8)
    if t > TL["total"] - 0.5:
        arr = (arr * max(0.0, (TL["total"] - t) / 0.5)).astype(np.uint8)
    return np.ascontiguousarray(arr).tobytes()


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
        print(f"  {s['id']:9s} {s['start']:6.2f} -> {s['end']:6.2f}")
    if "--preview" in sys.argv:
        init_worker(tl)
        out = os.path.join(BUILD, "preview")
        os.makedirs(out, exist_ok=True)
        times = [float(a.split("=")[1]) for a in sys.argv if a.startswith("--t=")]
        if not times:
            for s in tl["scenes"]:
                times += [s["start"] + 0.5, s["end"] - 0.2]
        for tt in times:
            img = np.frombuffer(render_frame(int(tt * FPS)), np.uint8).reshape(H, W, 3)
            Image.fromarray(img).save(os.path.join(out, f"f_{tt:06.2f}.jpg"), quality=85)
        print("previews ->", out)
        return
    nframes = int(round(tl["total"] * FPS))
    out = os.path.join(BUILD, "video_silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
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
