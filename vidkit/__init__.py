"""vidkit: the shared toolkit behind every video in this repo.

  vidkit.voice    Piper TTS voiceover (model loaded once, per-line cache, parallel post-processing)
  vidkit.audio    procedural beat + whoosh/impact SFX + ducked voice mix (no samples, no licences)
  vidkit.routine  the narrated workout-routine renderer (subclass `Routine` per project)
  vidkit.build    one-command pipeline: voice -> render -> audio -> mux, with timings

Run `python3 -m vidkit.build <project_dir>` (see README.md / CLAUDE.md).
"""
