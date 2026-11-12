"""Narration, on-screen cards and shot plan for the leg day routine video.

Source clip (assets/source.mov, 720x1280 vertical, 24 fps, 10 s) has five 2-second shots:
  squat      0.00-1.96  barbell back squats, side view
  split      1.96-4.00  dumbbell Bulgarian split squats
  ext        4.00-5.96  leg extensions
  curl       5.96-8.00  lying leg curls
  calf       8.00-10.0  standing barbell calf raises
"""

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "squat": (1, 45),
    "split": (50, 94),
    "ext": (98, 141),
    "curl": (145, 190),
    "calf": (194, 238),
}

# shot = (segment, zoom, cx, cy, card_side[, card_y])
#   zoom: 1.0 = full frame; cx/cy: framing centre in source-normalised coords
#   card_side / card_y: where the sets/reps card sits (away from the lifter); card_y defaults to 720
SCENES = [
    dict(
        id="intro",
        lines=[
            "Leg day. Don't skip it.",
            "Here's a complete leg workout for your quads, hamstrings, glutes and calves.",
            "Five exercises, in about fifty minutes.",
        ],
        hot={"LEG", "DAY.", "SKIP", "QUADS,", "HAMSTRINGS,", "GLUTES", "CALVES.", "FIVE",
             "EXERCISES,", "FIFTY"},
        shots=[("squat", 1.3, 0.5, 0.4, None), ("split", 1.15, 0.5, 0.5, None),
               ("curl", 1.1, 0.55, 0.5, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="BARBELL BACK SQUATS", muscle="QUADS & GLUTES",
        sets="4", reps="6-8", rest="2 MIN", tip="BRACE + DEPTH",
        lines=[
            "Exercise one. Barbell back squats.",
            "Four sets of six to eight reps.",
            "Brace your core, sit down until your thighs hit parallel, and drive up through your whole foot.",
            "Rest two minutes between sets.",
        ],
        hot={"BARBELL", "BACK", "SQUATS.", "FOUR", "SETS", "SIX", "EIGHT", "BRACE", "PARALLEL,",
             "DRIVE", "WHOLE", "FOOT.", "TWO", "MINUTES"},
        shots=[("squat", 1.0, 0.5, 0.5, "right"), ("squat", 1.35, 0.45, 0.45, "right")],
        speed=0.65,
    ),
    dict(
        id="ex2",
        num=2, title="BULGARIAN SPLIT SQUATS", muscle="GLUTES & QUADS",
        sets="3", reps="8-10", rest="90s", tip="EACH LEG",
        lines=[
            "Exercise two. Bulgarian split squats.",
            "Three sets of eight to ten reps on each leg.",
            "Back foot on the bench, drop your back knee straight down, and keep your front knee over your toes.",
            "Rest ninety seconds.",
        ],
        hot={"BULGARIAN", "SPLIT", "SQUATS.", "THREE", "SETS", "EIGHT", "TEN", "EACH", "LEG.",
             "BENCH,", "STRAIGHT", "DOWN,", "TOES.", "NINETY"},
        shots=[("split", 1.15, 0.6, 0.5, "right", 600), ("split", 1.25, 0.58, 0.6, "right", 600)],
        speed=0.65,
    ),
    dict(
        id="ex3",
        num=3, title="LEG EXTENSIONS", muscle="QUADS",
        sets="3", reps="12-15", rest="60s", tip="PAUSE AT TOP",
        lines=[
            "Exercise three. Leg extensions.",
            "Three sets of twelve to fifteen reps.",
            "Kick up until your legs are straight, squeeze your quads for a second, and lower it slowly.",
            "Rest sixty seconds.",
        ],
        hot={"LEG", "EXTENSIONS.", "THREE", "SETS", "TWELVE", "FIFTEEN", "STRAIGHT,", "SQUEEZE",
             "QUADS", "SLOWLY.", "SIXTY"},
        shots=[("ext", 1.0, 0.5, 0.5, "left", 380), ("ext", 1.3, 0.55, 0.52, "left", 380)],
        speed=0.65,
    ),
    dict(
        id="ex4",
        num=4, title="LYING LEG CURLS", muscle="HAMSTRINGS",
        sets="3", reps="10-12", rest="60s", tip="HIPS DOWN",
        lines=[
            "Exercise four. Lying leg curls.",
            "Three sets of ten to twelve reps.",
            "Keep your hips pressed into the pad, curl your heels to your glutes, and control the way down.",
            "Rest sixty seconds.",
        ],
        hot={"LYING", "LEG", "CURLS.", "THREE", "SETS", "TEN", "TWELVE", "HIPS", "PAD,", "HEELS",
             "GLUTES,", "CONTROL", "SIXTY"},
        shots=[("curl", 1.0, 0.5, 0.5, "right", 960), ("curl", 1.3, 0.48, 0.52, "right", 960)],
        speed=0.65,
    ),
    dict(
        id="ex5",
        num=5, title="STANDING CALF RAISES", muscle="CALVES",
        sets="4", reps="12-15", rest="45s", tip="FULL STRETCH",
        lines=[
            "Exercise five. Standing calf raises.",
            "Four sets of twelve to fifteen reps.",
            "Rise up onto your toes, pause at the top, then sink into a full stretch at the bottom.",
            "Rest forty five seconds.",
        ],
        hot={"STANDING", "CALF", "RAISES.", "FOUR", "SETS", "TWELVE", "FIFTEEN", "TOES,", "PAUSE",
             "FULL", "STRETCH", "FORTY", "FIVE"},
        shots=[("calf", 1.0, 0.5, 0.5, "right"), ("calf", 1.4, 0.45, 0.7, "right", 560)],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "That's seventeen working sets.",
            "Run it once or twice a week, and add weight when the reps get easy.",
            "Save this for your next leg day, and follow for more.",
        ],
        hot={"SEVENTEEN", "WORKING", "SETS.", "TWICE", "ADD", "WEIGHT", "EASY.", "SAVE", "FOLLOW"},
        shots=[("squat", 1.1, 0.5, 0.45, None), ("calf", 1.0, 0.5, 0.5, None)],
        speed=0.7,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
