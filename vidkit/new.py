"""Start a new narrated routine video from a source clip.

    python3 -m vidkit.new <project_dir> <source_clip> [--title="PUSH DAY"]

  * copies the clip to <project>/assets/source.<ext>
  * detects the hard cuts in the clip and writes SEGMENTS (trimmed 1-2 frames off each cut)
  * writes build/shots.jpg: one labelled still per detected shot, so every shot can be
    identified from a single image
  * scaffolds script.py (fill in the narration), render.py, voice.py, audio.py, README.md,
    .gitignore, all wired to vidkit

Then: name the segments and write the lines in script.py, `python3 -m vidkit.build <dir> --preview`,
check the frames, and run the full build.
"""
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"


def detect_cuts(path, thresh=None):
    """Frame indices where a new shot starts (hard cuts), from mean abs diff of small grey frames."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    prev, diffs, frames = None, [], []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(f, (96, 96 * f.shape[0] // f.shape[1])), cv2.COLOR_BGR2GRAY)
        g = g.astype(np.float32)
        diffs.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        prev = g
        frames.append(f)
    d = np.array(diffs)
    if thresh is None:
        med = np.median(d[1:]) if len(d) > 1 else 0
        thresh = max(12.0, med * 6)
    cuts = [0] + [i for i in range(1, len(d)) if d[i] > thresh and d[i] >= d[max(0, i - 2):i + 3].max()]
    return cuts, len(frames), fps, frames


def segments(cuts, n):
    bounds = cuts + [n]
    segs = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a < 8:
            continue
        segs.append((a + 1 if a == 0 else a + 2, b - 2))   # stay clear of blended frames at each cut
    return segs


def contact(frames, segs, out):
    thumbs = []
    for i, (a, b) in enumerate(segs):
        f = cv2.cvtColor(frames[(a + b) // 2], cv2.COLOR_BGR2RGB)
        h = 420
        w = int(f.shape[1] * h / f.shape[0])
        im = Image.fromarray(cv2.resize(f, (w, h)))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w, 54), fill=(0, 0, 0))
        d.text((10, 8), f"s{i}  {a}-{b}", font=ImageFont.truetype(FONT, 34), fill=(255, 214, 64))
        thumbs.append(im)
    cols = min(len(thumbs), 5)
    rows = (len(thumbs) + cols - 1) // cols
    W = max(t.width for t in thumbs)
    sheet = Image.new("RGB", (cols * (W + 8), rows * 428), (0, 0, 0))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * (W + 8), (i // cols) * 428))
    sheet.save(out, quality=85)


SCRIPT = '''"""Narration, on-screen cards and shot plan for the {title_lc} video.

Source clip (assets/{src}, {w}x{h}, {fps:g} fps, {dur:.1f} s). Detected shots (see build/shots.jpg):
{shot_doc}
"""

# source frame ranges (inclusive), trimmed away from each cut. Rename s0.. to what each shot shows.
SEGMENTS = {{
{segs}
}}

# shot = (segment, zoom, cx, cy, card_side[, card_y])
#   zoom: 1.0 = full frame; cx/cy: framing centre in source-normalised coords
#   card_side / card_y: where the sets/reps card sits (away from the lifter); card_y defaults to 720
# Exercise scenes: line 1 names the exercise, line 2 gives sets and reps (the card lands and lights
# up SETS/REPS), the last line starts with "Rest" (lights up REST). Intro line 3 reveals the list.
SCENES = [
    dict(
        id="intro",
        lines=[
            "{title_cap}. Hook line here.",
            "Here's a complete workout for ...",
            "N exercises, in about M minutes.",
        ],
        hot={{"HOOK"}},
        shots=[("s0", 1.2, 0.5, 0.45, None), ("s1", 1.1, 0.5, 0.5, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="EXERCISE NAME", muscle="TARGET MUSCLE",
        sets="4", reps="8-10", rest="90s", tip="FORM CUE",
        lines=[
            "Exercise one. Exercise name.",
            "Four sets of eight to ten reps.",
            "One form cue sentence.",
            "Rest ninety seconds.",
        ],
        hot={{"FOUR", "SETS", "EIGHT", "TEN"}},
        shots=[("s0", 1.0, 0.5, 0.5, "right"), ("s0", 1.35, 0.45, 0.45, "right")],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "That's N working sets.",
            "Run it once or twice a week, and add weight when the reps get easy.",
            "Save this for your next session, and follow for more.",
        ],
        hot={{"SAVE", "FOLLOW"}},
        shots=[("s0", 1.1, 0.5, 0.45, None)],
        speed=0.7,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
'''

RENDER = '''"""{title_lc} ({w_out}x{h_out}, 30 fps): the shared vidkit routine renderer.

  python3 render.py [--preview [--t=12.5 ...]]   (or: python3 -m vidkit.build {name})
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.routine import Routine  # noqa: E402
import script  # noqa: E402


