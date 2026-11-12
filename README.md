# Animation

Narrated vertical videos (YouTube Shorts / Reels / TikTok), built from short source clips with an
original synthesized soundtrack and an offline TTS voice. Finished videos are in [`output/`](output).

| Project | Video | What it is |
|---|---|---|
| [`arm_day_routine`](arm_day_routine) | [72 s](output/arm_day_routine.mp4) | arm-day routine from a workout clip |
| [`chest_back_routine`](chest_back_routine) | [75 s](output/chest_back_routine.mp4) · [Short](output/chest_back_short.mp4) | landscape + 9:16 cut |
| [`leg_day_routine`](leg_day_routine) | [81 s](output/leg_day_routine.mp4) | five-exercise leg day |
| [`glute_day_routine`](glute_day_routine) | [63 s](output/glute_day_routine.mp4) | with a hook intro |
| [`nba_props_short`](nba_props_short) | [68 s](output/nba_props_short.mp4) | NBA player props from motion graphics |
| [`arm_day_short`](arm_day_short) | [47 s](output/arm_day_short.mp4) | 2D-animated avatar Short |

## Making a video

```bash
bash vidkit/setup.sh                                   # once per machine
python3 -m vidkit.new my_routine clip.mp4 --title="PUSH DAY"   # scaffold + shot detection
python3 -m vidkit.build my_routine --preview           # check layout stills
python3 -m vidkit.build my_routine                     # -> output/my_routine.mp4 + QA contact sheet
```

The shared engine is in [`vidkit/`](vidkit). See [`CLAUDE.md`](CLAUDE.md) for the conventions.
