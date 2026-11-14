"""Narration, on-screen cards and shot plan for the glute growth & hamstrings video (~45 s).

Source clip (assets/source.mp4, 720x1280 vertical, 24 fps, 10 s) has five 2-second shots:
  thrust   0.00-1.96  barbell hip thrusts
  rdl      1.96-4.08  Romanian deadlifts
  kick     4.08-5.96  cable glute kickbacks
  curl     5.96-8.00  seated leg curls
  abd      8.00-10.0  seated hip abductions

Structure: hook (promises the full workout at the end) -> five quick exercise scenes ->
a full-workout card held on screen long enough to screenshot.
"""

TITLE = "GLUTE GROWTH & HAMSTRINGS"
FOCUS = "GLUTE THICKNESS · LOWER GLUTES · HAMSTRINGS"

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "thrust": (1, 45),
    "rdl": (49, 96),
    "kick": (100, 141),
    "curl": (145, 190),
    "abd": (194, 238),
}

# shot = (segment, zoom, cx, cy, card_side[, card_y])
SCENES = [
    dict(
        id="intro",
        lines=[
            "Want thicker glutes and stronger hamstrings?",
            "Do these five exercises, and stay to the end for the full workout you can screenshot.",
        ],
        hot={"THICKER", "GLUTES", "STRONGER", "HAMSTRINGS?", "FIVE", "EXERCISES,", "END", "FULL",
             "WORKOUT", "SCREENSHOT."},
        shots=[("thrust", 1.3, 0.45, 0.45, None), ("kick", 1.2, 0.4, 0.55, None),
               ("rdl", 1.2, 0.5, 0.5, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="BARBELL HIP THRUSTS", muscle="GLUTE THICKNESS",
        sets="4", reps="8-12", rest="2 MIN", tip="SQUEEZE AT TOP",
        lines=["One. Barbell hip thrusts.", "Four sets of eight to twelve.", "Squeeze hard at the top."],
        hot={"BARBELL", "HIP", "THRUSTS.", "FOUR", "SETS", "EIGHT", "TWELVE.", "SQUEEZE", "HARD", "TOP."},
        shots=[("thrust", 1.0, 0.5, 0.5, "right", 400)],
        speed=0.65,
    ),
    dict(
        id="ex2",
        num=2, title="ROMANIAN DEADLIFTS", muscle="LOWER GLUTES & HAMSTRINGS",
        sets="3", reps="10-12", rest="2 MIN", tip="HIPS BACK",
        lines=["Two. Romanian deadlifts.", "Three sets of ten to twelve.", "Hips back, and feel the stretch."],
        hot={"ROMANIAN", "DEADLIFTS.", "THREE", "SETS", "TEN", "TWELVE.", "HIPS", "BACK,", "STRETCH."},
        shots=[("rdl", 1.0, 0.5, 0.5, "right", 600)],
        speed=0.65,
    ),
    dict(
        id="ex3",
        num=3, title="CABLE GLUTE KICKBACKS", muscle="GLUTES",
        sets="3", reps="12-15", rest="60s", tip="NO SWINGING",
        lines=["Three. Cable glute kickbacks.", "Three sets of twelve to fifteen.", "Kick back, and don't swing."],
        hot={"CABLE", "GLUTE", "KICKBACKS.", "THREE", "SETS", "TWELVE", "FIFTEEN.", "KICK", "BACK,",
             "SWING."},
        shots=[("kick", 1.0, 0.5, 0.5, "left", 420)],
        speed=0.65,
    ),
    dict(
        id="ex4",
        num=4, title="SEATED LEG CURLS", muscle="HAMSTRINGS",
        sets="3", reps="12-15", rest="60s", tip="FULL CURL",
        lines=["Four. Seated leg curls.", "Three sets of twelve to fifteen.",
               "Curl all the way back for your hamstrings."],
        hot={"SEATED", "LEG", "CURLS.", "THREE", "SETS", "TWELVE", "FIFTEEN.", "ALL", "WAY",
             "HAMSTRINGS."},
        shots=[("curl", 1.0, 0.5, 0.5, "left", 380)],
        speed=0.65,
    ),
    dict(
        id="ex5",
        num=5, title="SEATED HIP ABDUCTIONS", muscle="SIDE GLUTES",
        sets="3", reps="15-25", rest="45s", tip="PUSH + HOLD",
        lines=["Five. Seated hip abductions.", "Three sets of fifteen to twenty five.", "Push out, and hold."],
        hot={"SEATED", "HIP", "ABDUCTIONS.", "THREE", "SETS", "FIFTEEN", "TWENTY", "FIVE.", "PUSH",
             "OUT,", "HOLD."},
        shots=[("abd", 1.0, 0.5, 0.5, "right", 380)],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "Here's the full workout.",
            "Screenshot it, save it for your next glute day, and follow for more.",
        ],
        hot={"FULL", "WORKOUT.", "SCREENSHOT", "SAVE", "GLUTE", "DAY,", "FOLLOW"},
        shots=[("thrust", 1.1, 0.5, 0.5, None)],
        speed=0.6,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
