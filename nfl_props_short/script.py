"""Narration plan for the NFL player-props Short (~45 s).

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) is a motion-graphics slate:
a title card ("100% Hit Rate NFL Props"), five player-prop cards and a "Top 3 NFL
Favorites" card. Each scene plays its card's build-in animation once (frames `play`),
then holds on the fully revealed frame while the narration talks through the pick.

Source card issues the narration steers around:
  * Smith-Njigba's card lists two different season averages (8.9 and 7.9 rec), so the
    voice uses "cleared it in every game" instead of an average.
  * Gibbs's card reads "Hit Rate: 9/8 (100%)", which isn't possible, so the voice says
    "every game" instead of a fraction.

A line is either a plain string, or (caption_text, spoken_text) when a name needs a
phonetic spelling for the TTS voice.
"""

SCENES = [
    dict(
        id="intro", play=(0, 22),
        lines=[
            "These five NFL props have a hundred percent hit rate this season.",
            "Stay to the end for my top three.",
        ],
        hot={"FIVE", "NFL", "PROPS", "HUNDRED", "PERCENT", "HIT", "RATE.",
             "END", "TOP", "THREE."},
    ),
    dict(
        id="p1", play=(28, 54),
        lines=[
            "One. Trey McBride, seven plus receptions.",
            "Nine for nine, with a twenty seven percent target share.",
        ],
        hot={"TREY", "MCBRIDE,", "SEVEN", "PLUS", "RECEPTIONS.", "NINE", "TWENTY", "PERCENT", "TARGET",
             "SHARE."},
    ),
    dict(
        id="p2", play=(60, 86),
        lines=[
            ("Two. Jaxon Smith-Njigba, five plus receptions.",
             "Two. Jaxon Smith en-jig-buh, five plus receptions."),
            "He's cleared it every game, with a great matchup against the Raiders.",
        ],
        hot={"JAXON", "SMITH-NJIGBA,", "FIVE", "PLUS", "RECEPTIONS.", "EVERY", "GAME,", "GREAT",
             "MATCHUP", "RAIDERS."},
    ),
    dict(
        id="p3", play=(92, 116),
        lines=[
            ("Three. Bijan Robinson, sixty plus rushing yards.",
             "Three. Bee-jahn Robinson, sixty plus rushing yards."),
            "Nine for nine, averaging almost ninety eight a game.",
        ],
        hot={"BIJAN", "ROBINSON,", "SIXTY", "PLUS", "RUSHING", "YARDS.", "NINE", "NINETY", "EIGHT"},
    ),
    dict(
        id="p4", play=(123, 148),
        lines=[
            ("Four. Jahmyr Gibbs, seventy plus scrimmage yards.",
             "Four. Jah-meer Gibbs, seventy plus scrimmage yards."),
            "He's hit it every game, averaging over a hundred forty.",
        ],
        hot={"JAHMYR", "GIBBS,", "SEVENTY", "PLUS", "SCRIMMAGE", "YARDS.", "EVERY", "GAME,",
             "HUNDRED", "FORTY."},
    ),
    dict(
        id="p5", play=(154, 184),
        lines=[
            ("Five. Chris Olave, four plus receptions.",
             "Five. Chris Oh-lah-vay, four plus receptions."),
            "Eight for eight, with a good home matchup against Carolina.",
        ],
        hot={"CHRIS", "OLAVE,", "FOUR", "PLUS", "RECEPTIONS.", "EIGHT", "HOME", "MATCHUP", "CAROLINA."},
    ),
    dict(
        id="top3", play=(191, 239),
        lines=[
            ("My top three. McBride, Smith-Njigba, and Robinson.",
             "My top three. McBride, Smith en-jig-buh, and Bee-jahn Robinson."),
            "Which one are you riding with? Comment below, and follow for more.",
            "Check injury reports, and bet responsibly.",
        ],
        hot={"TOP", "THREE.", "MCBRIDE,", "SMITH-NJIGBA,", "ROBINSON.", "BELOW,", "FOLLOW", "INJURY",
             "REPORTS,", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
