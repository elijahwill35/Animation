"""Narration plan for the NBA parlay / referral Short (~45 s).

Source clip (assets/source.mp4, 720x1280, 24 fps, 10 s) is a motion-graphics slate:
a title card ("NBA LOCKS TONIGHT?"), three prop cards and a "Top 3 NBA Favorites" card.
Each scene plays its card's build-in animation once (frames `play`), then holds on the
fully revealed frame (last of `play`) while the narration talks through it.

The hook teases the referral bonus (a true, concrete reason to watch to the end) rather
than promising winnings. The last scene shows a promo panel for the referral offer with
a 21+ / terms / bet-responsibly line.

A line is either a plain string, or (caption_text, spoken_text) when the TTS voice needs a
phonetic spelling.
"""

PROMO = dict(bet="$20", bonus="$350")

SCENES = [
    dict(
        id="intro", play=(0, 20),
        lines=[
            "Three NBA plays I'm betting tonight.",
            "Stay to the end, and I'll show you how to turn twenty dollars into three hundred fifty "
            "in bonus bets.",
        ],
        hot={"THREE", "NBA", "PLAYS", "TONIGHT.", "END,", "TWENTY", "DOLLARS", "HUNDRED", "FIFTY",
             "BONUS", "BETS."},
    ),
    dict(
        id="p1", play=(24, 66),
        lines=[
            "First up, Davion Mitchell, over fourteen and a half points, minus one oh four on FanDuel.",
            ("With Klay Thompson and Pelle Larsson out, he carries the backcourt.",
             "With Klay Thompson and Pella Larsson out, he carries the backcourt."),
        ],
        hot={"DAVION", "MITCHELL,", "FOURTEEN", "HALF", "POINTS,", "MINUS", "FANDUEL.", "EIGHT", "TEN,",
             "CARRIES", "BACKCOURT."},
    ),
    dict(
        id="p2", play=(74, 114),
        lines=[
            "Next, Mitchell again, over one and a half threes, minus one seventy five on Fanatics.",
            "Same usage bump, eight of his last ten.",
        ],
        hot={"MITCHELL", "AGAIN,", "ONE", "HALF", "THREES,", "MINUS", "SEVENTY", "FIVE", "FANATICS.",
             "USAGE", "BUMP,", "EIGHT", "TEN."},
    ),
    dict(
        id="p3", play=(122, 161),
        lines=[
            "Last, Cedric Coward, over six and a half rebounds, minus one oh five on Fliff.",
            "Best hit rate on the slate.",
        ],
        hot={"CEDRIC", "COWARD,", "SIX", "HALF", "REBOUNDS,", "MINUS", "FIVE", "FLIFF.", "NINE", "TEN,",
             "BEST", "HIT", "RATE"},
    ),
    dict(
        id="top3", play=(166, 239), promo_from=1,   # promo panel appears with this line
        lines=[
            "Now the bonus.",
            "My referral code is in the description.",
            "New users who bet twenty dollars with my code get three hundred fifty in bonus bets.",
            "Twenty one plus, terms apply. Bet responsibly.",
        ],
        hot={"BONUS.", "REFERRAL", "CODE", "DESCRIPTION.", "NEW", "USERS", "TWENTY", "DOLLARS",
             "HUNDRED", "FIFTY", "BONUS", "BETS.", "TERMS", "RESPONSIBLY."},
    ),
]


def caption(line):
    return line[0] if isinstance(line, tuple) else line


def spoken(line):
    return line[1] if isinstance(line, tuple) else line
