"""Narration, on-screen cards and shot plan for the arm-day routine video.

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) has five 2-second shots:
  curl        0.00-1.96  standing dumbbell curls
  push_side   1.96-3.96  cable pushdown, side view
  push_front  3.96-6.00  rope pushdown, front view
  skull       6.00-8.00  skull crushers on an incline bench
  preacher    8.00-10.0  EZ-bar preacher curls (used as outro b-roll only)
"""

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "curl": (1, 45),
    "push_side": (49, 93),
    "push_front": (97, 142),
    "skull": (146, 190),
    "preacher": (194, 238),
}

# shot = (segment, zoom, cx, cy, card_side)
#   zoom: 1.0 = full frame; cx/cy: framing centre in source-normalised coords
#   card_side: which side of the screen the sets/reps card sits on (away from the lifter)
SCENES = [
    dict(
        id="intro",
        lines=[
            "Want bigger arms?",
            "Here's a simple arm day you can run this week.",
            "Three exercises, biceps and triceps, in about thirty minutes.",
        ],
        hot={"BIGGER", "ARMS?", "ARM", "DAY", "THREE", "EXERCISES,", "THIRTY"},
        shots=[("curl", 1.35, 0.45, 0.33, None), ("push_front", 1.15, 0.55, 0.45, None),
               ("skull", 1.1, 0.5, 0.45, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="DUMBBELL CURLS", muscle="BICEPS",
        sets="4", reps="10-12", rest="60-90s", tip="ELBOWS PINNED",
        lines=[
            "Exercise one. Dumbbell curls.",
            "Four sets of ten to twelve reps.",
            "Keep your elbows pinned to your sides, curl up, and squeeze hard at the top.",
            "Lower it slow, on a three second count.",
            "Don't swing the weight. If you have to swing, go lighter.",
            "Rest sixty to ninety seconds between sets.",
        ],
        hot={"DUMBBELL", "CURLS.", "FOUR", "SETS", "TEN", "TWELVE", "ELBOWS", "PINNED",
             "SQUEEZE", "SLOW,", "SWING,", "LIGHTER.", "THREE", "SECOND", "SIXTY", "NINETY"},
        shots=[("curl", 1.0, 0.5, 0.5, "right"), ("curl", 1.55, 0.42, 0.36, "right"),
               ("curl", 1.2, 0.5, 0.48, "right")],
        speed=0.62,
    ),
    dict(
        id="ex2",
        num=2, title="TRICEP CABLE PUSHDOWNS", muscle="TRICEPS",
        sets="3", reps="12-15", rest="60s", tip="LOCK OUT",
        lines=[
            "Exercise two. Tricep cable pushdowns.",
            "Three sets of twelve to fifteen reps.",
            "Lock your elbows at your sides and push down until your arms are fully straight.",
            "Then let the cable come back up under control.",
            "Keep your chest up, and don't let your shoulders roll forward.",
            "Rest sixty seconds.",
        ],
        hot={"TRICEP", "CABLE", "PUSHDOWNS.", "THREE", "SETS", "TWELVE", "FIFTEEN", "LOCK",
             "ELBOWS", "FULLY", "STRAIGHT.", "CONTROL.", "CHEST", "UP,", "SIXTY"},
        shots=[("push_side", 1.0, 0.5, 0.5, "left"), ("push_front", 1.0, 0.5, 0.5, "left"),
               ("push_side", 1.45, 0.62, 0.52, "left"), ("push_front", 1.35, 0.58, 0.5, "left")],
        speed=0.7,
    ),
    dict(
        id="ex3",
        num=3, title="SKULL CRUSHERS", muscle="TRICEPS",
        sets="3", reps="8-10", rest="90s", tip="ELBOWS UP",
        lines=[
            "Exercise three. Skull crushers.",
            "Three sets of eight to ten reps.",
            "Lower the bar slowly toward your forehead, and keep your elbows pointed up.",
            "Then press it back to the top, and squeeze your triceps.",
            "Pick a weight you can control. Your elbows will thank you.",
            "Rest ninety seconds.",
        ],
        hot={"SKULL", "CRUSHERS.", "THREE", "SETS", "EIGHT", "TEN", "SLOWLY", "FOREHEAD,",
             "ELBOWS", "UP.", "SQUEEZE", "TRICEPS.", "CONTROL.", "NINETY"},
        shots=[("skull", 1.0, 0.5, 0.5, "left"), ("skull", 1.3, 0.42, 0.36, "left"),
               ("skull", 1.12, 0.42, 0.45, "left")],
        speed=0.6,
    ),
    dict(
        id="outro",
        lines=[
            "That's ten working sets.",
            "Run it once or twice a week.",
            "Add a little weight, or one more rep, every week.",
            "Save this for your next arm day, and follow for more.",
        ],
        hot={"TEN", "WORKING", "SETS.", "TWICE", "WEIGHT,", "REP,", "WEEK.", "SAVE", "FOLLOW"},
        shots=[("preacher", 1.0, 0.5, 0.5, None), ("curl", 1.1, 0.5, 0.45, None)],
        speed=0.7,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
