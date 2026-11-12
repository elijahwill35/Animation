"""Vertical YouTube Shorts cut (1080x1920, 30 fps) of the chest & back routine.

Same timeline, voice and music as render.py (landscape): run render.py + audio first. The
landscape source is re-framed per shot (SHORT_SHOTS in script.py); wherever a wide shot doesn't
fill the 9:16 frame, a blurred, darkened copy of the same footage fills the rest. The sets/reps
card becomes a strip directly under the lifter.

  python3 render_short.py            -> build/short_silent.mp4 (reuses build/mix.wav)
  python3 render_short.py --preview  -> still frames in build/preview_short/
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import ImageDraw  # noqa: E402

from vidkit.routine import (FONT_BLACK, FONT_BOLD, RED, WHITE, YELLOW, Routine, back_out,  # noqa: E402
                            ease_out, font, rounded_panel, text_w)
import script  # noqa: E402


class Short(Routine):
    TITLE = "CHEST & BACK"
    INTRO_TITLE_SIZE = 122
    RECAP_TITLE_SIZE = 62
    OUT_NAME = "short_silent.mp4"
    PREVIEW_DIR = "preview_short"
    WRITE_TIMELINE = False
    PREGRADE = False   # the darkened blurred backdrop is graded after darkening, as before
    VIDEO_CY = 880  # where the framing centre lands on screen (between header and strip)

    def shot_list(self, sc):
        return script.SHORT_SHOTS[sc["id"]]

    def frame_bg(self, shot, t, speed):
        W, H = self.W, self.H
        lt = t - shot["start"]
        dur = shot["end"] - shot["start"]
        img = self.src_frame(shot["seg"], lt, speed, shot["phase"])
        sh, sw = img.shape[:2]
        punch = 1 + 0.07 * (1 - ease_out(lt / 0.25))
        push = 1 + 0.05 * (lt / max(dur, 1e-3))
        s = shot["zoom"] * punch * push
        cx, cy = shot["cx"] * sw, shot["cy"] * sh
        tx, ty = W / 2 - cx * s, self.VIDEO_CY - cy * s
        tx = min(0, max(W - sw * s, tx))
        if sh * s >= H:
            ty = min(0, max(H - sh * s, ty))
        M = np.float32([[s, 0, tx], [0, s, ty]])
        fg = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if sh * s >= H:
            return self.grade(fg)
        # blurred backdrop: cover-fill the frame, blur at low res, darken
        small = cv2.resize(img, (sw // 8, sh // 8), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 3)
        cover = H / sh * 1.1                      # cover-fill scale in full-res px
        bx = W / 2 - shot["cx"] * sw * cover
        Mb = np.float32([[cover * 8, 0, bx], [0, cover * 8, -(H * 0.05)]])
        bg = cv2.warpAffine(small, Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        bg = bg * 0.45
        y0, y1 = int(round(max(0, ty))), int(round(min(H, ty + sh * s)))
        mask = np.zeros((H, 1, 1), np.float32)
        mask[y0:y1] = 1
        for i in range(24):                       # soft 24px edges
            a_ = (i + 1) / 25
            if y0 + i < H:
                mask[y0 + i] = min(mask[y0 + i, 0, 0], a_)
            if y1 - 1 - i >= 0:
                mask[y1 - 1 - i] = min(mask[y1 - 1 - i, 0, 0], a_)
        return self.grade(fg * mask + bg * (1 - mask))

    def draw_card(self, base, ex, t, card_start, shot, sents):
        """Horizontal SETS | REPS | REST strip under the lifter, plus the form cue."""
        if t < card_start:
            return
        k = back_out((t - card_start) / 0.4)
        cw, chh = self.W - 120, 250
        panel = rounded_panel((cw, chh))
        d = ImageDraw.Draw(panel)
        d.rounded_rectangle((0, 0, cw - 1, 12), 6, fill=RED)
        rows = [("SETS", ex["sets"]), ("REPS", ex["reps"]), ("REST", ex["rest"])]
        spoken = self.spoken_rows(sents, t)
        colw = cw / 3
        for i, (lab, val) in enumerate(rows):
            x0 = int(i * colw)
            hl = spoken is not None and i in spoken
            if hl:
                d.rounded_rectangle((x0 + 14, 26, int(x0 + colw - 14), 180), 20, fill=(235, 40, 50, 210))
            cxm = x0 + colw / 2
            d.text((cxm, 56), lab, font=font(FONT_BOLD, 34), fill=(255, 255, 255, 210), anchor="mm")
            size = 88
            while text_w(d, val, font(FONT_BLACK, size)) > colw - 50:
                size -= 4
            d.text((cxm, 125), val, font=font(FONT_BLACK, size), fill=WHITE if hl else YELLOW, anchor="mm")
            if i:
                d.line((x0, 40, x0, 170), fill=(255, 255, 255, 60), width=2)
        d.text((cw / 2, 218), ex["tip"], font=font(FONT_BLACK, 36), fill=WHITE, anchor="mm")
        y = int(1290 + (1 - k) * 260)
        if y < self.H:
            base.alpha_composite(panel, (60, y))

    def prepare(self):
        super().prepare()
        ref = json.load(open(os.path.join(self.BUILD, "timeline.json")))
        assert abs(ref["total"] - self.tl["total"]) < 1e-6, \
            "run render.py first; timelines must match to reuse mix.wav"


if __name__ == "__main__":
    Short(script, __file__).main()
