# NBA Player Props, Nov 16 — narrated Short

A 41-second vertical video (1080×1920, 30 fps), stretched from the 10-second motion-graphics clip
in `assets/source.mov`. It opens with a hook and has a voiceover, synced captions and the
synthesized beat. Built the same way as [`nba_props_nov12`](../nba_props_nov12).

**Final video:** [`output/nba_props_nov16.mp4`](../output/nba_props_nov16.mp4)

## Script

| Time | Card | Narration |
|---|---|---|
| 0:00 | Tonight's 5 NBA Player Props | **Hook:** "Let me make you some money tonight. Five NBA props, and one of them has hit twenty one straight." |
| 0:05 | 1. Jaden McDaniels | over 2.5 assists · ten for ten |
| 0:11 | 2. Davion Mitchell | over 7.5 points · twenty one straight, on a low line (pays off the hook) |
| 0:17 | 3. Cedric Coward | over 6.5 rebounds · nine of his last ten |
| 0:23 | 4. Jaden McDaniels | over 4.5 rebounds · nine of ten |
| 0:29 | 5. Christian Braun | over 0.5 steals · "he only needs one" |
| 0:34 | Which one are you taking? | comment prompt · follow · "bet responsibly" |

Everything said comes from the cards. Braun's card reads "10/10 (90%)", which contradicts
itself, so the voice doesn't give his hit rate. Every card has a disclaimer at the very bottom,
so captions sit at y=1450 (`CAPTION_Y` in `render.py`).

## Build

```bash
python3 -m vidkit.build nba_props_nov16              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build nba_props_nov16 --preview    # voice + still frames only
```
