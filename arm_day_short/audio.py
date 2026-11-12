"""Soundtrack: original 132 BPM beat (lighter under the 3.6 s hook) + whoosh/impact SFX, ducked
under the voice. See vidkit/audio.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.audio import mix  # noqa: E402

mix(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"), bpm=132, light_until=3.6, voice="scenes")
