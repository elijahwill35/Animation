# NBA Player Props, Nov 12 — narrated Short

A 64-second vertical video (1080×1920, 30 fps), stretched from the 10-second motion-graphics clip
in `assets/source.mp4`. It opens with a hook and has a voiceover reading the script, with synced
captions and the synthesized beat. Built the same way as [`nba_props_short`](../nba_props_short).

**Final video:** [`output/nba_props_nov12.mp4`](../output/nba_props_nov12.mp4)

## Script

| Time | Card | Narration |
|---|---|---|
| 0:00 | 100% Hit Rate? Unmissable NBA Props | **Hook:** "Four of tonight's NBA props have hit ten straight games. Stay to the end for the three I'm riding." |
| 0:06 | 1. Cade Cunningham | 25+ points, rebounds and assists · 10/10, averaging over 35 |
| 0:14 | 2. Cooper Flagg | 20+ points and assists · 10/10, averaging almost 33 |
| 0:20 | 3. Jaylen Brown | 20+ PRA · 10/10, averaging almost 32 |
| 0:28 | 4. Miles Bridges | 12+ points and rebounds · 10/10, over 22 · "doesn't need a big night" |
| 0:37 | 5. Tyrese Maxey | 3+ threes · 7/10, but averages 2.7, "so it's riskier" |
| 0:44 | 6. Jonathan Kuminga | 21+ PRA · 7/10, averaging right around the line (20.8) |
| 0:53 | Top 3 NBA Favorites | Payoff: Cade, Flagg and Bridges · comment prompt · follow · "please bet responsibly" |

Everything said comes from the cards. Only four of the six are 10/10, so the hook says "four".
For Maxey and Kuminga the line sits at or above their average, so the voice says so instead of
selling them as locks. On the last card the captions sit between the list and the card's
disclaimer (`caption_y` in `script.py`).

## Build

```bash
python3 -m vidkit.build nba_props_nov12              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build nba_props_nov12 --preview    # voice + still frames only
```
