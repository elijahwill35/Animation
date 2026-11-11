"""Narration + on-screen plan for the arm-day Short.

Structure mirrors the reference Short (PSSVbHX5w90):
  hook (3 quick cuts) -> "and no, it's not ..." (red stripes -> solid red)
  -> muscle callout with red glow + anatomy inset -> exercise demos with
  green range-of-motion arrows -> recap -> red CTA screen.
"""

SCENES = [
    dict(id="hook", vo="Here's the arm day that builds massive arms, even in a t-shirt.",
         hot={"MASSIVE", "ARMS,", "T-SHIRT."}),
    dict(id="not", vo="And no, it's not a hundred sloppy curls.",
         hot={"NOT", "HUNDRED", "SLOPPY"}),
    dict(id="tri", vo="Your triceps are two thirds of your arm, so we train both sides.",
         hot={"TRICEPS", "TWO", "THIRDS", "BOTH"}),
    dict(id="ex1", vo="Exercise one. Barbell curls. Four sets of eight to ten. Squeeze at the top, and lower it slow.",
         hot={"BARBELL", "CURLS.", "FOUR", "SETS", "SQUEEZE", "SLOW."},
         title="BARBELL CURL", num="01", sets="4", reps="8-10", rest="90s", muscle="biceps",
         tip="SQUEEZE AT THE TOP"),
    dict(id="ex2", vo="Exercise two. Hammer curls. Three sets of ten to twelve. They build the brachialis, so your arms look thicker from the front.",
         hot={"HAMMER", "CURLS.", "THREE", "BRACHIALIS,", "THICKER"},
         title="HAMMER CURL", num="02", sets="3", reps="10-12", rest="75s", muscle="brachialis",
         tip="THUMBS UP GRIP"),
    dict(id="ex3", vo="Exercise three. Overhead triceps extensions. Three sets of ten to twelve. The deep stretch grows the long head, the biggest part of your triceps.",
         hot={"OVERHEAD", "EXTENSIONS.", "THREE", "STRETCH", "LONG", "HEAD,"},
         title="OVERHEAD EXTENSION", num="03", sets="3", reps="10-12", rest="75s", muscle="triceps",
         tip="DEEP STRETCH"),
    dict(id="ex4", vo="Exercise four. Rope pushdowns. Three sets of twelve to fifteen. Spread the rope and lock out hard.",
         hot={"ROPE", "PUSHDOWNS.", "THREE", "LOCK", "OUT"},
         title="ROPE PUSHDOWN", num="04", sets="3", reps="12-15", rest="60s", muscle="triceps",
         tip="LOCK OUT HARD"),
    dict(id="ex5", vo="Finish with a superset. Curls straight into pushdowns. Two rounds to failure.",
         hot={"SUPERSET.", "CURLS", "PUSHDOWNS.", "FAILURE."},
         title="SUPERSET FINISHER", num="05", sets="2", reps="FAILURE", rest="NONE", muscle="both",
         tip="NO REST BETWEEN"),
    dict(id="recap", vo="Rest about a minute between sets, and add weight every week.",
         hot={"MINUTE", "ADD", "WEIGHT", "WEEK."}),
    dict(id="cta", vo="Save this for your next arm day, and follow for more.",
         hot={"SAVE", "ARM", "DAY,", "FOLLOW"}),
]
