# NBA Player Props — narrated Short

A 68-second vertical video (1080×1920, 30 fps) built from the 10-second motion-graphics clip in
`assets/source.mp4`. It uses the same voice (Piper `en-us-ryan-high`), captions and synthesized beat
as the workout videos.

**Final video:** [`output/nba_props_short.mp4`](../output/nba_props_short.mp4)

## Timeline

| Time | Card | Narration covers |
|---|---|---|
| 0:00 | +89% Hit Rate Props | Intro |
| 0:06 | 1. Wendell Carter Jr. | 7+ rebounds, 10/10, 9.7 avg |
| 0:13 | 2. Shai Gilgeous-Alexander | 21+ points, 10/11, 29.5 avg, bigger role |
| 0:22 | 3. Franz Wagner | 15+ points, 9/10, starters out → higher usage |
| 0:30 | 4. Donovan Clingan | 7+ rebounds, 9/10, 10.3 avg, good matchup |
| 0:39 | 5. Alperen Sengun | 16+ points, 8/9, 21.3 avg |
| 0:46 | 6. Draymond Green | 6+ assists, 8/9, main playmaker |
| 0:53 | My Top 3 Favorites | Carter, SGA, Wagner, comment/follow call to action, "please bet responsibly" |

The narration only uses what is on the cards. Sengun's card reads "8/9 games (99%)", but 8/9 is
89%, so the voice says "eight of his last nine" and leaves the percentage out.

## How it's made

The source is graphics, not footage, so a back-and-forth loop would play the text animations in
reverse. Instead, each scene plays its card's build-in animation once (`play` frame range in
`script.py`), then holds on the finished frame. A slow push-in and procedural drifting embers keep
the held frame moving. Names the TTS voice would mispronounce get a phonetic spoken version
(a `(caption, spoken)` pair in `script.py`), for example "Shay Gil-jus Alexander" and "Alperen
Shen-goon".

```bash
python3 -m vidkit.build nba_props_short              # from the repo root: voice -> render -> audio -> mux -> QA
python3 -m vidkit.build nba_props_short --preview    # voice + still frames only, for checking layout
```
