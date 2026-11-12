"""One command from script.py to a finished, checked video.

    python3 -m vidkit.build <project_dir> [options]

Steps (each timed): voice.py -> render.py -> audio.py -> mux -> output/<name>.mp4 -> QA.

Options:
  --preview [--t=X ...]   voice + timeline + still frames only (build/preview/), no video.
                          Fastest way to check layout after editing script.py.
  --only=render,mux       run just these steps (voice, render, audio, mux, qa).
  --draft                 fast encode (preset ultrafast, crf 23) for a quick watch; not for upload.

QA (always after mux): ffprobe stream check, integrated loudness, and build/contact.jpg, a
4x4 contact sheet of the finished video, so one image shows the whole edit.

Per-project settings live in an optional <project>/project.json:
  {"output": "leg_day_routine.mp4",
   "cuts": [{"render": "render_short.py", "silent": "short_silent.mp4", "output": "chest_back_short.mp4"}]}
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = ["voice", "render", "audio", "mux", "qa"]


def run(cmd, cwd, env=None):
    t = time.time()
    subprocess.run(cmd, cwd=cwd, check=True, env=env)
    return time.time() - t


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    for line in reversed(r.stderr.splitlines()):
        if line.strip().startswith("I:"):
            return line.split(":")[1].strip()
    return "?"


def contact_sheet(video, out, dur):
    n = 16
    fps = n / max(dur, 1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf",
                    f"fps={fps:.5f},scale=-2:480,tile=4x4:padding=6:color=black", "-frames:v", "1",
                    "-q:v", "4", out], check=True)


def qa(final, build):
    info = probe(final)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    size = int(info["format"]["size"]) / 1e6
    sheet = os.path.join(build, "contact_" + os.path.splitext(os.path.basename(final))[0] + ".jpg")
    contact_sheet(final, sheet, dur)
    print(f"qa: {os.path.relpath(final, ROOT)}  {v['width']}x{v['height']} {v['codec_name']} "
          f"{v['r_frame_rate']}fps + {a['codec_name'] if a else 'NO AUDIO'}  {dur:.2f}s  {size:.1f} MB  "
          f"loudness {loudness(final)}")
    print(f"qa: contact sheet -> {os.path.relpath(sheet, ROOT)}")
    assert a is not None, "final video has no audio stream"


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)
    proj = os.path.abspath(args[0])
    name = os.path.basename(proj.rstrip("/"))
    build = os.path.join(proj, "build")
    os.makedirs(build, exist_ok=True)
    cfg = {}
    if os.path.exists(os.path.join(proj, "project.json")):
        cfg = json.load(open(os.path.join(proj, "project.json")))
    cuts = [dict(render="render.py", silent="video_silent.mp4", output=cfg.get("output", name + ".mp4"))]
    cuts += cfg.get("cuts", [])
    only = next((a.split("=")[1].split(",") for a in args if a.startswith("--only=")), STEPS)
    env = dict(os.environ)
    if "--draft" in args:
        env["VIDKIT_DRAFT"] = "1"
    times = {}

    if "--preview" in args:
        times["voice"] = run([sys.executable, "voice.py"], proj)
        times["preview"] = run([sys.executable, "render.py", "--preview"] +
                               [a for a in args if a.startswith("--t=")], proj)
        print("timings:", "  ".join(f"{k} {v:.0f}s" for k, v in times.items()))
        return

    if "voice" in only:
        times["voice"] = run([sys.executable, "voice.py"], proj)
    if "render" in only:
        times["render"] = run([sys.executable, "render.py"], proj, env)
    if "audio" in only:
        times["audio"] = run([sys.executable, "audio.py"], proj)
    for i, cut in enumerate(cuts):
        if i > 0 and "render" in only:
            times[f"render:{cut['render']}"] = run([sys.executable, cut["render"]], proj, env)
        final = os.path.join(ROOT, "output", cut["output"])
        if "mux" in only:
            os.makedirs(os.path.dirname(final), exist_ok=True)
            times[f"mux:{cut['output']}"] = run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(build, cut["silent"]),
                 "-i", os.path.join(build, "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-shortest", "-movflags", "+faststart", final], proj)
        if "qa" in only:
            qa(final, build)
    print("timings:", "  ".join(f"{k} {v:.0f}s" for k, v in times.items()),
          f"  total {sum(times.values()):.0f}s")


if __name__ == "__main__":
    main()
