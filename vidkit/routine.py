"""The narrated workout-routine renderer, shared by every *_routine project.

A project is a `script.py` (SEGMENTS, SCENES) plus a tiny `render.py`:

    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from vidkit.routine import Routine
    import script

    class Video(Routine):
        TITLE = "LEG DAY"
        SRC = "assets/source.mov"

    if __name__ == "__main__":
        Video(script, __file__).main()

Each exercise shot is slowed down and ping-pong looped (with frame blending) so the lifter keeps
repping for as long as the narration needs, re-framed with punch-ins and a slow push, and overlaid
with: exercise header + progress, a sets/reps/rest card beside the lifter, and word-chunk captions
synced to the voiceover. Every layout number is a class attribute, and every drawing step is a
method, so a project overrides only what it changes (see glute_day_routine for a custom hook intro,
chest_back_routine for landscape and a 9:16 re-frame).

  python3 render.py                    -> build/video_silent.mp4 + build/timeline.json
  python3 render.py --preview [--t=X]  -> still frames in build/preview/
"""
import json
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time
import wave
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
RED = (235, 40, 50)
YELLOW = (255, 214, 64)
WHITE = (255, 255, 255)


# ------------------------------------------------------------------ helpers
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


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back_out(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


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


def rounded_panel(size, radius=34, fill=(12, 12, 16, 185)):
    p = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill)
    return p


def pill(d, xy, label, text, k, size=50):
    """Red label + yellow text pill sliding in from the left (k: 0..1 animation)."""
    x, y = xy
    f = font(FONT_BLACK, size)
    lw = text_w(d, label, f) + 48
    tw = text_w(d, text, f) + 48
    xo = int(x - (1 - k) * 700)
    d.rounded_rectangle((xo, y, xo + lw + tw, y + 88), 26, fill=(12, 12, 16, 215))
    d.rounded_rectangle((xo, y, xo + lw, y + 88), 26, fill=RED)
    d.text((xo + lw / 2, y + 44), label, font=f, fill=WHITE, anchor="mm")
    d.text((xo + lw + tw / 2, y + 44), text, font=f, fill=YELLOW, anchor="mm")


@lru_cache(maxsize=None)
def _caption_img(words, hot, size):
    f = font(FONT_BLACK, size)
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


