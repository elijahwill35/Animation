# Arm Day — animated YouTube Short

A 47-second vertical (1080×1920, 30 fps) arm-day workout Short, animated from your single avatar
image. It follows the same flow as the reference Short `youtube.com/shorts/PSSVbHX5w90`.

**Final video:** [`output/arm_day_short.mp4`](../output/arm_day_short.mp4)

## Reference breakdown (what was measured)

| Metric | Reference Short | This video |
|---|---|---|
| Length | 43 s | 47 s (43.4 s of voiceover + pauses + end card) |
| Format | 9:16 vertical | 1080×1920, 30 fps, H.264 + AAC |
| Cuts | 20 scenes, one cut every ~1–3 s | 26 cuts, every ~1.0–3.6 s |
| Hook | 3 quick cuts in 3 s (close-up → medium → full) pointing at the camera | 3 cuts in 3.6 s (close-up → flex → full flex) |
| Pattern interrupt | red/gray stripes → solid red, glowing yellow eyes | "100 CURLS?" crossed out on stripes → solid red, glowing eyes, "NOPE." |
| Muscle callout | target muscle glows red, plus a small red-ringed anatomy close-up top right | red pulsing muscle glow + red-ringed magnifier on the working muscle |
| Exercise demo | full-body demo with green dashed range-of-motion arrows | the same: green dashed arrows follow the hands' real path |
| Background | light-gray studio, radial-line variant | light-gray studio, radial lines on callouts and the superset |
| Text | bold sans, key word in red above the figure | big red/white key word up top, plus word-chunk captions with red highlights |
| Ending | solid red, both hands pointing down, "click here" CTA | solid red, flex pose, "SAVE THIS" + bouncing arrows → FOLLOW button |
| Audio | energetic male voiceover | Piper TTS male voice, original synthesized 132 BPM beat, whooshes on cuts, impacts on slams |

## The workout in the video

| # | Exercise | Sets × Reps | Rest | Target |
|---|---|---|---|---|
| 01 | Barbell curl | 4 × 8–10 | 90 s | Biceps |
| 02 | Hammer curl | 3 × 10–12 | 75 s | Brachialis / forearm |
| 03 | Overhead triceps extension | 3 × 10–12 | 75 s | Triceps long head |
| 04 | Rope pushdown | 3 × 12–15 | 60 s | Triceps |
| 05 | Superset: curls → pushdowns | 2 rounds to failure | none | Both |

Scene timeline: hook 0:00 · "not 100 curls" 0:03.6 · triceps = 2/3 0:06.1 · ex1 0:09.6 · ex2 0:15.5 ·
ex3 0:22.1 · ex4 0:29.9 · superset 0:35.7 · recap 0:40.2 · CTA 0:43.3 – 0:47.1

## How it's made

The avatar (`assets/avatar.png`) is cut out and rigged as a 2D puppet:

* `rig.py` splits the arms into upper-arm and forearm layers with joint pivots, removes the
  selfie phone and raised arm, rebuilds the hidden cheek and neck by mirroring, and builds the
  second arm by mirroring the first. It also makes the biceps, triceps and forearm glow masks.
* `render.py` poses the puppet for each exercise (curls use forearm foreshortening, the overhead
  extension uses in-plane rotation with the forearms behind the head), draws the props
  (barbell, dumbbells, cable rope), arrows, cards, captions and camera cuts, and pipes the
  frames to ffmpeg.
* `voice.py` makes the voiceover with Piper TTS (`en-us-ryan-high`).
* `audio.py` synthesizes the beat and sound effects and mixes them with the voice, ducking the
  music under it.

```bash
pip install opencv-python-headless rembg piper-tts pillow numpy
python3 rig.py && python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest output/arm_day_short.mp4
```

`python3 render.py --preview [--only=ex1]` writes still frames to `build/preview/` for quick checks.

To change the workout, edit `script.py` (narration, hot words, sets and reps), then re-run
`voice.py`, `render.py` and `audio.py`. Scene lengths follow the voiceover automatically.

## Upgrading to full 3D AI animation

The reference looks like true 3D animation. That needs an AI video model. On Higgsfield,
`seedance_2_5` image-to-video costs about 35 credits per 5 s clip; the account had 1.6 credits
when this was made. With credits, each exercise scene can be regenerated from the avatar
with a prompt such as:

> "3D animated character from the reference image, plain light-gray studio, full body, performing
> strict standing barbell curls, slow controlled reps, biceps glowing red, static camera, 9:16"

You'd then drop the clips into the same timeline and overlays.
