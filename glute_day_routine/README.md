# Glute Day Routine — narrated workout video

A 63-second vertical video (1080×1920, 30 fps, ready for YouTube Shorts) built from the 20-second
workout clip in `assets/source.mp4`. It uses the same format, voice and music as
[`leg_day_routine`](../leg_day_routine), plus a hook at the start.

**Final video:** [`output/glute_day_routine.mp4`](../output/glute_day_routine.mp4)

## Hook (0:00 – 0:10)

Fast cuts across the exercises with big on-screen text:

1. "Squats alone won't build round glutes." → **SQUATS ALONE / WON'T DO IT**
2. "You need to hit all three areas…" → **TRAIN ALL 3 ZONES**, with pills that pop in as each one is
   said: LOWER → FULLNESS, UPPER → ROUNDNESS, SIDE → WIDTH
3. "Here's the workout." → **THE WORKOUT** list of all five exercises

## The routine (recommended glute workout)

| Time | # | Exercise | Sets × Reps | Rest | Zone | Cue on screen |
|---|---|---|---|---|---|---|
| 0:10 | 1 | Romanian deadlifts | 3 × 10 | 2–3 min | Lower glutes | Deep stretch |
| 0:19 | 2 | Bulgarian split squats | 3 × 10 each leg | 2 min | Lower glutes | Each leg |
| 0:27 | 3 | Diagonal cable kickbacks | 3 × 12–15 per leg | 60–90 s | Upper glutes | Per leg |
| 0:37 | 4 | Barbell hip thrusts | 3 × 10–12 | 2–3 min | Upper + overall | Pause at top |
| 0:45 | 5 | Seated hip abductions | 3 × 15–20 | 60–90 s | Side glutes | Hold 1–2 sec |

Outro (0:55): train glutes twice a week, add weight or reps over time, then the recap card and
"SAVE + FOLLOW".

Rest times come from the brief: 2–3 minutes for the heavier lifts and 60–90 seconds for isolation
work. They are on the cards rather than spoken, to keep the video near 60 seconds. The 45-degree hip
extension from the "5 best" list isn't in the footage, so the video follows the recommended workout.

## How it's made

This works the same way as `leg_day_routine`. The source has every exercise from two angles, so each
exercise scene cuts between both. The hook replaces the title intro (`draw_intro` in `render.py`).
The rest row on the card only lights up when a line actually talks about rest.

```bash
python3 -m vidkit.build glute_day_routine              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build glute_day_routine --preview    # voice + still frames only, for checking layout
```
