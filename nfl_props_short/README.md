# NFL Player Props — narrated Short

A 48-second vertical video (1080×1920, 30 fps) built from the 10-second slate graphic in
`assets/source.mp4`. It uses the same voice, captions, embers and beat as
[`nba_props_short`](../nba_props_short).

**Final video:** [`output/nfl_props_short.mp4`](../output/nfl_props_short.mp4)

## Script

| Time | Card | Narration |
|---|---|---|
| 0:00 | 100% Hit Rate NFL Props | "These five NFL props have a hundred percent hit rate this season. Stay to the end for my top three." |
| 0:06 | 1. Trey McBride, 7+ rec | "Nine for nine, with a twenty seven percent target share." |
| 0:12 | 2. Jaxon Smith-Njigba, 5+ rec | "He's cleared it every game, with a great matchup against the Raiders." |
| 0:18 | 3. Bijan Robinson, 60+ rush yds | "Nine for nine, averaging almost ninety eight a game." |
| 0:24 | 4. Jahmyr Gibbs, 70+ scrimmage yds | "He's hit it every game, averaging over a hundred forty." |
| 0:31 | 5. Chris Olave, 4+ rec | "Eight for eight, with a good home matchup against Carolina." |
| 0:37 | Top 3 NFL Favorites | "My top three. McBride, Smith-Njigba, and Robinson. Which one are you riding with? Comment below, and follow for more. Check injury reports, and bet responsibly." |

The source cards have two errors, so the narration avoids those numbers:
- Smith-Njigba's card lists two different season averages (8.9 and 7.9 receptions).
- Gibbs's card reads "Hit Rate: 9/8".

Names get phonetic spellings for the voice (Smith en-jig-buh, Bee-jahn, Jah-meer, Oh-lah-vay).

## How it's made

This works the same way as `nba_props_short`: each card plays its build-in animation once, then holds
with a push-in and drifting embers while the voiceover covers the pick.

```bash
python3 voice.py && python3 render.py && python3 audio.py
ffmpeg -i build/video_silent.mp4 -i build/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart ../output/nfl_props_short.mp4
```
