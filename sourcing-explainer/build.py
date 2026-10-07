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
    "00_want": "S00Want",
    "01_promise": "S01Promise",
    "02_growth": "S02Growth",
    "03_revenue": "S03Revenue",
    "04_margin": "S04Margin",
    "05_data": "S05Data",
    "06_how": "S06How",
    "07_close": "S07Close",
}
SCENE_LABELS = {k: f"Scene {int(k[:2])}, " + (C.SCENE_TITLES[k] or {"00_want": "what the CFO wants", "01_promise": "the promise", "07_close": "close"}.get(k, "title card"))
                for k in CLASSES}
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


def split_parts(dest):
    """Export each part of a multi-part scene as its own timed clip."""
    for key, parts in C.NARRATION.items():
        if len(parts) < 2:
            continue
        t = 0.0
        for i, part in enumerate(parts):
            d = C.part_duration(part)
            sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", dest / f"{key}.mp4",
                "-t", f"{d:.3f}", *ENC, dest / f"{key}_part{i + 1}.mp4"])
            t += d


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
    write_heygen()


HEYGEN_NAMES = {
    "00_want": "What the CFO wants",
    "01_promise": "The promise",
    "02_growth": "A faster yes",
    "03_revenue": "No surprises",
    "04_margin": "Caught in the draft",
    "05_data": "Backed by data",
    "06_how": "How AI fits in",
    "07_close": "Close",
}


def write_heygen():
    """A HeyGen-ready script: one block per scene, with pauses that match the video's timing."""
    def mmss(t):
        m, s = divmod(t, 60)
        return f"{int(m)}:{s:04.1f}"

    offsets, keys = C.scene_offsets(), C.SCENE_ORDER
    # Speech fills each scene; the gap to the next scene's first word is
    # the 1 s padding minus the 0.5 s cross-fade.
    gap = C.PADDING_SECONDS - C.CROSSFADE_SECONDS
    brk = f'<break time="{gap:g}s"/>'
    speech_total = sum(C.sentence_seconds(x) for k in keys for p in C.NARRATION[k] for x in p)

    out = [
        "HEYGEN SCRIPT: Supplier Intelligence Hub (v4)",
        "",
        f"Target pace: {C.WORDS_PER_SECOND * 60:g} words per minute. Total speech {speech_total:.1f}s, "
        f"video {C.combined_duration():.1f}s.",
        f'Pauses use HeyGen break tags. If your editor shows {brk} as text, delete it and use the',
        f"editor's pause button with the same length ({gap:g} seconds).",
        "",
        "=" * 72,
        "OPTION A: ONE SCENE. Paste this whole block into a single HeyGen scene.",
        "=" * 72,
        "",
    ]
    paras = []
    for i, k in enumerate(keys):
        text = " ".join(x for p in C.NARRATION[k] for x in p)
        paras.append(text + ("" if i == len(keys) - 1 else f" {brk}"))
    out += ["\n\n".join(paras), ""]

    out += [
        "=" * 72,
        "OPTION B: EIGHT SCENES. One HeyGen scene per video scene (best sync).",
        "Use output/<scene>.mp4 as each scene's background if you want the avatar over the animation.",
        f"Each scene ends with a {C.PADDING_SECONDS:g} second break so the scene runs as long as its MP4.",
        "=" * 72,
        "",
    ]
    for i, k in enumerate(keys):
        sentences = [x for p in C.NARRATION[k] for x in p]
        speech = sum(C.sentence_seconds(x) for x in sentences)
        start = offsets[k]
        out.append(f"SCENE {i + 1} of {len(keys)}: {HEYGEN_NAMES[k]}  |  file {k}.mp4  |  "
                   f"starts {mmss(start)} in the combined video  |  speech {speech:.1f}s of {C.scene_duration(k):.1f}s")
        out.append(" ".join(sentences) + f' <break time="{C.PADDING_SECONDS:g}s"/>')
        out.append("")
        out.append("  Cue sheet (each line should start at this time in the combined video):")
        for t0, _, x in C.sentence_timeline(k):
            out.append(f"    {mmss(start + t0)}  {x}")
        out.append("")

    out += [
        "=" * 72,
        "HOW TO KEEP IT IN SYNC",
        "=" * 72,
        f"1. Pick a calm, measured voice and set speed so Option A runs about {speech_total + gap * (len(keys) - 1):.0f} seconds",
        "   (speech plus pauses). Faster than that and the voice gets ahead of the visuals.",
        "2. Spot-check three cues against the cue sheet: the first line of Scene 3, the line",
        "   \"No source, no number.\" and the final \"Backed by data.\" Within half a second is fine.",
        "3. If the voice drifts, nudge the HeyGen speed slider, or lengthen the break tags slightly.",
        "4. For exact sync, use Option B: each scene's audio starts at 0:00 on its own MP4, so drift",
        "   can never build up across scenes.",
        "5. Read numbers as written: \"40,000 dollars\", \"85 percent\", \"120 days\". Keep \"CFO\" as letters.",
    ]
    (OUT / "heygen_script.txt").write_text("\n".join(out) + "\n")
    print("wrote heygen_script.txt")


def stills(dest):
    sdir = dest / "stills"
    sdir.mkdir(exist_ok=True)
    targets = [(k, dest / f"{k}.mp4") for k in C.SCENE_ORDER]
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
            split_parts(dest)
            combine(dest)
            print(f"combined: planned {C.combined_duration():.2f}s, "
                  f"actual {probe_duration(dest / 'explainer_combined.mp4'):.3f}s")
        stills(dest)
    check_no_em_dash()
