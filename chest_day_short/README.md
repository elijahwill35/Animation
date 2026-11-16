# Chest Day — narrated Short from two joined clips

A 56-second vertical video (1080×1920, 30 fps, ready for YouTube Shorts). It joins two uploaded clips
and uses the same format, voice and music as
[`glute_ham_routine`](../glute_ham_routine): a hook, five exercise cards, and a screenshot-ready
workout card at the end.

**Final video:** [`output/chest_day_short.mp4`](../output/chest_day_short.mp4)
**Workout card (image):** [`output/chest_day_workout_card.png`](../output/chest_day_workout_card.png)

## Source

`assets/source.mp4` is the two clips joined in workout order and resampled to 24 fps:

1. `assets/clip1_smith_press.mov`: low-incline Smith press (one continuous shot)
2. `assets/clip2_dips_flyes_press_pecdeck.mov`: chest dips, low-to-high cable flyes, dumbbell
   squeeze press, pec deck

```bash
ffmpeg -i assets/clip1_smith_press.mov -i assets/clip2_dips_flyes_press_pecdeck.mov \
  -filter_complex "[0:v]fps=24,format=yuv420p[a];[1:v]fps=24,format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 -crf 14 assets/source.mp4
```

## Script

| Time | Scene | Narration / on screen |
|---|---|---|
| 0:00 | Hook | "Bench press isn't building your chest. Do these five instead, and grab the full workout at the end." → **BENCH PRESS ISN'T BUILDING YOUR CHEST**, **DO THESE 5 INSTEAD**, **FULL WORKOUT AT THE END** |
| 0:05 | 1. Low-incline Smith press | 4 × 6–8 · 2 min · "Lower the bar to your upper chest, and keep your shoulder blades pinned." |
| 0:13 | 2. Chest dips | 3 × 8–10 · 90 s · "Lean forward and flare your elbows slightly, so your chest does the work, not your triceps." |
| 0:21 | 3. Low-to-high cable flyes | 3 × 12–15 · 60 s · "Sweep up to chin height, and squeeze for one second at the top." |
| 0:29 | 4. Dumbbell squeeze press | 3 × 10–12 · 60 s · "Press the dumbbells hard into each other, the whole rep." |
| 0:36 | 5. Pec deck, 1½ reps | 2 × 10–12 · 60 s · "A full rep, half a rep back out, then another full rep. It's brutal at the end." |
| 0:45 | Workout card | "Do this once or twice a week, and add weight or a rep when the top of the range gets easy. Screenshot the full workout, and follow for more." |

## Build

```bash
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/chest_day_short.mp4
```
