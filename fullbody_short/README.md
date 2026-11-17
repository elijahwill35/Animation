# "Ozempic Who?" Full-Body Workout — narration added

The uploaded video (`assets/source.mp4`, 56 s, 1080×1920, no audio) was already fully edited. Its
video is kept exactly as it was, with no re-encode. This project only adds a voiceover timed to the
on-screen text, plus the same synthesized beat and whooshes as the other videos.

**Final video:** [`output/fullbody_short.mp4`](../output/fullbody_short.mp4)

## Script and timing

| Time | On screen | Narration |
|---|---|---|
| 0:00 | Ozempic Who? … Shredded | "Ozempic who? This routine will have your body shredded." |
| 0:04 | 6 moves · 3 rounds | "Six moves, three rounds. Rest sixty to ninety seconds between rounds." |
| 0:09 | 1/6 Goblet squats, 15 reps | "Goblet squats, fifteen reps. Chest up, dumbbell at your chest. Hips back, thighs to parallel." |
| 0:16 | 2/6 Push-ups, 12–15 reps | "Push-ups, twelve to fifteen. Body in one straight line. Chest to just above the floor." |
| 0:23 | 3/6 Dumbbell rows, 12 each arm | "Dumbbell rows, twelve each arm. Flat back, hinge at the hips. Pull your elbow to your hip." |
| 0:30 | 4/6 Walking lunges, 10 each leg | "Walking lunges, ten each leg. Long step, back knee near the floor. Drive up through your front heel." |
| 0:37 | 5/6 Shoulder press, 12 reps | "Shoulder press, twelve reps. Brace your core, ribs down. Press straight up, no leaning back." |
| 0:44 | 6/6 Mountain climbers, 30 s | "Mountain climbers, thirty seconds. Hips level with your shoulders. Fast knees, and keep breathing." |
| 0:51 | Do 3 rounds / Save this… | "Do three rounds. Save this for your next workout, and tag the friend who needs it." |

"Ozempic" is fed to the voice as phonetic spelling (`SPOKEN` in `script.py`) so it says
"oh-ZEM-pik". The narration matches the on-screen text word for word where it can. Each exercise starts at
8.67 s + 7 s × n. Its two form tips appear 1.4 s and 4.2 s into the scene, and each spoken tip is
anchored to those moments.

## Build

```bash
python3 voice.py      # one Piper TTS clip per line
python3 timeline.py   # places lines at their target times, warns if one overruns a scene
python3 audio.py      # beat + whooshes + voice -> build/mix.wav
ffmpeg -i assets/source.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -shortest -movflags +faststart ../output/fullbody_short.mp4
```
