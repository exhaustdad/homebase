"""Render the scenes and write every output file.

    python build.py --preview     fast low-quality pass into output/preview
    python build.py               final 1920x1080, 30 fps pass into output

Steps: check the data, render each scene, export one file per narration part
for any scene that has several, join all scenes with 0.5 second cross-fades,
write narration.txt and captions.srt, and save one still frame per scene.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import config
from config import CROSSFADE, NARRATION, SCENE_HEADINGS, SCENE_ORDER, scene_timing

HERE = Path(__file__).resolve().parent
SCENE_CLASSES = {
    "00_title": "TitleScene",
    "01_problem": "ProblemScene",
    "02_flow": "FlowScene",
    "03_dollars": "DollarsScene",
    "04_action": "ActionScene",
}
QUALITY = {
    "preview": {"flags": ["-ql"], "folder": "480p15", "fps": 15},
    "final": {"flags": ["-qh", "--frame_rate", "30"], "folder": "1080p30", "fps": 30},
}


def run(cmd):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=HERE)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def render(key, mode, media_dir, out_dir):
    q = QUALITY[mode]
    cls = SCENE_CLASSES[key]
    run([sys.executable, "-m", "manim", *q["flags"], "--disable_caching",
         "--media_dir", str(media_dir), "scenes.py", cls])
    src = media_dir / "videos" / "scenes" / q["folder"] / f"{cls}.mp4"
    dst = out_dir / f"{key}.mp4"
    shutil.copyfile(src, dst)
    return dst


def split_parts(key, out_dir):
    """Export one file per narration part for scenes that have more than one."""
    _, _, starts = scene_timing(key)
    if len(starts) < 2:
        return []
    src = out_dir / f"{key}.mp4"
    ends = starts[1:] + [None]
    outs = []
    for i, (s, e) in enumerate(zip(starts, ends), 1):
        dst = out_dir / f"{key}_part{i}.mp4"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{s:.3f}", "-i", str(src)]
        if e is not None:
            cmd += ["-t", f"{e - s:.3f}"]
        run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(dst)])
        outs.append(dst)
    return outs


def scene_offsets(durations):
    """Start time of each scene inside the combined video."""
    offsets, t = [], 0.0
    for d in durations:
        offsets.append(t)
        t += d - CROSSFADE
    return offsets


def combine(paths, durations, fps, out_path):
    offsets = scene_offsets(durations)
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for p in paths:
        cmd += ["-i", str(p)]
    chain, prev = [], "[0:v]"
    for i in range(1, len(paths)):
        label = f"[v{i}]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={CROSSFADE}:offset={offsets[i]:.4f}{label}")
        prev = label
    cmd += ["-filter_complex", ";".join(chain), "-map", prev, "-r", str(fps),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(out_path)]
    run(cmd)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_captions(durations, path):
    offsets = scene_offsets(durations)
    lines, n = [], 1
    for key, off in zip(SCENE_ORDER, offsets):
        _, cues, _ = scene_timing(key)
        for start, end, sentence in cues:
            lines += [str(n), f"{srt_time(off + start)} --> {srt_time(off + end)}", sentence, ""]
            n += 1
    path.write_text("\n".join(lines), encoding="utf-8")


def write_narration(path):
    out = []
    for key in SCENE_ORDER:
        dur, _, _ = scene_timing(key)
        out.append(f"{SCENE_HEADINGS[key]} ({dur:.1f} s)")
        parts = NARRATION[key]
        for i, part in enumerate(parts, 1):
            label = f"Part {i}: " if len(parts) > 1 else ""
            out.append(label + " ".join(part))
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


def stills(paths, out_dir):
    """Save a frame near the end of each scene, when everything is on screen."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in paths:
        t = max(probe_duration(p) - 0.6, 0)
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(p),
             "-frames:v", "1", str(out_dir / f"{p.stem}.png")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="fast low-quality render")
    ap.add_argument("--only", nargs="*", help="scene keys to render, for example 03_dollars")
    args = ap.parse_args()

    config.assert_data()
    mode = "preview" if args.preview else "final"
    out_dir = HERE / "output" / ("preview" if args.preview else "")
    out_dir.mkdir(parents=True, exist_ok=True)
    media_dir = HERE / "media"

    keys = args.only or SCENE_ORDER
    for key in keys:
        render(key, mode, media_dir, out_dir)

    paths = [out_dir / f"{k}.mp4" for k in SCENE_ORDER]
    planned = [scene_timing(k)[0] for k in SCENE_ORDER]
    actual = [probe_duration(p) for p in paths]
    frame = 1 / QUALITY[mode]["fps"]
    print("\nscene            planned   rendered")
    for k, a, b in zip(SCENE_ORDER, planned, actual):
        flag = "" if abs(a - b) <= 1.5 * frame else "  MISMATCH"
        print(f"{k:15s} {a:8.2f}s {b:9.2f}s{flag}")

    for key in SCENE_ORDER:
        split_parts(key, out_dir)
    combined = out_dir / "explainer_combined.mp4"
    combine(paths, planned, QUALITY[mode]["fps"], combined)
    write_captions(planned, out_dir / "captions.srt")
    write_narration(out_dir / "narration.txt")
    stills(paths, out_dir / "stills")
    total = sum(planned) - CROSSFADE * (len(planned) - 1)
    print(f"\ncombined planned {total:.2f}s, rendered {probe_duration(combined):.2f}s")


if __name__ == "__main__":
    main()
