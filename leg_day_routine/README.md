# Leg Day Routine — narrated workout video

An 81-second vertical video (1080×1920, 30 fps, ready for YouTube Shorts) that explains a leg day
routine. It is built from the 10-second workout clip in `assets/source.mov`, with the same style,
voice and music as [`arm_day_routine`](../arm_day_routine).

**Final video:** [`output/leg_day_routine.mp4`](../output/leg_day_routine.mp4)

## The routine

| # | Exercise | Sets × Reps | Rest | Target | Cue on screen |
|---|---|---|---|---|---|
| 1 | Barbell back squats | 4 × 6–8 | 2 min | Quads & glutes | Brace + depth |
| 2 | Bulgarian split squats | 3 × 8–10 per leg | 90 s | Glutes & quads | Each leg |
| 3 | Leg extensions | 3 × 12–15 | 60 s | Quads | Pause at top |
| 4 | Lying leg curls | 3 × 10–12 | 60 s | Hamstrings | Hips down |
| 5 | Standing calf raises | 4 × 12–15 | 45 s | Calves | Full stretch |

17 working sets in total. Timeline: intro 0:00 · squats 0:09 · split squats 0:20 · leg extensions 0:34 ·
leg curls 0:46 · calf raises 0:58 · recap + save/follow 1:10 – 1:21

## How it's made

This works the same way as `arm_day_routine`, and `render.py` and `audio.py` are copies of it. The
recap is extended to five exercises, and each shot can set its own card height (the optional 6th field
of a shot in `script.py`), so the sets/reps card stays clear of the lifter on every machine. Each
2-second shot is slowed down and looped back and forth with frame blending, re-framed with
punch-ins, and overlaid with the header, the sets/reps/rest card and synced captions.

```bash
pip install opencv-python-headless piper-tts pillow numpy
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/leg_day_routine.mp4
```

`python3 render.py --preview [--t=12.5 ...]` writes still frames to `build/preview/`. To change sets,
reps or wording, edit `script.py` and re-run all three scripts.
