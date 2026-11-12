"""Glute day routine (1080x1920, 30 fps): the shared vidkit routine renderer with a hook intro.

  python3 render.py [--preview [--t=12.5 ...]]   (or: python3 -m vidkit.build glute_day_routine)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.routine import (FONT_BLACK, RED, WHITE, YELLOW, Routine, back_out, ease_out, font,  # noqa: E402
                            pill, shadow_text, text_w)
from PIL import ImageDraw  # noqa: E402
import script  # noqa: E402


class Video(Routine):
    TITLE = "GLUTE DAY"
    GAP = 0.22
    TAIL = {"intro": 0.35, "outro": 1.9}
    EX_LEAD, EX_TAIL = 0.4, 0.6

    def draw_intro(self, base, sc, t):
        """Hook: 'SQUATS ALONE WON'T DO IT' -> the three glute zones -> the workout list."""
        d = ImageDraw.Draw(base)
        s0, s1, s2 = sc["sents"]
        if t < s1["start"]:
            k = back_out((t - sc["start"]) / 0.3)
            size = int(122 * (0.5 + 0.5 * k))
            shadow_text(d, (self.W // 2, 250), "SQUATS ALONE", font(FONT_BLACK, size), stroke=8, anchor="mm")
            k2 = back_out((t - sc["start"] - 0.45) / 0.3)
            if k2 > 0:
                size2 = int(122 * (0.5 + 0.5 * k2))
                shadow_text(d, (self.W // 2, 395), "WON'T DO IT", font(FONT_BLACK, size2), fill=YELLOW, stroke=8,
                            anchor="mm")
            return
        if t < s2["start"]:
            k = ease_out((t - s1["start"]) / 0.3)
            shadow_text(d, (self.W // 2, 240 - int((1 - k) * 60)), "TRAIN ALL 3 ZONES", font(FONT_BLACK, 104),
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
        d.rounded_rectangle((self.W / 2 - tw / 2, 200, self.W / 2 + tw / 2, 296), 48, fill=RED)
        d.text((self.W / 2, 248), "THE WORKOUT", font=fp, fill=WHITE, anchor="mm")
        for i, e in enumerate(self.EXERCISES):
            ki = back_out((t - s2["start"] - 0.1 - i * 0.12) / 0.3)
            if ki <= 0:
                continue
            f = font(FONT_BLACK, 44)
            label = f"{i + 1}  {e['title']}"
            lw = text_w(d, label, f) + 60
            yy = 340 + i * 90
            xx = int(self.W / 2 - lw / 2 + (1 - ki) * 400)
            d.rounded_rectangle((xx, yy, xx + lw, yy + 76), 22, fill=(12, 12, 16, 210))
            d.text((xx + 30, yy + 38), label, font=f, fill=WHITE, anchor="lm")


if __name__ == "__main__":
    Video(script, __file__).main()
