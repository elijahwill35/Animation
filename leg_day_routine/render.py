"""Leg day routine (1080x1920, 30 fps): the shared vidkit routine renderer with leg-day titles.

  python3 render.py [--preview [--t=12.5 ...]]   (or: python3 -m vidkit.build leg_day_routine)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.routine import Routine  # noqa: E402
import script  # noqa: E402


class Video(Routine):
    TITLE = "LEG DAY"
    SRC = "assets/source.mov"


if __name__ == "__main__":
    Video(script, __file__).main()
