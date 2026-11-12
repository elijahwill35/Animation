"""Render the glute day routine video (1080x1920, 30 fps) from the 10 s source clip.

Each exercise shot is slowed down and ping-pong looped (with frame blending) so the
lifter keeps repping for as long as the narration needs, re-framed with punch-ins and a
slow push, and overlaid with: exercise header + progress, a sets/reps/rest card beside
the lifter, and word-chunk captions synced to the voiceover.

  python3 render.py            -> build/video_silent.mp4 + build/timeline.json
  python3 render.py --preview  -> a few still frames in build/preview/
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

from script import EXERCISES, SCENES, SEGMENTS

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SRC = os.path.join(HERE, "assets", "source.mp4")
W, H, FPS = 1080, 1920, 30
SRC_FPS = 24

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
RED = (235, 40, 50)
YELLOW = (255, 214, 64)
WHITE = (255, 255, 255)

GAP = 0.22          # pause between sentences
LEAD = {"intro": 0.25, "outro": 0.35}
TAIL = {"intro": 0.35, "outro": 1.9}
EX_LEAD, EX_TAIL = 0.4, 0.6


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
    scenes, cuts, slams, lines = [], [], [], []
    for sc in SCENES:
        is_ex = "num" in sc
        lead = EX_LEAD if is_ex else LEAD[sc["id"]]
        tail = EX_TAIL if is_ex else TAIL[sc["id"]]
        start = t
        t += lead
        sents = []
        for i, line in enumerate(sc["lines"]):
            key = f"{sc['id']}_{i}"
            d = wav_dur(os.path.join(BUILD, "vo", key + ".wav"))
            words = line.split()
            chunks = chunk_words(words)
            weights = [sum(len(w) for w in c) + 2 for c in chunks]
            tot = sum(weights)
            ct, caps = t, []
            for c, wgt in zip(chunks, weights):
                cd = d * wgt / tot
                caps.append(dict(words=c, start=ct, end=ct + cd))
                ct += cd
            caps[-1]["end"] = t + d + GAP * 0.8  # hold last chunk through the pause
            sents.append(dict(key=key, start=t, dur=d, caps=caps, text=line))
            lines.append(dict(key=key, start=t))
            t += d + GAP
        t += tail - GAP
        end = t
        # shots: split the scene evenly
        n = len(sc["shots"])
        shots = []
        for k, sh in enumerate(sc["shots"]):
            s0 = start + (end - start) * k / n
            s1 = start + (end - start) * (k + 1) / n
            shots.append(dict(seg=sh[0], zoom=sh[1], cx=sh[2], cy=sh[3], side=sh[4],
                              card_y=sh[5] if len(sh) > 5 else 720,
                              start=s0, end=s1, phase=(k * 0.37 + len(scenes) * 0.21) % 1))
            if k > 0:
                cuts.append(s0)
        cuts.append(start)
        slams.append(start)
        if is_ex:
            slams.append(sents[1]["start"])  # sets/reps card lands
        scenes.append(dict(id=sc["id"], start=start, end=end, sents=sents, shots=shots))
    return dict(total=t, scenes=scenes, cuts=sorted(set(cuts))[1:], slams=slams, lines=lines)


# ------------------------------------------------------------------ source frames
FRAMES = None


def load_frames():
    cap = cv2.VideoCapture(SRC)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return np.stack(out)


def src_frame(seg, t, speed, phase):
    a, b = SEGMENTS[seg]
    L = b - a
    pos = t * SRC_FPS * speed + phase * 2 * L
    m = pos % (2 * L)
    p = m if m <= L else 2 * L - m
    i0 = int(math.floor(p))
    fr = p - i0
    i1 = min(i0 + 1, L)
    f0 = FRAMES[a + i0].astype(np.float32)
    if fr < 1e-3:
        return f0
    return f0 * (1 - fr) + FRAMES[a + i1].astype(np.float32) * fr


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back_out(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def frame_bg(shot, t, speed):
    lt = t - shot["start"]
    dur = shot["end"] - shot["start"]
    img = src_frame(shot["seg"], lt, speed, shot["phase"])
    sh, sw = img.shape[:2]
    punch = 1 + 0.07 * (1 - ease_out(lt / 0.25))
    push = 1 + 0.05 * (lt / max(dur, 1e-3))
    s = (W / sw) * shot["zoom"] * punch * push
    cx, cy = shot["cx"] * sw, shot["cy"] * sh
    tx, ty = W / 2 - cx * s, H / 2 - cy * s
    tx = min(0, max(W - sw * s, tx))
    ty = min(0, max(H - sh * s, ty))
    M = np.float32([[s, 0, tx], [0, s, ty]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # light grade: a touch of contrast + warmth
    out = np.clip((out - 128) * 1.06 + 128 + np.float32([-4, 0, 6]), 0, 255)
    return out


# ------------------------------------------------------------------ overlay drawing
@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(d, txt, f, stroke=0):
    b = d.textbbox((0, 0), txt, font=f, stroke_width=stroke)
    return b[2] - b[0]


def shadow_text(d, xy, txt, f, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), anchor="la"):
    x, y = xy
    d.text((x + 4, y + 6), txt, font=f, fill=(0, 0, 0, 140), stroke_width=stroke,
           stroke_fill=(0, 0, 0, 140), anchor=anchor)
    d.text((x, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


@lru_cache(maxsize=None)
def gradient():
    g = np.zeros((H, W, 4), np.uint8)
    y = np.arange(H)[:, None]
    top = np.clip(1 - y / 520, 0, 1) ** 1.6 * 170
    bot = np.clip((y - 1250) / 670, 0, 1) ** 1.4 * 200
    g[..., 3] = np.maximum(top, bot).astype(np.uint8).repeat(W, 1)
    return Image.fromarray(g, "RGBA")


@lru_cache(maxsize=None)
def caption_img(words, hot):
    f = font(FONT_BLACK, 92)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    space = 24
    widths = [text_w(tmp, w, f, 9) for w in words]
    tw = sum(widths) + space * (len(words) - 1)
    img = Image.new("RGBA", (tw + 40, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 20
    for w, ww in zip(words, widths):
        col = YELLOW if w in hot else WHITE
        d.text((x + 5, 26), w, font=f, fill=(0, 0, 0, 150), stroke_width=9, stroke_fill=(0, 0, 0, 150))
        d.text((x, 20), w, font=f, fill=col, stroke_width=9, stroke_fill=(0, 0, 0))
        x += ww + space
    return img


def draw_caption(base, cap, hot, t):
    words = tuple(w.upper() for w in cap["words"])
    img = caption_img(words, hot)
    k = back_out((t - cap["start"]) / 0.16)
    sc = 0.75 + 0.25 * k
    max_w = W - 80
    if img.width * sc > max_w:
        sc *= max_w / (img.width * sc)
    im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
    base.alpha_composite(im, (int(W / 2 - im.width / 2), int(1600 - im.height / 2)))


def rounded_panel(size, radius=34, fill=(12, 12, 16, 185)):
    p = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill)
    return p


def draw_header(base, ex, t, start):
    d = ImageDraw.Draw(base)
    k = ease_out((t - start) / 0.35)
    off = int((1 - k) * -200)
    # pill
    pill = f"EXERCISE {ex['num']} OF {len(EXERCISES)}"
    fp = font(FONT_BLACK, 38)
    pw = text_w(d, pill, fp) + 56
    d.rounded_rectangle((60, 92 + off, 60 + pw, 150 + off), 29, fill=RED)
    d.text((60 + 28, 121 + off), pill, font=fp, fill=WHITE, anchor="lm")
    # progress bar
    for i in range(len(EXERCISES)):
        x0 = 60 + pw + 30 + i * 70
        col = WHITE if i + 1 == ex["num"] else (255, 255, 255, 90)
        if i + 1 < ex["num"]:
            col = RED
        d.rounded_rectangle((x0, 114 + off, x0 + 56, 128 + off), 7, fill=col)
    # title, shrink to fit
    size = 104
    while text_w(d, ex["title"], font(FONT_BLACK, size), 6) > W - 120 and size > 50:
        size -= 2
    shadow_text(d, (60, 172 + off), ex["title"], font(FONT_BLACK, size), stroke=6)
    ft = font(FONT_BOLD, 40)
    d.text((64, 172 + size + 24 + off), "TARGET  ·  " + ex["muscle"], font=ft, fill=(255, 255, 255, 230),
           stroke_width=3, stroke_fill=(0, 0, 0))


def draw_card(base, ex, t, card_start, side, sents, y=720):
    if t < card_start:
        return
    k = back_out((t - card_start) / 0.4)
    cw, chh = 330, 560
    x_in = 44 if side == "left" else W - cw - 44
    x_off = -cw - 80 if side == "left" else cw + 80
    x = int(x_in + x_off * (1 - k))
    panel = rounded_panel((cw, chh))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle((0, 0, 14, chh - 1), 7, fill=RED)
    rows = [("SETS", ex["sets"]), ("REPS", ex["reps"]), ("REST", ex["rest"])]
    # highlight the row being spoken: sets+reps during sentence 1, rest during the last
    spoken = None
    s1 = sents[1]
    if s1["start"] <= t < s1["start"] + s1["dur"] + 0.3:
        spoken = {0, 1}
    sl = sents[-1]
    if sl["text"].lower().startswith("rest") and sl["start"] <= t < sl["start"] + sl["dur"] + 0.3:
        spoken = {2}
    ry = 30
    for i, (lab, val) in enumerate(rows):
        hl = spoken is not None and i in spoken
        if hl:
            d.rounded_rectangle((26, ry - 8, cw - 18, ry + 140), 20, fill=(235, 40, 50, 210))
        d.text((44, ry), lab, font=font(FONT_BOLD, 34), fill=(255, 255, 255, 210))
        size = 92
        while text_w(d, val, font(FONT_BLACK, size)) > cw - 70:
            size -= 4
        d.text((42, ry + 36), val, font=font(FONT_BLACK, size), fill=WHITE if hl else YELLOW)
        ry += 160
    d.line((40, ry - 4, cw - 30, ry - 4), fill=(255, 255, 255, 70), width=2)
    tip_size = 34
    while text_w(d, ex["tip"], font(FONT_BLACK, tip_size)) > cw - 70:
        tip_size -= 2
    d.text((44, ry + 14), ex["tip"], font=font(FONT_BLACK, tip_size), fill=WHITE)
    base.alpha_composite(panel, (x, y))


def pill(d, xy, label, text, k):
    """Red label + white text pill sliding in from the left (k: 0..1 animation)."""
    x, y = xy
    fl, ft = font(FONT_BLACK, 50), font(FONT_BLACK, 50)
    lw = text_w(d, label, fl) + 48
    tw = text_w(d, text, ft) + 48
    xo = int(x - (1 - k) * 700)
    d.rounded_rectangle((xo, y, xo + lw + tw, y + 88), 26, fill=(12, 12, 16, 215))
    d.rounded_rectangle((xo, y, xo + lw, y + 88), 26, fill=RED)
    d.text((xo + lw / 2, y + 44), label, font=fl, fill=WHITE, anchor="mm")
    d.text((xo + lw + tw / 2, y + 44), text, font=ft, fill=YELLOW, anchor="mm")


def draw_intro(base, sc, t):
    """Hook: 'SQUATS ALONE WON'T DO IT' -> the three glute zones -> the workout list."""
    d = ImageDraw.Draw(base)
    s0, s1, s2 = sc["sents"]
    if t < s1["start"]:
        k = back_out((t - sc["start"]) / 0.3)
        size = int(122 * (0.5 + 0.5 * k))
        shadow_text(d, (W // 2, 250), "SQUATS ALONE", font(FONT_BLACK, size), stroke=8, anchor="mm")
        k2 = back_out((t - sc["start"] - 0.45) / 0.3)
        if k2 > 0:
            size2 = int(122 * (0.5 + 0.5 * k2))
            shadow_text(d, (W // 2, 395), "WON'T DO IT", font(FONT_BLACK, size2), fill=YELLOW, stroke=8,
                        anchor="mm")
        return
    if t < s2["start"]:
        k = ease_out((t - s1["start"]) / 0.3)
        shadow_text(d, (W // 2, 240 - int((1 - k) * 60)), "TRAIN ALL 3 ZONES", font(FONT_BLACK, 104),
                    stroke=7, anchor="mm")
        zones = [("LOWER", "FULLNESS", 0.28), ("UPPER", "ROUNDNESS", 0.55), ("SIDE", "WIDTH", 0.8)]
        for i, (lab, txt, frac) in enumerate(zones):
            at = s1["start"] + s1["dur"] * frac - 0.35
            ki = back_out((t - at) / 0.35)
            if ki > 0:
                pill(d, (110, 400 + i * 120), lab, txt, ki)
        return
    fp = font(FONT_BLACK, 60)
    tw = text_w(d, "THE WORKOUT", fp) + 70
    d.rounded_rectangle((W / 2 - tw / 2, 200, W / 2 + tw / 2, 296), 48, fill=RED)
    d.text((W / 2, 248), "THE WORKOUT", font=fp, fill=WHITE, anchor="mm")
    for i, e in enumerate(EXERCISES):
        ki = back_out((t - s2["start"] - 0.1 - i * 0.12) / 0.3)
        if ki <= 0:
            continue
        f = font(FONT_BLACK, 44)
        label = f"{i + 1}  {e['title']}"
        lw = text_w(d, label, f) + 60
        yy = 340 + i * 90
        xx = int(W / 2 - lw / 2 + (1 - ki) * 400)
        d.rounded_rectangle((xx, yy, xx + lw, yy + 76), 22, fill=(12, 12, 16, 210))
        d.text((xx + 30, yy + 38), label, font=f, fill=WHITE, anchor="lm")


def draw_outro(base, sc, t):
    d = ImageDraw.Draw(base)
    s_last = sc["sents"][-1]
    k = ease_out((t - sc["start"] - 0.1) / 0.4)
    panel_h = 170 + 118 * len(EXERCISES)
    panel = rounded_panel((W - 120, panel_h), fill=(12, 12, 16, 200))
    pd = ImageDraw.Draw(panel)
    pd.text((48, 40), "GLUTE DAY RECAP", font=font(FONT_BLACK, 66), fill=WHITE)
    pd.rounded_rectangle((48, 128, 200, 138), 5, fill=RED)
    for i, e in enumerate(EXERCISES):
        ki = ease_out((t - sc["start"] - 0.3 - i * 0.18) / 0.3)
        if ki <= 0:
            continue
        yy = 170 + i * 118
        pd.text((48, yy), f"{e['num']}", font=font(FONT_BLACK, 72), fill=RED)
        size = 48
        while text_w(pd, e["title"], font(FONT_BLACK, size)) > 800 and size > 30:
            size -= 2
        pd.text((120, yy + 6), e["title"], font=font(FONT_BLACK, size), fill=(255, 255, 255, int(255 * ki)))
        pd.text((120, yy + 62), f"{e['sets']} SETS  x  {e['reps']} REPS   ·   REST {e['rest']}",
                font=font(FONT_BOLD, 36), fill=(255, 214, 64, int(255 * ki)))
    yoff = int((1 - k) * -panel_h - 60)
    base.alpha_composite(panel, (60, 110 + yoff))
    if t >= s_last["start"]:
        kb = back_out((t - s_last["start"]) / 0.45)
        fp = font(FONT_BLACK, 70)
        txt = "SAVE  +  FOLLOW"
        tw = text_w(d, txt, fp) + 100
        bw, bh = int(tw * kb), int(124 * kb)
        if bw > 10:
            cy = 1120
            d.rounded_rectangle((W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2), bh // 2, fill=RED)
            if kb > 0.7:
                d.text((W / 2, cy), txt, font=fp, fill=WHITE, anchor="mm")


# ------------------------------------------------------------------ frame
TL = None


def shot_at(sc, t):
    for sh in sc["shots"]:
        if sh["start"] <= t < sh["end"]:
            return sh
    return sc["shots"][-1]


def render_frame(fi):
    t = fi / FPS
    sc_i = next((i for i, s in enumerate(TL["scenes"]) if s["start"] <= t < s["end"]), len(TL["scenes"]) - 1)
    sc = TL["scenes"][sc_i]
    spec = SCENES[sc_i]
    shot = shot_at(sc, t)
    bg = frame_bg(shot, t, spec["speed"])
    # flash on scene changes
    since = t - sc["start"]
    if sc_i > 0 and since < 0.18:
        bg = bg + (1 - since / 0.18) * 0.55 * (255 - bg)
    base = Image.fromarray(cv2.cvtColor(bg.astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
    base.alpha_composite(gradient())
    if "num" in spec:
        draw_header(base, spec, t, sc["start"])
        side = shot["side"] or "right"
        draw_card(base, spec, t, sc["sents"][1]["start"] - 0.1, side, sc["sents"], shot["card_y"])
    elif spec["id"] == "intro":
        draw_intro(base, sc, t)
    else:
        draw_outro(base, sc, t)
    hot = frozenset(spec["hot"])
    for s in sc["sents"]:
        for c in s["caps"]:
            if c["start"] <= t < c["end"]:
                draw_caption(base, c, hot, t)
    # fade out at the very end
    total = TL["total"]
    arr = np.asarray(base.convert("RGB"))
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
            times = []
            for s in tl["scenes"]:
                times += [s["start"] + 0.6] + [sh["start"] + 0.5 for sh in s["shots"]] + [s["end"] - 0.3]
        for tt in times:
            fi = int(tt * FPS)
            img = np.frombuffer(render_frame(fi), np.uint8).reshape(H, W, 3)
            Image.fromarray(img).save(os.path.join(out, f"f_{tt:06.2f}.jpg"), quality=85)
        print("previews ->", out)
        return
    out = os.path.join(BUILD, "video_silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=init_worker, initargs=(tl,)) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(nframes), chunksize=8)):
            ff.stdin.write(buf)
            if i % 150 == 0:
                print(f"  frame {i}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
