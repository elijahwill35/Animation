"""Narration plan for the NBA player-props Short (Nov 12 slate).

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) is a motion-graphics video:
a "100% HIT RATE? / UNMISSABLE NBA PROPS / TOP 6 PROPS - NOV 12" title card, six player-prop
cards (~1 s each) and a "TOP 3 NBA FAVORITES" card. Each scene plays its card's build-in
animation once (frames `play`), then holds on the fully revealed frame (last of `play`) for as
long as the narration needs.

A line is either a plain string, or (caption_text, spoken_text) when a name needs a phonetic
spelling for the TTS voice.

Everything said comes from the cards. Two of them (Maxey 3+ threes on a 2.7 average, Kuminga
21+ PRA on a 20.8 average) sit above the player's average, so the narration says so instead of
selling them as locks. Only four of the six are 10/10, so the hook says "four".
"""

SCENES = [
    dict(
        id="intro", play=(0, 17),
        lines=["Four of tonight's NBA props have hit ten straight games.",
               "Stay to the end for the three I'm riding."],
        hot={"FOUR", "TEN", "STRAIGHT", "GAMES.", "END", "THREE", "RIDING."},
    ),
    dict(
        id="p1", play=(20, 45),
        lines=["Number one. Cade Cunningham, twenty five plus points, rebounds and assists.",
               "Ten for ten, averaging over thirty five."],
        hot={"CADE", "CUNNINGHAM,", "TWENTY", "FIVE", "PLUS", "TEN", "THIRTY", "FIVE."},
    ),
    dict(
        id="p2", play=(46, 70),
        lines=["Number two. Cooper Flagg, twenty plus points and assists.",
               "Ten for ten, averaging almost thirty three."],
        hot={"COOPER", "FLAGG,", "TWENTY", "PLUS", "TEN", "THIRTY", "THREE."},
    ),
    dict(
        id="p3", play=(71, 94),
        lines=["Number three. Jaylen Brown, twenty plus points, rebounds and assists.",
               "Ten for ten, averaging almost thirty two."],
        hot={"JAYLEN", "BROWN,", "TWENTY", "PLUS", "TEN", "THIRTY", "TWO."},
    ),
    dict(
        id="p4", play=(95, 118),
        lines=["Number four. Miles Bridges, twelve plus points and rebounds.",
               "Ten for ten, averaging over twenty two. He doesn't need a big night."],
        hot={"MILES", "BRIDGES,", "TWELVE", "PLUS", "TEN", "TWENTY", "TWO.", "BIG", "NIGHT."},
    ),
    dict(
        id="p5", play=(119, 141),
        lines=[("Number five. Tyrese Maxey, three plus threes.",
                "Number five. Tyreese Maxey, three plus threes."),
               "Seven of ten, but he averages two point seven, so it's riskier."],
        hot={"TYRESE", "MAXEY,", "THREE", "PLUS", "THREES.", "SEVEN", "TEN,", "TWO", "SEVEN,",
             "RISKIER."},
    ),
    dict(
        id="p6", play=(142, 164),
        lines=[("Number six. Jonathan Kuminga, twenty one plus points, rebounds and assists.",
                "Number six. Jonathan Koo-ming-ga, twenty one plus points, rebounds and assists."),
               "Seven of ten, averaging right around the line."],
        hot={"JONATHAN", "KUMINGA,", "TWENTY", "ONE", "PLUS", "SEVEN", "TEN,", "LINE."},
    ),
    dict(
        id="top3", play=(165, 239), caption_y=1615,   # above the card's disclaimer
        lines=["So, who am I riding?",
               "Cade, Flagg, and Bridges.",
               "Which one are you taking? Tell me in the comments.",
               "Follow for daily picks, and please bet responsibly."],
        hot={"RIDING?", "CADE,", "FLAGG,", "BRIDGES.", "COMMENTS.", "FOLLOW", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
