"""Soundtrack: original 124 BPM beat + whoosh/impact SFX, ducked under the voice. See vidkit/audio.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.audio import mix  # noqa: E402

mix(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"))
