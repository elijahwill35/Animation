"""Narration, on-screen cards and shot plan for the chest & back routine video.

Source clip (assets/source.mp4, 1280x720 landscape, 24 fps, 10 s) has five 2-second shots:
  pushup     0.00-1.96  push-ups, front view
  row        1.96-3.96  dumbbell bent-over rows, side view
  incline    3.96-5.96  dumbbell incline press
  pulldown   5.96-8.00  lat pulldown, rear three-quarter view
  bench      8.00-10.0  flat barbell bench press, overhead front view
"""

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "pushup": (1, 45),
    "row": (49, 93),
    "incline": (97, 141),
    "pulldown": (145, 190),
    "bench": (194, 238),
}

# shot = (segment, zoom, cx, cy, card_side)
#   zoom: 1.0 = full frame; cx/cy: framing centre in source-normalised coords
#   card_side: which side of the screen the sets/reps card sits on (away from the lifter)
SCENES = [
    dict(
        id="intro",
        lines=[
            "Want a bigger chest and a wider back?",
            "Here's a chest and back day that hits both.",
            "Five exercises, in about forty five minutes.",
        ],
        hot={"BIGGER", "CHEST", "WIDER", "BACK?", "BACK", "BOTH.", "FIVE", "EXERCISES,", "FORTY", "FIVE"},
        shots=[("bench", 1.15, 0.5, 0.45, None), ("row", 1.2, 0.62, 0.5, None),
               ("pulldown", 1.15, 0.58, 0.45, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="PUSH-UPS", muscle="CHEST",
        sets="3", reps="15-20", rest="45s", tip="BODY STRAIGHT",
        lines=[
            "Exercise one. Push-ups.",
            "Three sets of fifteen to twenty reps.",
            "Keep your body in a straight line, and lower your chest all the way to the floor.",
            "Rest forty five seconds.",
        ],
        hot={"PUSH-UPS.", "THREE", "SETS", "FIFTEEN", "TWENTY", "STRAIGHT", "LINE,", "FLOOR.",
             "FORTY", "FIVE"},
        shots=[("pushup", 1.0, 0.5, 0.5, "right"), ("pushup", 1.25, 0.5, 0.42, "right")],
        speed=0.65,
    ),
    dict(
        id="ex2",
        num=2, title="BENT-OVER ROWS", muscle="BACK",
        sets="4", reps="8-10", rest="90s", tip="FLAT BACK",
        lines=[
            "Exercise two. Bent over rows.",
            "Four sets of eight to ten reps.",
            "Hinge at the hips, keep your back flat, and pull the weights to your waist.",
            "Rest ninety seconds.",
        ],
        hot={"BENT", "OVER", "ROWS.", "FOUR", "SETS", "EIGHT", "TEN", "HINGE", "FLAT,", "WAIST.",
             "NINETY"},
        shots=[("row", 1.0, 0.5, 0.5, "left"), ("row", 1.4, 0.64, 0.55, "left")],
        speed=0.65,
    ),
    dict(
        id="ex3",
        num=3, title="DUMBBELL INCLINE PRESS", muscle="UPPER CHEST",
        sets="3", reps="8-12", rest="90s", tip="CONTROL DOWN",
        lines=[
            "Exercise three. Dumbbell incline press.",
            "Three sets of eight to twelve reps.",
            "Lower the dumbbells slowly to your upper chest, then press them back up together.",
            "Rest ninety seconds.",
        ],
        hot={"DUMBBELL", "INCLINE", "PRESS.", "THREE", "SETS", "EIGHT", "TWELVE", "SLOWLY", "UPPER",
             "CHEST,", "TOGETHER.", "NINETY"},
        shots=[("incline", 1.0, 0.5, 0.5, "left"), ("incline", 1.3, 0.6, 0.45, "left")],
        speed=0.65,
    ),
    dict(
        id="ex4",
        num=4, title="LAT PULLDOWNS", muscle="LATS",
        sets="3", reps="10-12", rest="75s", tip="ELBOWS DOWN",
        lines=[
            "Exercise four. Lat pulldowns.",
            "Three sets of ten to twelve reps.",
            "Keep your chest up, pull the bar to your collarbone, and drive your elbows down.",
            "Rest seventy five seconds.",
        ],
        hot={"LAT", "PULLDOWNS.", "THREE", "SETS", "TEN", "TWELVE", "CHEST", "UP,", "COLLARBONE,",
             "ELBOWS", "DOWN.", "SEVENTY", "FIVE"},
        shots=[("pulldown", 1.0, 0.5, 0.5, "left"), ("pulldown", 1.3, 0.6, 0.42, "left")],
        speed=0.65,
    ),
    dict(
        id="ex5",
        num=5, title="FLAT BENCH PRESS", muscle="CHEST",
        sets="4", reps="6-8", rest="2 MIN", tip="FEET PLANTED",
        lines=[
            "Exercise five. Flat bench press.",
            "Four sets of six to eight reps.",
            "Plant your feet, touch the bar to your chest, and press it up hard.",
            "Rest two minutes between sets.",
        ],
        hot={"FLAT", "BENCH", "PRESS.", "FOUR", "SETS", "SIX", "EIGHT", "PLANT", "FEET,", "CHEST,",
             "HARD.", "TWO", "MINUTES"},
        shots=[("bench", 1.0, 0.5, 0.5, "right"), ("bench", 1.3, 0.5, 0.42, "right")],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "That's seventeen working sets.",
            "Run it once or twice a week, and add weight when the reps get easy.",
            "Save this for your next chest and back day, and follow for more.",
        ],
        hot={"SEVENTEEN", "WORKING", "SETS.", "TWICE", "ADD", "WEIGHT", "EASY.", "SAVE", "FOLLOW"},
        shots=[("bench", 1.1, 0.5, 0.45, None), ("row", 1.0, 0.5, 0.5, None)],
        speed=0.7,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
