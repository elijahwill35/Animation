# Chest & Back Routine — narrated workout video

A 75-second landscape video (1920×1080, 30 fps) that explains a chest and back routine. It is built
from the 10-second workout clip in `assets/source.mp4`, with the same style, voice and music as
[`arm_day_routine`](../arm_day_routine). The source clip is landscape, so the video is too. A
vertical crop would cut off the push-ups and bench press.

**Final videos:**
* [`output/chest_back_routine.mp4`](../output/chest_back_routine.mp4): landscape, 1920×1080
* [`output/chest_back_short.mp4`](../output/chest_back_short.mp4): vertical for YouTube Shorts, 1080×1920

## The routine

| # | Exercise | Sets × Reps | Rest | Target | Cue on screen |
|---|---|---|---|---|---|
| 1 | Push-ups | 3 × 15–20 | 45 s | Chest | Body straight |
| 2 | Bent-over rows | 4 × 8–10 | 90 s | Back | Flat back |
| 3 | Dumbbell incline press | 3 × 8–12 | 90 s | Upper chest | Control down |
| 4 | Lat pulldowns | 3 × 10–12 | 75 s | Lats | Elbows down |
| 5 | Flat bench press | 4 × 6–8 | 2 min | Chest | Feet planted |

17 working sets in total. Timeline: intro 0:00 · push-ups 0:08 · rows 0:19 · incline press 0:30 ·
lat pulldowns 0:41 · bench press 0:53 · recap + save/follow 1:04 – 1:15

## How it's made

This uses the shared `vidkit` routine renderer with a landscape layout (`render.py` overrides the
intro and recap). Each 2-second shot is slowed down and looped back and forth with frame blending.
On top of it go the "EXERCISE n OF 5" header and progress bar, a sets/reps/rest card beside the
lifter (the row being read lights up red), and synced captions. The intro lists the five exercises.
The outro shows a recap card and a "SAVE + FOLLOW" button.

```bash
python3 -m vidkit.build chest_back_routine              # from the repo root: voice -> render -> audio -> mux -> QA, both cuts (project.json)
python3 -m vidkit.build chest_back_routine --preview    # voice + still frames only, for checking layout
```

`python3 render.py --preview [--t=12.5 ...]` writes still frames to `build/preview/`. To change sets,
reps or wording, edit `script.py` and re-run the build.

## Vertical (Shorts) version

`render_short.py` renders the same timeline at 1080×1920 and reuses `build/mix.wav`, so run
`render.py` first. Each shot gets its own framing from `SHORT_SHOTS` in `script.py`. Tight shots
(rows, pulldowns) fill the screen. Wide shots (push-ups, bench press) sit full-width over a blurred,
darkened copy of the same footage, so nothing is cropped off. The sets/reps/rest card becomes a strip
directly under the lifter.

The build command above renders this cut too (it's listed in `project.json`).

