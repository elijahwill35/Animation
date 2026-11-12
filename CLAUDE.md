# Animation repo — how videos get made

Narrated vertical workout/sports videos, built from short source clips. All shared code is in
`vidkit/`; each project folder holds only what is specific to that video.

## Fast path for a new routine video (source clip with a few 2 s exercise shots)

```bash
python3 -m vidkit.new push_day_routine /path/to/clip.mp4 --title="PUSH DAY"
#   -> detects the shots, writes SEGMENTS, build/shots.jpg (look at this ONE image), scaffolds files
# edit push_day_routine/script.py: rename segments, write lines/cards/shots (copy leg_day_routine's style)
python3 -m vidkit.build push_day_routine --preview          # voice + stills in build/preview/
python3 -m vidkit.build push_day_routine                    # full: voice→render→audio→mux→QA
#   -> output/push_day_routine.mp4 + build/contact_push_day_routine.jpg (4x4 sheet: check this ONE image)
```

Look at `build/shots.jpg`, a few preview stills and the contact sheet. You don't need to read the
renderer to make a routine video. Tell the user the timings that build prints.

## Layout

- `vidkit/routine.py`: the routine renderer (`Routine` class). Layout numbers are class attributes,
  and each drawing step is a method. A project's `render.py` subclasses it and overrides only what
  differs: `TITLE`/`SRC` for a plain video, `draw_intro` for a hook (`glute_day_routine`), landscape
  plus intro/recap overrides (`chest_back_routine/render.py`), or a 9:16 re-frame of landscape
  footage (`chest_back_routine/render_short.py`).
- `vidkit/voice.py`: Piper `en-us-ryan-high`. Loads the model once and caches each line by
  (text, settings) in `build/vo/cache`, so editing one sentence re-voices only that sentence.
  Piper is NOT deterministic (each run is a new take), so the cache also locks a good take in.
- `vidkit/audio.py`: procedural beat + SFX + ducked voice (royalty-free, deterministic: seed 7).
- `vidkit/build.py`: the pipeline. `--preview`, `--only=render,mux`, `--draft` (ultrafast encode).
  An optional `project.json` sets the output name and extra cuts (see `chest_back_routine`).
- `vidkit/new.py`: project scaffold + shot detection.
- `arm_day_short/` (2D puppet from an avatar) and `nba_props_short/` (holds motion-graphics cards)
  have their own renderers but share vidkit voice/audio/build.

## Script conventions (routine videos)

- intro: 3 lines; the exercise list appears with line 3. Exercise scenes: line 1 names it, line 2
  gives sets×reps (the card lands and SETS/REPS light up), the last line starting "Rest" lights up REST.
- `hot` = words shown in yellow, written as they appear UPPERCASED with punctuation ("SQUATS.").
- shot = (segment, zoom, cx, cy, card_side[, card_y]); put the card on the side away from the lifter.
- TTS mispronunciations: use a `(caption, spoken)` tuple plus `spoken()` (see `nba_props_short`).

## Environment

Needs `opencv-python-headless piper-tts pillow numpy`, ffmpeg, Inter fonts
(`/usr/share/fonts/opentype/inter`), and the voice at `/root/piper/en-us-ryan-high.onnx`
(from https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz).
`bash vidkit/setup.sh` installs everything it can (idempotent).

## Performance notes (4 cores)

An ~80 s routine video takes ~11 s to voice from cold (0 s cached), ~75 s to render+encode, and
~5 s for audio. Rendering runs ~34 ms/frame. The source is colour-graded once at load
(`PREGRADE`), and the sets/reps card panels are cached. The encode (x264 `veryfast`, CRF 15)
matches the old `medium`/CRF 19 on SSIM/PSNR at ~1.8x the speed. Files are ~1.5x larger.

## Don't

- Don't overwrite a committed `output/*.mp4` unless the user asked for that video to change.
  A rebuild means a new voice take unless `build/vo/cache` is still there.
- Don't commit `build/` (it's gitignored).
