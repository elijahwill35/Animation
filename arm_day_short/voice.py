"""Voiceover: one Piper TTS clip per scene (en-us-ryan-high, slightly faster read), cached.
See vidkit/voice.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit import voice  # noqa: E402
from script import SCENES  # noqa: E402

voice.synth([(sc["id"], sc["vo"]) for sc in SCENES],
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "vo"),
            length_scale=0.86, sentence_silence=0.12)
