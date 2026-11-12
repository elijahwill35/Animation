"""Narration plan for the NBA player-props Short.

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) is a motion-graphics video:
a title card, six player-prop cards (~1 s each) and a "My Top 3 Favorites" card.
Each scene plays its card's build-in animation once (frames `play`), then holds on the
fully revealed frame (last of `play`) for as long as the narration needs.

A line is either a plain string, or (caption_text, spoken_text) when a name needs a
phonetic spelling for the TTS voice.

Note: the source card for Sengun reads "8/9 games (99%)"; 8/9 is 89%, so the
narration only says "eight of his last nine".
"""

SCENES = [
    dict(
        id="intro", play=(0, 22),
        lines=["Here are tonight's top six NBA player props, all hitting at eighty nine percent or better."],
        hot={"TOP", "SIX", "NBA", "PLAYER", "PROPS,", "EIGHTY", "NINE", "PERCENT"},
    ),
    dict(
        id="p1", play=(25, 43),
        lines=["Number one. Wendell Carter Junior, over seven rebounds.",
               "Ten for ten in his last ten games, averaging nine point seven."],
        hot={"WENDELL", "CARTER", "JUNIOR,", "SEVEN", "REBOUNDS.", "TEN", "NINE", "POINT"},
    ),
    dict(
        id="p2", play=(45, 65),
        lines=[("Number two. Shai Gilgeous-Alexander, twenty one plus points.",
                "Number two. Shay Gil-jus Alexander, twenty one plus points."),
               "Ten of his last eleven, averaging twenty nine and a half, with a bigger role tonight."],
        hot={"SHAI", "GILGEOUS-ALEXANDER,", "TWENTY", "ONE", "PLUS", "POINTS.", "TEN", "ELEVEN,",
             "NINE", "HALF,", "BIGGER", "ROLE"},
    ),
    dict(
        id="p3", play=(67, 89),
        lines=["Number three. Franz Wagner, fifteen plus points.",
               "Nine of his last ten, and with key starters out, expect higher usage."],
        hot={"FRANZ", "WAGNER,", "FIFTEEN", "PLUS", "POINTS.", "NINE", "TEN,", "HIGHER", "USAGE."},
    ),
    dict(
        id="p4", play=(91, 114),
        lines=["Number four. Donovan Clingan, over seven rebounds.",
               "Nine of his last ten, averaging ten point three, with a good matchup tonight."],
        hot={"DONOVAN", "CLINGAN,", "SEVEN", "REBOUNDS.", "NINE", "TEN,", "POINT", "THREE,", "MATCHUP"},
    ),
    dict(
        id="p5", play=(116, 138),
        lines=[("Number five. Alperen Sengun, sixteen plus points.",
                "Number five. Alperen Shen-goon, sixteen plus points."),
               "Eight of his last nine, averaging twenty one point three."],
        hot={"ALPEREN", "SENGUN,", "SIXTEEN", "PLUS", "POINTS.", "EIGHT", "NINE,", "TWENTY", "ONE",
             "POINT", "THREE."},
    ),
    dict(
        id="p6", play=(140, 163),
        lines=["Number six. Draymond Green, six plus assists.",
               "Eight of his last nine. He's the main playmaker."],
        hot={"DRAYMOND", "GREEN,", "SIX", "PLUS", "ASSISTS.", "EIGHT", "NINE.", "PLAYMAKER."},
    ),
    dict(
        id="top3", play=(165, 239),
        lines=["My top three favorites.",
               "Carter, over seven rebounds.",
               ("Shai, twenty one plus points.", "Shay, twenty one plus points."),
               "And Wagner, fifteen plus.",
               "Which one are you taking? Let me know in the comments.",
               "Follow for daily picks, and please bet responsibly."],
        hot={"TOP", "THREE", "FAVORITES.", "CARTER,", "SEVEN", "SHAI,", "TWENTY", "ONE", "WAGNER,",
             "FIFTEEN", "COMMENTS.", "FOLLOW", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
