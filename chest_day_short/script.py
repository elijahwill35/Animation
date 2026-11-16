"""Narration, on-screen cards and shot plan for the chest day Short.

assets/source.mp4 joins the two uploaded clips (both 720x1280, resampled to 24 fps):
  clip1_smith_press.mov              -> smith     frames   0-230  low-incline Smith press
  clip2_dips_flyes_press_pecdeck.mov -> dips      frames 231-275
                                        flyes     frames 276-324  low-to-high cable flyes
                                        press     frames 325-372  dumbbell squeeze press
                                        pecdeck   frames 373-420

Structure: hook ("Bench press isn't building your chest") -> five exercise scenes ->
a full-workout card held on screen long enough to screenshot.
"""

TITLE_1 = "CHEST DAY"
TITLE_2 = "5 EXERCISES · 40 MIN"
FOCUS_LABEL = "HOW TO PROGRESS"
FOCUS = "1-2× A WEEK · ADD WEIGHT OR A REP AT THE TOP OF THE RANGE"

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "smith": (1, 229),
    "dips": (233, 274),
    "flyes": (278, 323),
    "press": (327, 371),
    "pecdeck": (375, 419),
}

# shot = (segment, zoom, cx, cy, card_side[, card_y])
SCENES = [
    dict(
        id="intro",
        lines=[
            "Bench press isn't building your chest.",
            "Do these five instead, and grab the full workout at the end.",
        ],
        hot={"BENCH", "PRESS", "ISN'T", "CHEST.", "FIVE", "INSTEAD,", "FULL", "WORKOUT", "END."},
        shots=[("smith", 1.3, 0.45, 0.4, None), ("flyes", 1.2, 0.5, 0.4, None),
               ("pecdeck", 1.15, 0.5, 0.45, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="LOW-INCLINE SMITH PRESS", muscle="UPPER CHEST",
        sets="4", reps="6-8", rest="2 MIN", tip="15-30° INCLINE",
        lines=[
            "One. Low incline Smith press.",
            "Four sets of six to eight.",
            "Lower the bar to your upper chest, and keep your shoulder blades pinned.",
        ],
        hot={"LOW", "INCLINE", "SMITH", "PRESS.", "FOUR", "SETS", "SIX", "EIGHT.", "UPPER", "CHEST,",
             "SHOULDER", "BLADES", "PINNED."},
        shots=[("smith", 1.0, 0.5, 0.5, "right", 760), ("smith", 1.3, 0.45, 0.42, "right", 760)],
        speed=0.75,
    ),
    dict(
        id="ex2",
        num=2, title="CHEST DIPS", muscle="LOWER CHEST",
        sets="3", reps="8-10", rest="90s", tip="LEAN FORWARD",
        lines=[
            "Two. Chest dips.",
            "Three sets of eight to ten.",
            "Lean forward and flare your elbows slightly, so your chest does the work, not your triceps.",
        ],
        hot={"CHEST", "DIPS.", "THREE", "SETS", "EIGHT", "TEN.", "LEAN", "FORWARD", "FLARE", "ELBOWS",
             "CHEST", "WORK,", "TRICEPS."},
        shots=[("dips", 1.0, 0.5, 0.5, "right", 600), ("dips", 1.3, 0.42, 0.42, "right", 600)],
        speed=0.65,
    ),
    dict(
        id="ex3",
        num=3, title="LOW-TO-HIGH CABLE FLYES", muscle="UPPER CHEST",
        sets="3", reps="12-15", rest="60s", tip="SQUEEZE 1 SEC",
        lines=[
            "Three. Low to high cable flyes.",
            "Three sets of twelve to fifteen.",
            "Sweep up to chin height, and squeeze for one second at the top.",
        ],
        hot={"LOW", "HIGH", "CABLE", "FLYES.", "THREE", "SETS", "TWELVE", "FIFTEEN.", "CHIN", "HEIGHT,",
             "SQUEEZE", "ONE", "SECOND"},
        shots=[("flyes", 1.0, 0.5, 0.5, "right", 900), ("flyes", 1.3, 0.5, 0.4, "right", 900)],
        speed=0.65,
    ),
    dict(
        id="ex4",
        num=4, title="DUMBBELL SQUEEZE PRESS", muscle="INNER CHEST",
        sets="3", reps="10-12", rest="60s", tip="PRESS THEM TOGETHER",
        lines=[
            "Four. Dumbbell squeeze press.",
            "Three sets of ten to twelve.",
            "Press the dumbbells hard into each other, the whole rep.",
        ],
        hot={"DUMBBELL", "SQUEEZE", "PRESS.", "THREE", "SETS", "TEN", "TWELVE.", "HARD", "EACH",
             "OTHER,", "WHOLE", "REP."},
        shots=[("press", 1.0, 0.5, 0.5, "right", 1000), ("press", 1.25, 0.5, 0.4, "right", 1000)],
        speed=0.65,
    ),
    dict(
        id="ex5",
        num=5, title="PEC DECK, 1½ REPS", muscle="FULL CHEST",
        sets="2", reps="10-12", rest="60s", tip="FULL + HALF + FULL",
        lines=[
            "Five. Pec deck, with one and a half reps.",
            "Two sets of ten to twelve.",
            "A full rep, half a rep back out, then another full rep. It's brutal at the end.",
        ],
        hot={"PEC", "DECK,", "ONE", "HALF", "REPS.", "TWO", "SETS", "TEN", "TWELVE.", "FULL", "BRUTAL"},
        shots=[("pecdeck", 1.0, 0.5, 0.5, "left", 1000), ("pecdeck", 1.25, 0.5, 0.42, "left", 1000)],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "Do this once or twice a week, and add weight or a rep when the top of the range gets easy.",
            "Screenshot the full workout, and follow for more.",
        ],
        hot={"ONCE", "TWICE", "WEEK,", "ADD", "WEIGHT", "REP", "EASY.", "SCREENSHOT", "FULL", "WORKOUT,",
             "FOLLOW"},
        shots=[("smith", 1.1, 0.5, 0.5, None)],
        speed=0.6,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
