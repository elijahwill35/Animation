"""Narration and on-screen plan for the "No GLP-1 needed" bodyweight circuit Short (~40 s).

Same layout as the "Ozempic Who?" full-body video: hook slide -> workout overview ->
one scene per move (number, body area, title, reps pill, footage in a rounded card,
form tip) -> "Do 3 rounds" outro with every move in a grid.

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) has six ~1.7 s shots, in order.
"""

TOPLINE = "FULL BODY · NO EQUIPMENT"
ROUNDS = 3
REST = "60-90 s"

# source frame ranges (inclusive), trimmed away from each cut
SEGMENTS = {
    "jump": (1, 37),
    "lunge": (41, 77),
    "inch": (81, 117),
    "taps": (121, 157),
    "skate": (161, 197),
    "knees": (201, 238),
}

# id, title, area, reps (pill), segment, narration (name line, tip line), on-screen tip
MOVES = [
    ("jump", "Jump Squats", "LEGS + GLUTES", "15 REPS",
     ("Jump squats, fifteen reps.", "Land soft, and sink right into the next one."),
     "Land soft, sink into the next rep"),
    ("lunge", "Reverse Lunges", "LEGS + GLUTES", "12 EACH LEG",
     ("Reverse lunges, twelve each leg.", "Step back, and keep your front knee over your ankle."),
     "Step back, front knee over ankle"),
    ("inch", "Inchworm Walkouts", "CORE + SHOULDERS", "10 REPS",
     ("Inchworm walkouts, ten reps.", "Walk your hands out to a plank, then walk them back."),
     "Walk out to a plank, walk back"),
    ("taps", "Plank Shoulder Taps", "CORE", "20 TOTAL",
     ("Plank shoulder taps, twenty total.", "Feet wide, and keep your hips still."),
     "Feet wide, hips still"),
    ("skate", "Skaters", "LEGS + CARDIO", "30 SECONDS",
     ("Skaters, thirty seconds.", "Leap side to side, and land on one foot."),
     "Leap side to side, land on one foot"),
    ("knees", "High Knees", "CARDIO", "40 SECONDS",
     ("High knees, forty seconds.", "Knees to hip height, and pump your arms."),
     "Knees to hip height, pump your arms"),
]

HOOK_LINES = ["Who needs a GLP-1?", "Not you, after this routine."]
OVERVIEW_LINES = ["Six moves, three rounds, no equipment."]
OUTRO_LINES = ["Do three rounds, resting sixty to ninety seconds between each.",
               "Save this for your next workout, and tag the friend who needs it."]

# Spoken overrides for words the TTS voice gets wrong (raw IPA in [[ ]] for Piper).
SPOKEN = {}
