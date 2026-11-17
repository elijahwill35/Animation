"""Place each voice line at its target time (or just after the previous line if that one runs
long) and write build/timeline.json in the format audio.py expects. Warns when a line would
spill past the next scene change.
"""
import json
import os

from script import CUTS, LINES, SLAMS, TOTAL

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
dur = json.load(open(os.path.join(BUILD, "vo", "durations.json")))

lines, t_free, ok = [], 0.0, True
for key, text, target in LINES:
    start = max(target, t_free + 0.12)
    end = start + dur[key]
    nxt = next((c for c in sorted(CUTS + [TOTAL]) if c > target + 0.05), TOTAL)
    flag = "" if end <= nxt + 0.05 else f"  <-- runs {end - nxt:.2f}s past the cut at {nxt:.2f}"
    ok &= not flag
    print(f"{key:9s} {start:6.2f} -> {end:6.2f} (target {target:5.2f}){flag}")
    lines.append(dict(key=key, start=start))
    t_free = end

tl = dict(total=TOTAL, cuts=CUTS, slams=SLAMS, lines=lines, scenes=[])
with open(os.path.join(BUILD, "timeline.json"), "w") as f:
    json.dump(tl, f, indent=1)
print("all lines fit" if ok else "some lines overrun")