# ------------------------------------------------------------------ engine
class Routine:
    # identity
    TITLE = "WORKOUT"
    RECAP_TITLE = None          # default: f"{TITLE} RECAP"
    INTRO_TAG = "THE ROUTINE"
    SRC = "assets/source.mp4"
    OUT_NAME = "video_silent.mp4"
    PREVIEW_DIR = "preview"
    WRITE_TIMELINE = True       # False for a second cut that reuses mix.wav
    PREGRADE = True             # grade the source once at load (False: grade every output frame)

    # format
    W, H, FPS = 1080, 1920, 30
    SRC_FPS = 24
    CRF, PRESET = 15, "veryfast"   # same SSIM/PSNR as medium@19, ~1.8x faster encode (files ~1.4x larger)

    # pacing (seconds)
    GAP = 0.30                  # pause between sentences
    LEAD = {"intro": 0.25, "outro": 0.35}
    TAIL = {"intro": 0.5, "outro": 2.2}
    EX_LEAD, EX_TAIL = 0.45, 1.1

    # look
    GRAD_TOP = 520              # top darkening height
    GRAD_BOT = (1250, 670)      # bottom darkening start, height
    CAPTION_SIZE, CAPTION_Y, CAPTION_MARGIN = 92, 1600, 80
    HEADER_SIZE = 104
    CARD_W, CARD_H, CARD_X, CARD_Y, CARD_ROW = 330, 560, 44, 720, 160
    INTRO_TITLE_SIZE = 190
    INTRO_LIST_Y, INTRO_LIST_STEP, INTRO_LIST_STAGGER = 460, 92, 0.25
    RECAP_TITLE_SIZE = 66
    RECAP_Y0, RECAP_ROW, RECAP_STAGGER, RECAP_TITLE_W = 170, 118, 0.18, 800
    RECAP_PANEL_H = None        # default: fits the exercise count
    CTA_TEXT, CTA_Y = "SAVE  +  FOLLOW", 1120

    def __init__(self, script, file):
        self.script = script
        self.SCENES = script.SCENES
        self.SEGMENTS = script.SEGMENTS
        self.EXERCISES = [s for s in self.SCENES if "num" in s]
        self.HERE = os.path.dirname(os.path.abspath(file))
        self.BUILD = os.path.join(self.HERE, "build")
        self.frames = None
        self.tl = None

    # -------------------------------------------------------------- timeline
    def shot_list(self, sc):
        return sc["shots"]

    def build_timeline(self):
        t = 0.0
        scenes, cuts, slams, lines = [], [], [], []
        for sc in self.SCENES:
            is_ex = "num" in sc
            lead = self.EX_LEAD if is_ex else self.LEAD[sc["id"]]
            tail = self.EX_TAIL if is_ex else self.TAIL[sc["id"]]
            start = t
            t += lead
            sents = []
            for i, line in enumerate(sc["lines"]):
                key = f"{sc['id']}_{i}"
                d = wav_dur(os.path.join(self.BUILD, "vo", key + ".wav"))
                chunks = chunk_words(line.split())
                weights = [sum(len(w) for w in c) + 2 for c in chunks]
                tot = sum(weights)
                ct, caps = t, []
                for c, wgt in zip(chunks, weights):
                    cd = d * wgt / tot
                    caps.append(dict(words=c, start=ct, end=ct + cd))
                    ct += cd
                caps[-1]["end"] = t + d + self.GAP * 0.8  # hold last chunk through the pause
                sents.append(dict(key=key, start=t, dur=d, caps=caps, text=line))
                lines.append(dict(key=key, start=t))
                t += d + self.GAP
            t += tail - self.GAP
            end = t
            specs = self.shot_list(sc)
            n = len(specs)
            shots = []
            for k, sh in enumerate(specs):
                s0 = start + (end - start) * k / n
                s1 = start + (end - start) * (k + 1) / n
                shots.append(dict(seg=sh[0], zoom=sh[1], cx=sh[2], cy=sh[3],
                                  side=sh[4] if len(sh) > 4 else None,
                                  card_y=sh[5] if len(sh) > 5 else self.CARD_Y,
                                  start=s0, end=s1, phase=(k * 0.37 + len(scenes) * 0.21) % 1))
                if k > 0:
                    cuts.append(s0)
            cuts.append(start)
            slams.append(start)
            if is_ex:
                slams.append(sents[1]["start"])  # sets/reps card lands
            scenes.append(dict(id=sc["id"], start=start, end=end, sents=sents, shots=shots))
        return dict(total=t, scenes=scenes, cuts=sorted(set(cuts))[1:], slams=slams, lines=lines)

    # -------------------------------------------------------------- footage
    def load_frames(self):
        cap = cv2.VideoCapture(os.path.join(self.HERE, self.SRC))
        out = []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            out.append(f)
        frames = np.stack(out)
        if self.PREGRADE:   # grading per pixel commutes with the (linear) warp: do it once, at source res
            lut = np.stack([np.floor(np.clip((np.arange(256) - 128) * 1.06 + 128 + off, 0, 255))
                            for off in (-4, 0, 6)], -1).astype(np.uint8)[None]
            for i in range(len(frames)):
                frames[i] = cv2.LUT(frames[i], lut)
        return frames

    def src_frame(self, seg, t, speed, phase):
        a, b = self.SEGMENTS[seg]
        L = b - a
        pos = t * self.SRC_FPS * speed + phase * 2 * L
        m = pos % (2 * L)
        p = m if m <= L else 2 * L - m
        i0 = int(math.floor(p))
        fr = p - i0
        i1 = min(i0 + 1, L)
        if fr < 1e-3:
            return self.frames[a + i0].astype(np.float32)
        return cv2.addWeighted(self.frames[a + i0], 1 - fr, self.frames[a + i1], fr, 0, dtype=cv2.CV_32F)

    def frame_bg(self, shot, t, speed):
        W, H = self.W, self.H
        lt = t - shot["start"]
        dur = shot["end"] - shot["start"]
        img = self.src_frame(shot["seg"], lt, speed, shot["phase"])
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
        return out if self.PREGRADE else self.grade(out)

    @staticmethod
    def grade(out):
        """Light grade: a touch of contrast + warmth (in place, float32 BGR)."""
        out -= 128
        out *= 1.06
        out += np.float32([124, 128, 134])
        return np.clip(out, 0, 255, out=out)

    # -------------------------------------------------------------- overlays
    @lru_cache(maxsize=None)
    def gradient(self):
        W, H = self.W, self.H
        g = np.zeros((H, W, 4), np.uint8)
        y = np.arange(H)[:, None]
        top = np.clip(1 - y / self.GRAD_TOP, 0, 1) ** 1.6 * 170
        b0, bh = self.GRAD_BOT
        bot = np.clip((y - b0) / bh, 0, 1) ** 1.4 * 200
        g[..., 3] = np.maximum(top, bot).astype(np.uint8).repeat(W, 1)
        return Image.fromarray(g, "RGBA")

    def draw_caption(self, base, cap, hot, t):
        words = tuple(w.upper() for w in cap["words"])
        img = _caption_img(words, hot, self.CAPTION_SIZE)
        k = back_out((t - cap["start"]) / 0.16)
        sc = 0.75 + 0.25 * k
        max_w = self.W - self.CAPTION_MARGIN
        if img.width * sc > max_w:
            sc *= max_w / (img.width * sc)
        im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)
        base.alpha_composite(im, (int(self.W / 2 - im.width / 2), int(self.CAPTION_Y - im.height / 2)))

    def draw_header(self, base, ex, t, start):
        W = self.W
        d = ImageDraw.Draw(base)
        k = ease_out((t - start) / 0.35)
        off = int((1 - k) * -200)
        label = f"EXERCISE {ex['num']} OF {len(self.EXERCISES)}"
        fp = font(FONT_BLACK, 38)
        pw = text_w(d, label, fp) + 56
        d.rounded_rectangle((60, 92 + off, 60 + pw, 150 + off), 29, fill=RED)
        d.text((60 + 28, 121 + off), label, font=fp, fill=WHITE, anchor="lm")
        for i in range(len(self.EXERCISES)):     # progress bar
            x0 = 60 + pw + 30 + i * 70
            col = WHITE if i + 1 == ex["num"] else (255, 255, 255, 90)
            if i + 1 < ex["num"]:
                col = RED
            d.rounded_rectangle((x0, 114 + off, x0 + 56, 128 + off), 7, fill=col)
        size = self.HEADER_SIZE
        while text_w(d, ex["title"], font(FONT_BLACK, size), 6) > W - 120 and size > 50:
            size -= 2
        shadow_text(d, (60, 172 + off), ex["title"], font(FONT_BLACK, size), stroke=6)
        d.text((64, 172 + size + 24 + off), "TARGET  ·  " + ex["muscle"], font=font(FONT_BOLD, 40),
               fill=(255, 255, 255, 230), stroke_width=3, stroke_fill=(0, 0, 0))

    def spoken_rows(self, sents, t):
        """Highlight sets+reps while sentence 1 is spoken, rest while a 'Rest ...' line is."""
        s1 = sents[1]
        spoken = None
        if s1["start"] <= t < s1["start"] + s1["dur"] + 0.3:
            spoken = {0, 1}
        sl = sents[-1]
        if sl["text"].lower().startswith("rest") and sl["start"] <= t < sl["start"] + sl["dur"] + 0.3:
            spoken = {2}
        return spoken

    def draw_card(self, base, ex, t, card_start, shot, sents):
        if t < card_start:
            return
        side = shot["side"] or "right"
        k = back_out((t - card_start) / 0.4)
        cw = self.CARD_W
        x_in = self.CARD_X if side == "left" else self.W - cw - self.CARD_X
        x_off = -cw - 80 if side == "left" else cw + 80
        x = int(x_in + x_off * (1 - k))
        spoken = self.spoken_rows(sents, t)
        base.alpha_composite(self.card_panel(ex["id"], tuple(sorted(spoken or ()))), (x, shot["card_y"]))

    @lru_cache(maxsize=None)
    def card_panel(self, ex_id, spoken):
        ex = next(e for e in self.EXERCISES if e["id"] == ex_id)
        cw, chh = self.CARD_W, self.CARD_H
        panel = rounded_panel((cw, chh))
        d = ImageDraw.Draw(panel)
        d.rounded_rectangle((0, 0, 14, chh - 1), 7, fill=RED)
        rows = [("SETS", ex["sets"]), ("REPS", ex["reps"]), ("REST", ex["rest"])]
        ry = 30
        for i, (lab, val) in enumerate(rows):
            hl = i in spoken
            if hl:
                d.rounded_rectangle((26, ry - 8, cw - 18, ry + 140), 20, fill=(235, 40, 50, 210))
            d.text((44, ry), lab, font=font(FONT_BOLD, 34), fill=(255, 255, 255, 210))
            size = 92
            while text_w(d, val, font(FONT_BLACK, size)) > cw - 70:
                size -= 4
            d.text((42, ry + 36), val, font=font(FONT_BLACK, size), fill=WHITE if hl else YELLOW)
            ry += self.CARD_ROW
        d.line((40, ry - 4, cw - 30, ry - 4), fill=(255, 255, 255, 70), width=2)
        tip_size = 34
        while text_w(d, ex["tip"], font(FONT_BLACK, tip_size)) > cw - 70:
            tip_size -= 2
        d.text((44, ry + 14), ex["tip"], font=font(FONT_BLACK, tip_size), fill=WHITE)
        return panel

    def draw_intro(self, base, sc, t):
        W = self.W
        d = ImageDraw.Draw(base)
        k = back_out((t - sc["start"] - 0.05) / 0.4)
        size = int(self.INTRO_TITLE_SIZE * (0.6 + 0.4 * k))
        shadow_text(d, (W // 2, 210), self.TITLE, font(FONT_BLACK, size), fill=WHITE, stroke=8, anchor="mm")
        k2 = ease_out((t - sc["start"] - 0.3) / 0.35)
        if k2 > 0:
            fp = font(FONT_BLACK, 52)
            tw = text_w(d, self.INTRO_TAG, fp) + 60
            yy = 330 + int((1 - k2) * 40)
            d.rounded_rectangle((W / 2 - tw / 2, yy, W / 2 + tw / 2, yy + 78), 39, fill=RED)
            d.text((W / 2, yy + 39), self.INTRO_TAG, font=fp, fill=WHITE, anchor="mm")
        s2 = sc["sents"][2]
        if t >= s2["start"]:
            for i, e in enumerate(self.EXERCISES):
                ki = back_out((t - s2["start"] - i * self.INTRO_LIST_STAGGER) / 0.35)
                if ki <= 0:
                    continue
                fp = font(FONT_BLACK, 44)
                label = f"{i + 1}  {e['title']}"
                tw = text_w(d, label, fp) + 60
                yy = self.INTRO_LIST_Y + i * self.INTRO_LIST_STEP
                xx = int(W / 2 - tw / 2 + (1 - ki) * 300)
                d.rounded_rectangle((xx, yy, xx + tw, yy + 78), 22, fill=(12, 12, 16, 200))
                d.text((xx + 30, yy + 39), label, font=fp, fill=WHITE, anchor="lm")

    def recap_panel(self, sc, t, pw):
        n = len(self.EXERCISES)
        panel_h = self.RECAP_PANEL_H or (self.RECAP_Y0 + self.RECAP_ROW * n)
        panel = rounded_panel((pw, panel_h), fill=(12, 12, 16, 200))
        pd = ImageDraw.Draw(panel)
        title = self.RECAP_TITLE or f"{self.TITLE} RECAP"
        pd.text((48, 40), title, font=font(FONT_BLACK, self.RECAP_TITLE_SIZE), fill=WHITE)
        pd.rounded_rectangle((48, 128, 200, 138), 5, fill=RED)
        for i, e in enumerate(self.EXERCISES):
            ki = ease_out((t - sc["start"] - 0.3 - i * self.RECAP_STAGGER) / 0.3)
            if ki <= 0:
                continue
            yy = self.RECAP_Y0 + i * self.RECAP_ROW
            pd.text((48, yy), f"{e['num']}", font=font(FONT_BLACK, 72), fill=RED)
            size = 48
            while text_w(pd, e["title"], font(FONT_BLACK, size)) > self.RECAP_TITLE_W and size > 30:
                size -= 2
            pd.text((120, yy + 6), e["title"], font=font(FONT_BLACK, size), fill=(255, 255, 255, int(255 * ki)))
            pd.text((120, yy + 62), f"{e['sets']} SETS  x  {e['reps']} REPS   ·   REST {e['rest']}",
                    font=font(FONT_BOLD, 36), fill=(255, 214, 64, int(255 * ki)))
        return panel

    def draw_cta(self, base, sc, t, cx, cy):
        s_last = sc["sents"][-1]
        if t < s_last["start"]:
            return
        d = ImageDraw.Draw(base)
        kb = back_out((t - s_last["start"]) / 0.45)
        fp = font(FONT_BLACK, 70)
        tw = text_w(d, self.CTA_TEXT, fp) + 100
        bw, bh = int(tw * kb), int(124 * kb)
        if bw > 10:
            d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), bh // 2, fill=RED)
            if kb > 0.7:
                d.text((cx, cy), self.CTA_TEXT, font=fp, fill=WHITE, anchor="mm")

    def draw_outro(self, base, sc, t):
        k = ease_out((t - sc["start"] - 0.1) / 0.4)
        panel = self.recap_panel(sc, t, self.W - 120)
        yoff = int((1 - k) * -panel.height - 60)
        base.alpha_composite(panel, (60, 110 + yoff))
        self.draw_cta(base, sc, t, self.W / 2, self.CTA_Y)

    # -------------------------------------------------------------- frame
    def render_frame(self, fi):
        tl = self.tl
        t = fi / self.FPS
        sc_i = next((i for i, s in enumerate(tl["scenes"]) if s["start"] <= t < s["end"]), len(tl["scenes"]) - 1)
        sc = tl["scenes"][sc_i]
        spec = self.SCENES[sc_i]
        shot = next((sh for sh in sc["shots"] if sh["start"] <= t < sh["end"]), sc["shots"][-1])
        bg = self.frame_bg(shot, t, spec["speed"])
        since = t - sc["start"]
        if sc_i > 0 and since < 0.18:          # flash on scene changes
            bg = bg + (1 - since / 0.18) * 0.55 * (255 - bg)
        base = Image.fromarray(cv2.cvtColor(bg.astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
        base.alpha_composite(self.gradient())
        if "num" in spec:
            self.draw_header(base, spec, t, sc["start"])
            self.draw_card(base, spec, t, sc["sents"][1]["start"] - 0.1, shot, sc["sents"])
        elif spec["id"] == "intro":
            self.draw_intro(base, sc, t)
        else:
            self.draw_outro(base, sc, t)
        hot = frozenset(spec["hot"])
        for s in sc["sents"]:
            for c in s["caps"]:
                if c["start"] <= t < c["end"]:
                    self.draw_caption(base, c, hot, t)
        arr = np.asarray(base.convert("RGB"))
        total = tl["total"]
        if t > total - 0.5:                     # fade out at the very end
            arr = (arr * max(0.0, (total - t) / 0.5)).astype(np.uint8)
        return arr.tobytes()

    # -------------------------------------------------------------- run
    def prepare(self):
        self.tl = self.build_timeline()
        self.frames = self.load_frames()

    def preview(self, times=None):
        out = os.path.join(self.BUILD, self.PREVIEW_DIR)
        os.makedirs(out, exist_ok=True)
        if not times:
            times = []
            for s in self.tl["scenes"]:
                times += [s["start"] + 0.6] + [sh["start"] + 0.5 for sh in s["shots"]] + [s["end"] - 0.3]
        for tt in times:
            img = np.frombuffer(self.render_frame(int(tt * self.FPS)), np.uint8).reshape(self.H, self.W, 3)
            Image.fromarray(img).save(os.path.join(out, f"f_{tt:06.2f}.jpg"), quality=85)
        print(f"previews ({len(times)}) ->", out)

    def render(self):
        nframes = int(round(self.tl["total"] * self.FPS))
        out = os.path.join(self.BUILD, self.OUT_NAME)
        preset, crf = (("ultrafast", 23) if os.environ.get("VIDKIT_DRAFT") else (self.PRESET, self.CRF))
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{self.W}x{self.H}", "-r", str(self.FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                               "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        global _ENGINE
        _ENGINE = self                           # inherited by forked workers (frames shared copy-on-write)
        t0 = time.time()
        with mp.get_context("fork").Pool(os.cpu_count()) as pool:
            for i, buf in enumerate(pool.imap(_render, range(nframes), chunksize=8)):
                ff.stdin.write(buf)
                if i % 300 == 0:
                    print(f"  frame {i}/{nframes}", flush=True)
        ff.stdin.close()
        ff.wait()
        dt = time.time() - t0
        print(f"render: wrote {out} ({nframes} frames in {dt:.0f}s, {nframes / dt:.1f} fps)")

    def main(self, argv=None):
        argv = sys.argv[1:] if argv is None else argv
        self.prepare()
        if self.WRITE_TIMELINE:
            with open(os.path.join(self.BUILD, "timeline.json"), "w") as f:
                json.dump(self.tl, f, indent=1)
        print(f"timeline: total {self.tl['total']:.2f}s  " +
              "  ".join(f"{s['id']}@{s['start']:.1f}" for s in self.tl["scenes"]))
        if "--preview" in argv:
            self.preview([float(a.split("=")[1]) for a in argv if a.startswith("--t=")])
        else:
            self.render()


_ENGINE = None


def _render(fi):
    return _ENGINE.render_frame(fi)
