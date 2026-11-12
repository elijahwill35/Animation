# Arm Day Routine — narrated workout video

A 72-second vertical video (1080×1920, 30 fps) that explains an arm-day routine. It is built from the
10-second workout clip in `assets/source.mp4`.

**Final video:** [`output/arm_day_routine.mp4`](../output/arm_day_routine.mp4)

## The routine

| # | Exercise | Sets × Reps | Rest | Cue on screen |
|---|---|---|---|---|
| 1 | Dumbbell curls | 4 × 10–12 | 60–90 s | Elbows pinned |
| 2 | Tricep cable pushdowns | 3 × 12–15 | 60 s | Lock out |
| 3 | Skull crushers | 3 × 8–10 | 90 s | Elbows up |

Timeline: intro 0:00 · dumbbell curls 0:08 · cable pushdowns 0:26 · skull crushers 0:43 ·
recap + save/follow 1:00 – 1:12

## What's on screen

* **Header:** "EXERCISE n OF 3" with a progress bar, the exercise name and the target muscle.
* **Sets/reps card** next to the lifter, on the side away from him. It slides in when the narrator
  reads the sets and reps. The row being read lights up red: sets and reps first, then rest.
* **Captions** in 3-word chunks, synced to the voice, with key words in yellow.
* **Intro** lists the three exercises. The **outro** shows a recap card with every exercise's
  sets × reps × rest, then a "SAVE + FOLLOW" button.

## How it's made

The source clip has five 2-second shots: curls, pushdown (side), rope pushdown (front), skull
crushers and preacher curls. The preacher-curl shot only plays behind the recap. Each shot is
slowed to 0.6–0.8× and ping-pong looped with frame blending, so the lifter keeps repping for as long
as the narration runs. Shots also change framing (wide, then punch-in) every few seconds.

* `script.py`: narration lines, highlighted words, sets/reps/rest and the shot list per exercise.
* `voice.py`: makes the voiceover one sentence at a time with Piper TTS (`en-us-ryan-high`), the
  same voice and processing as `arm_day_short` (via `vidkit/voice.py`, which caches each sentence).
* `render.py`: a small subclass of the shared `vidkit/routine.py` renderer. It builds the timeline from the voice lengths and renders every frame (re-framing,
  cards, captions, flashes on cuts), using all CPU cores.
* `audio.py`: calls `vidkit/audio.py`, which makes an original synthesized beat with whooshes and
  impacts, then mixes it under the voice with ducking.

```bash
python3 -m vidkit.build arm_day_routine              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build arm_day_routine --preview    # voice + still frames only, for checking layout
```

`python3 render.py --preview [--t=12.5 ...]` writes still frames to `build/preview/`.

To change sets, reps or wording, edit `script.py` and re-run the build. Scene lengths follow
the voiceover automatically.
