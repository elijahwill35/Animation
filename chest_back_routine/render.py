"""Chest & back routine, landscape (1920x1080, 30 fps): the shared vidkit routine renderer with a
landscape layout (titles top-left, card beside the lifter, recap slides in from the left).

  python3 render.py [--preview [--t=12.5 ...]]   (or: python3 -m vidkit.build chest_back_routine)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import ImageDraw  # noqa: E402

from vidkit.routine import (FONT_BLACK, FONT_BOLD, RED, WHITE, Routine, back_out, ease_out,  # noqa: E402
                            font, rounded_panel, shadow_text, text_w)
import script  # noqa: E402


class Video(Routine):
    TITLE = "CHEST & BACK"
    W, H = 1920, 1080
    GRAD_TOP, GRAD_BOT = 420, (700, 380)
    CAPTION_SIZE, CAPTION_Y, CAPTION_MARGIN = 84, 985, 200
    HEADER_SIZE = 96
    CARD_W, CARD_H, CARD_X, CARD_Y, CARD_ROW = 340, 540, 60, 372, 150

    def draw_intro(self, base, sc, t):
        d = ImageDraw.Draw(base)
        k = back_out((t - sc["start"] - 0.05) / 0.4)
        size = int(150 * (0.6 + 0.4 * k))
        shadow_text(d, (80, 60), self.TITLE, font(FONT_BLACK, size), fill=WHITE, stroke=8)
        k2 = ease_out((t - sc["start"] - 0.3) / 0.35)
        if k2 > 0:
            fp = font(FONT_BLACK, 50)
            tw = text_w(d, self.INTRO_TAG, fp) + 60
            yy = 240 + int((1 - k2) * 40)
            d.rounded_rectangle((84, yy, 84 + tw, yy + 76), 38, fill=RED)
            d.text((84 + tw / 2, yy + 38), self.INTRO_TAG, font=fp, fill=WHITE, anchor="mm")
        s2 = sc["sents"][2]
        if t >= s2["start"]:
            for i, e in enumerate(self.EXERCISES):
                ki = back_out((t - s2["start"] - i * 0.2) / 0.35)
                if ki <= 0:
                    continue
                fp = font(FONT_BLACK, 42)
                label = f"{i + 1}  {e['title']}"
                tw = text_w(d, label, fp) + 60
                yy = 360 + i * 84
                xx = int(84 - (1 - ki) * 400)
                d.rounded_rectangle((xx, yy, xx + tw, yy + 70), 20, fill=(12, 12, 16, 200))
                d.text((xx + 30, yy + 35), label, font=fp, fill=WHITE, anchor="lm")

    def draw_outro(self, base, sc, t):
        k = ease_out((t - sc["start"] - 0.1) / 0.4)
        pw, panel_h = 1000, 170 + 120 * len(self.EXERCISES)
        panel = rounded_panel((pw, panel_h), fill=(12, 12, 16, 200))
        pd = ImageDraw.Draw(panel)
        pd.text((48, 36), f"{self.TITLE} RECAP", font=font(FONT_BLACK, 62), fill=WHITE)
        pd.rounded_rectangle((48, 120, 200, 130), 5, fill=RED)
        for i, e in enumerate(self.EXERCISES):
            ki = ease_out((t - sc["start"] - 0.3 - i * 0.18) / 0.3)
            if ki <= 0:
                continue
            yy = 160 + i * 120
            pd.text((48, yy), f"{e['num']}", font=font(FONT_BLACK, 70), fill=RED)
            size = 46
            while text_w(pd, e["title"], font(FONT_BLACK, size)) > pw - 180 and size > 30:
                size -= 2
            pd.text((120, yy + 4), e["title"], font=font(FONT_BLACK, size), fill=(255, 255, 255, int(255 * ki)))
            pd.text((120, yy + 58), f"{e['sets']} SETS  x  {e['reps']} REPS   ·   REST {e['rest']}",
                    font=font(FONT_BOLD, 34), fill=(255, 214, 64, int(255 * ki)))
        xoff = int((1 - k) * -(pw + 100))
        base.alpha_composite(panel, (60 + xoff, 60))
        self.draw_cta(base, sc, t, 1500, 420)


if __name__ == "__main__":
    Video(script, __file__).main()
