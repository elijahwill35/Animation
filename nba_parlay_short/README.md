# NBA Parlay + Referral — narrated Short

A 44-second vertical video (1080×1920, 30 fps) built from the 10-second slate graphic in
`assets/source.mp4`. It uses the same voice, captions, embers and beat as
[`nba_props_short`](../nba_props_short), plus a hook badge and a referral promo panel.

**Final video:** [`output/nba_parlay_short.mp4`](../output/nba_parlay_short.mp4)

## Script

| Time | On screen | Narration |
|---|---|---|
| 0:00 | NBA Locks Tonight? | "Three NBA plays I'm betting tonight." |
| 0:02 | + hook badge **BET $20 · GET $350 IN BONUS BETS AT THE END** | "Stay to the end, and I'll show you how to turn twenty dollars into three hundred fifty in bonus bets." |
| 0:07 | 1. Davion Mitchell, over 14.5 pts | "…minus one oh four on FanDuel. With Klay Thompson and Pelle Larsson out, he carries the backcourt." |
| 0:17 | 2. Davion Mitchell, over 1.5 threes | "…minus one seventy five on Fanatics. Same usage bump, eight of his last ten." |
| 0:25 | 3. Cedric Coward, over 6.5 rebounds | "…minus one oh five on Fliff. Best hit rate on the slate." |
| 0:31 | Top 3 card → promo panel | "Now the bonus. My referral code is in the description. New users who bet twenty dollars with my code get three hundred fifty in bonus bets. Twenty one plus, terms apply. Bet responsibly." |

The promo panel reads: NEW USER BONUS · BET $20 · GET $350 IN BONUS BETS · USE MY REFERRAL CODE ·
LINK IN THE DESCRIPTION · "21+ · New users only · Terms apply · Bet responsibly". To change the
amounts, edit `PROMO` in `script.py` and the matching narration lines.

The hook teases the bonus rather than promising winnings, because sportsbook referral rules
generally don't allow "guaranteed" or "easy money" claims.

## How it's made

This works the same way as `nba_props_short`. Each card plays its build-in animation once, then holds
with a push-in and drifting embers. The promo blurs the Top 3 card and slides the offer panel over it.
The voice runs slightly faster here (`--length-scale 0.85`) to fit about 45 seconds.

```bash
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/nba_parlay_short.mp4
```
