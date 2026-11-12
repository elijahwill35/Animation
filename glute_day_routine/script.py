"""Narration, on-screen cards and shot plan for the glute day routine video.

Source clip (assets/source.mp4, 720x1280 vertical, 24 fps, 20 s) shows the five exercises of
the recommended glute workout twice, from two angles each:
  rdl_a      0.00-1.96   Romanian deadlift, front three-quarter
  split_a    1.96-3.96   Bulgarian split squat
  kick_a     3.96-6.00   diagonal cable kickback, side
  thrust_a   6.00-8.08   barbell hip thrust, close
  abd_a      8.08-10.96  seated hip abduction, front
  rdl_b     10.96-13.00  Romanian deadlift, side
  split_b   13.00-14.54  Bulgarian split squat, side
  kick_b    14.54-16.08  diagonal cable kickback, rear three-quarter
  thrust_b  16.08-17.96  barbell hip thrust, side
  abd_b     17.96-20.00  seated hip abduction, front
"""

# source frame ranges (inclusive), trimmed 1-2 frames away from each cut
SEGMENTS = {
    "rdl_a": (1, 45),
    "split_a": (49, 93),
    "kick_a": (97, 142),
    "thrust_a": (146, 192),
    "abd_a": (196, 261),
    "rdl_b": (265, 310),
    "split_b": (314, 347),
    "kick_b": (351, 384),
    "thrust_b": (388, 429),
    "abd_b": (433, 478),
}

# shot = (segment, zoom, cx, cy, card_side[, card_y])
SCENES = [
    dict(
        id="intro",
        lines=[
            "Squats alone won't build round glutes.",
            "You need to hit all three areas. Lower glutes for fullness, upper glutes for roundness, "
            "and side glutes for width.",
            "Here's the workout.",
        ],
        hot={"SQUATS", "ALONE", "WON'T", "ROUND", "GLUTES.", "THREE", "AREAS.", "LOWER", "FULLNESS,",
             "UPPER", "ROUNDNESS,", "SIDE", "WIDTH."},
        shots=[("thrust_b", 1.3, 0.5, 0.5, None), ("kick_b", 1.15, 0.45, 0.5, None),
               ("rdl_a", 1.1, 0.55, 0.45, None), ("abd_b", 1.15, 0.5, 0.55, None),
               ("split_a", 1.1, 0.58, 0.5, None)],
        speed=0.8,
    ),
    dict(
        id="ex1",
        num=1, title="ROMANIAN DEADLIFTS", muscle="LOWER GLUTES",
        sets="3", reps="10", rest="2-3 MIN", tip="DEEP STRETCH",
        lines=[
            "One. Romanian deadlifts, for your lower glutes.",
            "Three sets of ten.",
            "Push your hips back, keep your back neutral, and lower until you feel a deep stretch.",
        ],
        hot={"ROMANIAN", "DEADLIFTS,", "LOWER", "GLUTES.", "THREE", "SETS", "TEN.", "HIPS", "BACK,",
             "NEUTRAL,", "DEEP", "STRETCH."},
        shots=[("rdl_a", 1.0, 0.5, 0.5, "left"), ("rdl_b", 1.0, 0.5, 0.5, "right")],
        speed=0.65,
    ),
    dict(
        id="ex2",
        num=2, title="BULGARIAN SPLIT SQUATS", muscle="LOWER GLUTES",
        sets="3", reps="10", rest="2 MIN", tip="EACH LEG",
        lines=[
            "Two. Bulgarian split squats.",
            "Three sets of ten on each leg.",
            "Lean slightly forward, and drive up through your front heel.",
        ],
        hot={"BULGARIAN", "SPLIT", "SQUATS.", "THREE", "SETS", "TEN", "EACH", "LEG.", "LEAN", "FORWARD,",
             "FRONT", "HEEL."},
        shots=[("split_a", 1.0, 0.5, 0.5, "left", 560), ("split_b", 1.0, 0.5, 0.5, "left", 560)],
        speed=0.65,
    ),
    dict(
        id="ex3",
        num=3, title="DIAGONAL CABLE KICKBACKS", muscle="UPPER GLUTES",
        sets="3", reps="12-15", rest="60-90s", tip="PER LEG",
        lines=[
            "Three. Diagonal cable kickbacks, for your upper glutes.",
            "Three sets of twelve to fifteen per leg.",
            "Kick back and slightly out, keep your hips square, and control the return.",
        ],
        hot={"DIAGONAL", "CABLE", "KICKBACKS,", "UPPER", "GLUTES.", "THREE", "SETS", "TWELVE", "FIFTEEN",
             "OUT,", "HIPS", "SQUARE,", "CONTROL"},
        shots=[("kick_a", 1.0, 0.5, 0.5, "left", 760), ("kick_b", 1.0, 0.5, 0.5, "right", 640)],
        speed=0.65,
    ),
    dict(
        id="ex4",
        num=4, title="BARBELL HIP THRUSTS", muscle="UPPER + OVERALL GLUTES",
        sets="3", reps="10-12", rest="2-3 MIN", tip="PAUSE AT TOP",
        lines=[
            "Four. Barbell hip thrusts.",
            "Three sets of ten to twelve.",
            "Drive through your heels, keep your ribs down, and squeeze hard at the top.",
        ],
        hot={"BARBELL", "HIP", "THRUSTS.", "THREE", "SETS", "TEN", "TWELVE.", "HEELS,", "RIBS",
             "DOWN,", "SQUEEZE", "HARD"},
        shots=[("thrust_a", 1.0, 0.5, 0.5, "right", 370), ("thrust_b", 1.0, 0.5, 0.5, "left", 1000)],
        speed=0.65,
    ),
    dict(
        id="ex5",
        num=5, title="SEATED HIP ABDUCTIONS", muscle="SIDE GLUTES",
        sets="3", reps="15-20", rest="60-90s", tip="HOLD 1-2 SEC",
        lines=[
            "Five. Seated hip abductions, for your side glutes.",
            "Three sets of fifteen to twenty.",
            "Push your knees out, hold for a second, and return slowly. No momentum.",
        ],
        hot={"SEATED", "HIP", "ABDUCTIONS,", "SIDE", "GLUTES.", "THREE", "SETS", "FIFTEEN", "TWENTY.",
             "KNEES", "OUT,", "HOLD", "SLOWLY.", "MOMENTUM."},
        shots=[("abd_a", 1.0, 0.5, 0.5, "right", 380), ("abd_b", 1.0, 0.5, 0.5, "right", 380)],
        speed=0.65,
    ),
    dict(
        id="outro",
        lines=[
            "Train glutes twice a week, and add weight or reps over time.",
            "Save this for your next glute day, and follow for more.",
        ],
        hot={"TWICE", "WEEK,", "ADD", "WEIGHT", "REPS",
             "SAVE", "FOLLOW"},
        shots=[("thrust_b", 1.15, 0.5, 0.55, None), ("rdl_b", 1.0, 0.5, 0.5, None)],
        speed=0.7,
    ),
]

EXERCISES = [s for s in SCENES if "num" in s]
