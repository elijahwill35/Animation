"""Narration timed to the finished, silent "Ozempic Who?" full-body video (56 s, 1080x1920).

The video is already edited, so nothing is re-rendered: each line has a target time that
matches when its text appears on screen, and mix.py places the voice there (or right after
the previous line if that runs long), adds the beat and whooshes, and muxes it onto the
original video stream.

On-screen timing (measured from the video):
  0.0   hook "Ozempic Who? This routine will have your body Shredded" ("Shredded" lands ~1.8 s)
  3.7   overview card: 6 moves · 3 rounds
  each exercise starts at 8.67 + 7k s; first form tip at +1.43 s, second at +4.2 s
  50.67 "Do 3 rounds" outro, "Save this for your next workout! Tag the friend who needs it" ~52.5 s
"""

SEG = [8.67 + 7 * k for k in range(7)]   # six exercises + outro
TOTAL = 56.0

EXERCISES = [
    ("Goblet squats, fifteen reps.", "Chest up, dumbbell at your chest.", "Hips back, thighs to parallel."),
    ("Push-ups, twelve to fifteen.", "Body in one straight line.", "Chest to just above the floor."),
    ("Dumbbell rows, twelve each arm.", "Flat back, hinge at the hips.", "Pull your elbow to your hip."),
    ("Walking lunges, ten each leg.", "Long step, back knee near the floor.", "Drive up through your front heel."),
    ("Shoulder press, twelve reps.", "Brace your core, ribs down.", "Press straight up, no leaning back."),
    ("Mountain climbers, thirty seconds.", "Hips level with your shoulders.", "Fast knees, and keep breathing."),
]

# (key, text, target start time in seconds)
LINES = [
    ("hook_0", "Ozempic who?", 0.25),
    ("hook_1", "This routine will have your body shredded.", 1.1),
    ("overview", "Six moves, three rounds. Rest sixty to ninety seconds between rounds.", 3.9),
]
for i, (name, tip1, tip2) in enumerate(EXERCISES):
    s = SEG[i]
    LINES += [
        (f"ex{i + 1}_0", name, s + 0.3),
        (f"ex{i + 1}_1", tip1, s + 1.45),
        (f"ex{i + 1}_2", tip2, s + 4.2),
    ]
LINES += [
    ("outro_0", "Do three rounds.", SEG[6] + 0.3),
    ("outro_1", "Save this for your next workout, and tag the friend who needs it.", SEG[6] + 1.6),
]

# whooshes on every scene change, impacts on the hook's big word and each exercise title
CUTS = [3.67] + SEG
SLAMS = [1.8] + [s + 0.3 for s in SEG[:6]]
