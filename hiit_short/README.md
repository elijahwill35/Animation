# "Who Needs a GLP-1?" Bodyweight Circuit — narrated Short

A 43-second vertical video (1080×1920, 30 fps) built from the 10-second clip in `assets/source.mp4`.
It uses the same layout as the "Ozempic Who?" full-body video
([`fullbody_short`](../fullbody_short)) and the same voice and beat as the other videos.

**Final video:** [`output/hiit_short.mp4`](../output/hiit_short.mp4)

## Script

| Time | Slide | Narration |
|---|---|---|
| 0:00 | **Who needs a GLP-1? / NOT YOU. / not after this routine** | "Who needs a GLP-1? Not you, after this routine." |
| 0:04 | The workout: 6 moves · 3 rounds, rest 60–90 s, no equipment needed | "Six moves, three rounds, no equipment." |
| 0:07 | 1/6 Jump Squats · 15 reps | "Jump squats, fifteen reps. Land soft, and sink right into the next one." |
| 0:11 | 2/6 Reverse Lunges · 12 each leg | "Reverse lunges, twelve each leg. Step back, and keep your front knee over your ankle." |
| 0:16 | 3/6 Inchworm Walkouts · 10 reps | "Inchworm walkouts, ten reps. Walk your hands out to a plank, then walk them back." |
| 0:22 | 4/6 Plank Shoulder Taps · 20 total | "Plank shoulder taps, twenty total. Feet wide, and keep your hips still." |
| 0:26 | 5/6 Skaters · 30 seconds | "Skaters, thirty seconds. Leap side to side, and land on one foot." |
| 0:31 | 6/6 High Knees · 40 seconds | "High knees, forty seconds. Knees to hip height, and pump your arms." |
| 0:34 | Do 3 rounds + grid of all six moves | "Do three rounds, resting sixty to ninety seconds between each. Save this for your next workout, and tag the friend who needs it." |

The 3 rounds and 60–90 s rest were not in the brief. They match the previous full-body video, so
edit `ROUNDS` / `REST` in `script.py` and the matching narration if you want something different. The
form tips are also new; change them in `MOVES`.

## Build

```bash
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/hiit_short.mp4
```

`python3 render.py --preview [--t=12.5 ...]` writes still frames to `build/preview/`.
