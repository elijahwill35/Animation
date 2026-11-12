# NFL Player Props, Nov 12 — narrated Short

A 64-second vertical video (1080×1920, 30 fps), stretched from the 10-second motion-graphics clip
in `assets/source.mp4`. It opens with a hook and has a voiceover reading the script, with synced
captions and the synthesized beat. Built the same way as [`nba_props_nov12`](../nba_props_nov12).

**Final video:** [`output/nfl_props_nov12.mp4`](../output/nfl_props_nov12.mp4)

## Script

| Time | Card | Narration |
|---|---|---|
| 0:00 | 100% NFL Hit Rate? Top 4 NFL Props | **Hook:** "Three NFL props tonight are a perfect ten for ten. And one of them only needs two catches. Stay to the end for the three I'm riding." |
| 0:08 | 1. Jayden Daniels | 10+ rushing yards · 10/10, averaging over 40 · his legs give him multiple ways to clear it |
| 0:19 | 2. Stefon Diggs | 30+ receiving yards · 10/10, averaging 58.5 · low line, doesn't need a massive game |
| 0:29 | 3. Isaiah Likely | 2+ receptions · 10/10, averaging over 5 · steady role, only needs two (pays off the hook) |
| 0:39 | 4. Cam Skattebo | 40+ rushing yards · 8/10, averaging almost 65 · has missed twice, so he's the riskiest |
| 0:50 | Top 3 NFL Favorites | Payoff: Daniels, Diggs and Likely · rain, check the injury report · comment prompt · follow · "please bet responsibly" |

Everything said comes from the cards. Three of the four are 10/10, so the hook says "three".
Not used: the title card's "WSH vs NYG" and the note's J.J. McCarthy line (they don't match the
players on the cards), and the Diggs card's "40.5 rushing yds" bullet (it looks copied from Daniels').
On the last card the captions sit below the card's injury/weather note (`caption_y` in `script.py`).

## Build

```bash
python3 -m vidkit.build nfl_props_nov12              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build nfl_props_nov12 --preview    # voice + still frames only
```
