"""Arm day routine (1080x1920, 30 fps): the shared vidkit routine renderer, arm-day layout.

  python3 render.py [--preview [--t=12.5 ...]]   (or: python3 -m vidkit.build arm_day_routine)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.routine import Routine  # noqa: E402
import script  # noqa: E402


class Video(Routine):
    TITLE = "ARM DAY"
    # three exercises: roomier intro list and recap
    INTRO_LIST_Y, INTRO_LIST_STEP = 470, 96
    RECAP_PANEL_H, RECAP_Y0, RECAP_ROW, RECAP_STAGGER, RECAP_TITLE_W = 600, 180, 130, 0.2, 560
    CTA_Y = 800


if __name__ == "__main__":
    Video(script, __file__).main()
