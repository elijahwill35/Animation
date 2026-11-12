"""Narration plan for the NFL player-props Short (Nov 12).

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) is a motion-graphics video:
a "100% NFL HIT RATE? / TOP 4 NFL PROPS / NOV 12" title card, four player-prop cards
(~1.5 s each) and a "TOP 3 NFL FAVORITES" card with an injury/weather note. Each scene plays
its card's build-in animation once (frames `play`), then holds on the fully revealed frame.

A line is either a plain string, or (caption_text, spoken_text) when a name needs a phonetic
spelling for the TTS voice.

Everything said comes from the cards. Three of the four are 10/10, so the hook says "three".
Not used: the title card's "WSH vs NYG" and the note's J.J. McCarthy line (they don't match the
players on the cards), and the Diggs card's "40.5 rushing yds" bullet (a copy of Daniels').
"""

SCENES = [
    dict(
        id="intro", play=(0, 21),
        lines=["Three NFL props tonight are a perfect ten for ten.",
               "And one of them only needs two catches.",
               "Stay to the end for the three I'm riding."],
        hot={"THREE", "NFL", "PROPS", "PERFECT", "TEN", "TWO", "CATCHES.", "END"},
    ),
    dict(
        id="p1", play=(22, 56),
        lines=["Number one. Jayden Daniels, ten plus rushing yards.",
               "Ten for ten in his last ten, averaging over forty rushing yards a game.",
               "His legs give him multiple ways to clear this."],
        hot={"JAYDEN", "DANIELS,", "TEN", "PLUS", "RUSHING", "YARDS.", "FORTY", "MULTIPLE"},
    ),
    dict(
        id="p2", play=(57, 92),
        lines=["Number two. Stefon Diggs, thirty plus receiving yards.",
               "Another ten for ten, averaging fifty eight and a half.",
               "It's a low line, so he doesn't need a massive game."],
        hot={"STEFON", "DIGGS,", "THIRTY", "PLUS", "RECEIVING", "YARDS.", "TEN", "FIFTY", "EIGHT",
             "LOW", "LINE,", "MASSIVE"},
    ),
    dict(
        id="p3", play=(93, 129),
        lines=["Number three. Isaiah Likely, two plus receptions.",
               "Ten for ten, averaging over five catches a game.",
               "He has a steady role in the passing game, and he only needs two."],
        hot={"ISAIAH", "LIKELY,", "TWO", "PLUS", "RECEPTIONS.", "TEN", "FIVE", "CATCHES", "STEADY",
             "TWO."},
    ),
    dict(
        id="p4", play=(130, 165),
        lines=[("Number four. Cam Skattebo, forty plus rushing yards.",
                "Number four. Cam Skatta-bo, forty plus rushing yards."),
               "Eight of his last ten, averaging almost sixty five.",
               "He gets the workload, but he's missed twice, so he's the riskiest."],
        hot={"CAM", "SKATTEBO,", "FORTY", "PLUS", "RUSHING", "YARDS.", "EIGHT", "TEN,", "SIXTY",
             "FIVE.", "WORKLOAD,", "TWICE,", "RISKIEST."},
    ),
    dict(
        id="top3", play=(166, 239), caption_y=1790,   # below the card's injury/weather note
        lines=["So, who am I riding?",
               "Daniels, Diggs, and Likely.",
               "Rain is in the forecast, so check the injury report.",
               "Which one are you taking? Tell me in the comments.",
               "Follow for daily picks, and please bet responsibly."],
        hot={"RIDING?", "DANIELS,", "DIGGS,", "LIKELY.", "RAIN", "INJURY", "REPORT", "COMMENTS.",
             "FOLLOW", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
