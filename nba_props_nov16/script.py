"""Narration plan for the NBA player-props Short (Nov 16).

Source clip (assets/source.mov, 720x1280, 24 fps, 10 s) is a motion-graphics video:
a "TONIGHT'S 5 NBA PLAYER PROPS / BEST RECENT HIT RATES" title, five player-prop cards
(~1.5 s each, each fades out before the next) and a "WHICH ONE ARE YOU TAKING? / DROP IT IN
THE COMMENTS" end card. Each scene plays its card's build-in once (frames `play`), then holds
on the last fully revealed frame (before the card fades) while the narration runs.

A line is either a plain string, or (caption_text, spoken_text) for TTS pronunciation.

Everything said comes from the cards. Braun's card reads "10/10 (90%)", which contradicts
itself, so the narration only says he needs one steal.
"""

SCENES = [
    dict(
        id="intro", play=(0, 27),
        lines=["Let me make you some money tonight.",
               "Five NBA props, and one of them has hit twenty one straight."],
        hot={"MONEY", "TONIGHT.", "FIVE", "NBA", "PROPS,", "TWENTY", "ONE", "STRAIGHT."},
    ),
    dict(
        id="p1", play=(28, 58),
        lines=["Number one. Jaden McDaniels, over two and a half assists.",
               "Ten for ten."],
        hot={"JADEN", "MCDANIELS,", "OVER", "TWO", "HALF", "ASSISTS.", "TEN"},
    ),
    dict(
        id="p2", play=(64, 94),
        lines=["Number two. Davion Mitchell, over seven and a half points.",
               "That's twenty one straight, on a low line."],
        hot={"DAVION", "MITCHELL,", "OVER", "SEVEN", "HALF", "POINTS.", "TWENTY", "ONE", "STRAIGHT,",
             "LOW"},
    ),
    dict(
        id="p3", play=(100, 128),
        lines=["Number three. Cedric Coward, over six and a half rebounds.",
               "Nine of his last ten."],
        hot={"CEDRIC", "COWARD,", "OVER", "SIX", "HALF", "REBOUNDS.", "NINE", "TEN."},
    ),
    dict(
        id="p4", play=(133, 165),
        lines=["Number four. McDaniels again, over four and a half rebounds.",
               "Nine of ten."],
        hot={"MCDANIELS", "AGAIN,", "OVER", "FOUR", "HALF", "REBOUNDS.", "NINE", "TEN."},
    ),
    dict(
        id="p5", play=(173, 203),
        lines=["Number five. Christian Braun, over half a steal.",
               "He only needs one."],
        hot={"CHRISTIAN", "BRAUN,", "OVER", "HALF", "STEAL.", "ONE."},
    ),
    dict(
        id="outro", play=(209, 239),
        lines=["Which one are you taking? Drop it in the comments.",
               "Follow for more picks, and bet responsibly."],
        hot={"TAKING?", "COMMENTS.", "FOLLOW", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
