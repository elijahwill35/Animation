# Glute Growth & Hamstrings — narrated workout video

A 46-second vertical video (1080×1920, 30 fps, ready for YouTube Shorts) built from the 10-second
workout clip in `assets/source.mp4`. It uses the same format, voice and music as
[`leg_day_routine`](../leg_day_routine). It adds a hook that promises the full workout at the end, and
an end card that holds long enough to screenshot.

**Final video:** [`output/glute_ham_routine.mp4`](../output/glute_ham_routine.mp4)
**Workout card (image):** [`output/glute_ham_workout_card.png`](../output/glute_ham_workout_card.png)

## Structure

| Time | Scene | Narration / on screen |
|---|---|---|
| 0:00 | Hook | "Want thicker glutes and stronger hamstrings?" → **THICKER GLUTES / STRONGER HAMSTRINGS** |
| 0:02 | Reason to stay | "Do these five exercises, and stay to the end for the full workout you can screenshot." → **5 EXERCISES**, **FULL WORKOUT AT THE END** with a bouncing arrow |
| 0:07 | 1. Barbell hip thrusts | 4 × 8–12 · "Squeeze hard at the top." |
| 0:13 | 2. Romanian deadlifts | 3 × 10–12 · "Hips back, and feel the stretch." |
| 0:19 | 3. Cable glute kickbacks | 3 × 12–15 · "Kick back, and don't swing." |
| 0:25 | 4. Seated leg curls | 3 × 12–15 · "Curl all the way back for your hamstrings." |
| 0:31 | 5. Seated hip abductions | 3 × 15–25 · "Push out, and hold." |
| 0:38 | Full workout card | "Here's the full workout. Screenshot it, save it for your next glute day, and follow for more." The card stays on screen for about 3 more seconds. |

The "EXERCISE n OF 5" progress bar also keeps viewers watching through to the payoff.

The rest times on the exercise cards (2 min for hip thrusts and RDLs, 60 s for kickbacks and leg curls,
45 s for abductions) are suggestions added for the video. The workout itself only listed sets and reps,
so the end card shows only sets, reps and main focus.

## How it's made

This works the same way as `leg_day_routine`. The hook and the end card replace the title intro and
recap (`draw_intro` / `draw_outro` in `render.py`). After a full render, `render.py` also saves the end
card as a standalone PNG in `output/`.

```bash
pip install opencv-python-headless piper-tts pillow numpy
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/glute_ham_routine.mp4
```
