"""Render, assemble, and write narration and captions.

Usage:
  python build.py preview   fast 480p15 render to output/preview/
  python build.py final     1920x1080 30 fps render and all deliverables in output/
  python build.py text      only rewrite narration.txt and captions.srt
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import config as C

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
MEDIA = ROOT / "build" / "media"
MANIM = ROOT / ".venv" / "bin" / "manim"

CLASSES = {
    "00_title": "S00Title",
    "01_vendors": "S01Vendors",
    "02_flow": "S02Flow",
    "03_posture": "S03Posture",
    "04_dollars": "S04Dollars",
    "05_agents": "S05Agents",
    "06_ahead": "S06Ahead",
}
SCENE_LABELS = {
    "00_title": "Scene 0, title card",
    "01_vendors": "Scene 1, Too many vendors, too many places",
    "02_flow": "Scene 2, One flow, two speeds",
    "03_posture": "Scene 3, Every signal gets a posture",
    "04_dollars": "Scene 4, From signal to dollars",
    "05_agents": "Scene 5, Six agents, one hub",
    "06_ahead": "Scene 6, From reacting to seeing ahead",
}
ENC = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-an"]


def sh(cmd):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT)


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def render(quality):
    dest = OUT if quality == "final" else OUT / "preview"
    dest.mkdir(parents=True, exist_ok=True)
    flags = ["-r", "1920,1080", "--fps", str(C.FPS_FINAL)] if quality == "final" else ["-ql"]
    for key, cls in CLASSES.items():
        sh([MANIM, "render", "--disable_caching", "--media_dir", MEDIA, *flags,
            "-o", key, "scenes.py", cls])
        found = sorted(MEDIA.glob(f"videos/scenes/*/{key}.mp4"), key=lambda p: p.stat().st_mtime)
        shutil.copy(found[-1], dest / f"{key}.mp4")
    return dest


def check_durations(dest):
    report = {}
    for key in C.SCENE_ORDER:
        planned, actual = C.scene_duration(key), probe_duration(dest / f"{key}.mp4")
        report[key] = (planned, actual)
        print(f"{key}: planned {planned:.2f}s, actual {actual:.3f}s")
    return report


def split_scene4(dest):
    src = dest / "04_dollars.mp4"
    cut = C.part_duration(C.NARRATION["04_dollars"][0])
    sh(["ffmpeg", "-y", "-v", "error", "-i", src, "-t", f"{cut:.3f}", *ENC, dest / "04a_dollars_part1.mp4"])
    sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{cut:.3f}", "-i", src, *ENC, dest / "04b_dollars_part2.mp4"])


def combine(dest):
    files = [dest / f"{k}.mp4" for k in C.SCENE_ORDER]
    durs = [probe_duration(f) for f in files]
    inputs = []
    for f in files:
        inputs += ["-i", f]
    parts, prev, acc = [], "[0:v]", 0.0
    for i in range(1, len(files)):
        acc += durs[i - 1] - C.CROSSFADE_SECONDS
        tag = f"[v{i}]"
        parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={C.CROSSFADE_SECONDS}:offset={acc:.3f}{tag}")
        prev = tag
    sh(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts),
        "-map", prev, *ENC, dest / "explainer_combined.mp4"])


def write_text():
    OUT.mkdir(exist_ok=True)
    lines = []
    for key in C.SCENE_ORDER:
        lines.append(SCENE_LABELS[key])
        parts = C.NARRATION[key]
        for i, part in enumerate(parts, 1):
            if len(parts) > 1:
                lines.append(f"Part {i}:")
            lines.append(" ".join(part))
        lines.append("")
    (OUT / "narration.txt").write_text("\n".join(lines))

    def ts(t):
        ms = round(t * 1000)
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    blocks, n = [], 0
    offsets = C.scene_offsets()
    for key in C.SCENE_ORDER:
        for start, end, sentence in C.sentence_timeline(key):
            n += 1
            blocks.append(f"{n}\n{ts(offsets[key] + start)} --> {ts(offsets[key] + end)}\n{sentence}\n")
    (OUT / "captions.srt").write_text("\n".join(blocks))
    print(f"wrote narration.txt and captions.srt ({n} captions, combined {C.combined_duration():.2f}s)")


def stills(dest):
    sdir = dest / "stills"
    sdir.mkdir(exist_ok=True)
    targets = [(k, dest / f"{k}.mp4") for k in C.SCENE_ORDER]
    if (dest / "04a_dollars_part1.mp4").exists():
        targets.insert(5, ("04a_dollars_part1", dest / "04a_dollars_part1.mp4"))
    for name, f in targets:
        t = max(probe_duration(f) - 0.3, 0)
        sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", f, "-frames:v", "1", sdir / f"{name}.png"])


EM_DASH = chr(0x2014)


def check_no_em_dash():
    bad = []
    for p in ROOT.rglob("*"):
        if ".venv" in p.parts or "build" in p.parts or not p.is_file():
            continue
        if EM_DASH in p.name:
            bad.append(str(p))
        if p.suffix in {".py", ".md", ".txt", ".srt"} and EM_DASH in p.read_text(encoding="utf-8"):
            bad.append(str(p))
    assert not bad, f"em dash found in: {bad}"
    print("em dash check: clean")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    write_text()
    if mode in ("preview", "final"):
        dest = render(mode)
        check_durations(dest)
        if mode == "final":
            split_scene4(dest)
            combine(dest)
            print(f"combined: planned {C.combined_duration():.2f}s, "
                  f"actual {probe_duration(dest / 'explainer_combined.mp4'):.3f}s")
        stills(dest)
    check_no_em_dash()
