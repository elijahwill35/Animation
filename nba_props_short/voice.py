"""Voiceover: one Piper TTS clip per sentence (en-us-ryan-high), cached; names use their phonetic
spoken form from script.py. See vidkit/voice.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit import voice  # noqa: E402
from script import SCENES, spoken  # noqa: E402

voice.synth(voice.scene_lines(SCENES, spoken),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "vo"))
