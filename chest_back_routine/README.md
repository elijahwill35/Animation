# Chest & Back Routine — narrated workout video

A 75-second landscape video (1920×1080, 30 fps) that explains a chest and back routine. It is built
from the 10-second workout clip in `assets/source.mp4`, with the same style, voice and music as
[`arm_day_routine`](../arm_day_routine). The source clip is landscape, so the video is too. A
vertical crop would cut off the push-ups and bench press.

**Final video:** [`output/chest_back_routine.mp4`](../output/chest_back_routine.mp4)

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

This works the same way as `arm_day_routine`, and `render.py` and `audio.py` are copies of it with a
landscape layout. Each 2-second shot is slowed down and looped back and forth with frame blending.
On top of it go the "EXERCISE n OF 5" header and progress bar, a sets/reps/rest card beside the
lifter (the row being read lights up red), and synced captions. The intro lists the five exercises.
The outro shows a recap card and a "SAVE + FOLLOW" button.

```bash
pip install opencv-python-headless piper-tts pillow numpy
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/chest_back_routine.mp4
```

`python3 render.py --preview [--t=12.5 ...]` writes still frames to `build/preview/`. To change sets,
reps or wording, edit `script.py` and re-run all three scripts.