class Video(Routine):
    TITLE = "{title}"
    SRC = "assets/{src}"


if __name__ == "__main__":
    Video(script, __file__).main()
'''

VOICE = '''"""Voiceover: one Piper TTS clip per sentence (en-us-ryan-high), cached. See vidkit/voice.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit import voice  # noqa: E402
from script import SCENES  # noqa: E402

voice.synth(voice.scene_lines(SCENES), os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "vo"))
'''

AUDIO = '''"""Soundtrack: original 124 BPM beat + whoosh/impact SFX, ducked under the voice. See vidkit/audio.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vidkit.audio import mix  # noqa: E402

mix(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"))
'''

README = '''# {title_cap} — narrated workout video

A vertical video (1080×1920, 30 fps, ready for YouTube Shorts) built from the clip in
`assets/{src}` with the shared `vidkit` routine renderer.

**Final video:** [`output/{name}.mp4`](../output/{name}.mp4)

## Build

```bash
python3 -m vidkit.build {name}              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build {name} --preview    # voice + still frames only, for checking layout
```
'''


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)
    proj, clip = os.path.abspath(args[0]), args[1]
    name = os.path.basename(proj.rstrip("/"))
    title = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--title=")),
                 name.replace("_routine", "").replace("_", " ").upper())
    os.makedirs(os.path.join(proj, "assets"), exist_ok=True)
    os.makedirs(os.path.join(proj, "build"), exist_ok=True)
    src = "source" + os.path.splitext(clip)[1].lower()
    dst = os.path.join(proj, "assets", src)
    if os.path.abspath(clip) != dst:
        shutil.copyfile(clip, dst)

    cuts, n, fps, frames = detect_cuts(dst)
    segs = segments(cuts, n)
    h, w = frames[0].shape[:2]
    contact(frames, segs, os.path.join(proj, "build", "shots.jpg"))
    shot_doc = "\n".join(f"  s{i:<3d} {a / fps:5.2f}-{(b + 1) / fps:5.2f}  frames {a}-{b}  (what is it?)"
                         for i, (a, b) in enumerate(segs))
    seg_lines = "\n".join(f'    "s{i}": ({a}, {b}),' for i, (a, b) in enumerate(segs))
    fmt = dict(name=name, title=title, title_lc=title.lower(), title_cap=title.title(), src=src, w=w, h=h,
               fps=fps, dur=n / fps, shot_doc=shot_doc, segs=seg_lines, w_out=1080, h_out=1920)
    files = {"script.py": SCRIPT, "render.py": RENDER, "voice.py": VOICE, "audio.py": AUDIO,
             "README.md": README, ".gitignore": "build/\n"}
    for fn, tpl in files.items():
        path = os.path.join(proj, fn)
        if os.path.exists(path):
            print("  keep existing", fn)
            continue
        with open(path, "w") as f:
            f.write(tpl.format(**fmt) if fn != ".gitignore" else tpl)
    print(f"new project {name}: {len(segs)} shots detected in {n} frames @ {fps:g} fps ({w}x{h})")
    print(shot_doc)
    print(f"shot stills -> {os.path.relpath(os.path.join(proj, 'build', 'shots.jpg'))}")
    if w > h:
        print("note: landscape source; see chest_back_routine for the landscape layout and the 9:16 re-frame.")


if __name__ == "__main__":
    main()
