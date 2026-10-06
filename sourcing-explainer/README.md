# Supplier Intelligence Hub explainer

A silent, 7 scene explainer built with Manim Community Edition. All data is synthetic and the vendor ("Vendor X") is fictional. Every scene carries the badge "Illustrative data only. Fictional vendor."

## Files

| File | What it holds |
|---|---|
| `config.py` | Palette, fonts, narration (one list of sentences per scene part), timing math, Scene 4 numbers and asserts |
| `common.py` | Shared base scene: background, top-left title, corner badge, beat clock, automatic text overlap and off-screen check |
| `scenes.py` | The 7 scene classes |
| `build.py` | Renders scenes, splits Scene 4, joins with cross-fades, writes `narration.txt` and `captions.srt`, extracts still frames, checks for em dashes |
| `output/` | Final deliverables (see below) |

Outputs: `00_title.mp4` to `06_ahead.mp4`, `04a_dollars_part1.mp4`, `04b_dollars_part2.mp4`, `explainer_combined.mp4`, `narration.txt`, `captions.srt`, `stills/`. Previews (480p15) live in `output/preview/`.

## Re-render

One-time setup (Ubuntu or Debian):

```
sudo apt-get install -y libpango1.0-dev libcairo2-dev pkg-config ffmpeg fonts-noto-core
python3 -m venv .venv
.venv/bin/pip install manim
```

Inter must also be installed for labels. LaTeX is not needed.

Then, from this folder:

```
.venv/bin/python build.py preview   # fast 480p15 pass, output/preview/
.venv/bin/python build.py final     # 1920x1080 at 30 fps, all deliverables
.venv/bin/python build.py text      # only narration.txt and captions.srt
```

A render fails on purpose if any text overlaps other text or leaves the frame, if an animation would run past its narration beat, or if the Scene 4 math asserts fail.

## Change the text

- **Narration:** edit `NARRATION` in `config.py`. Keep one sentence per list item. Scene length, animation beats, `narration.txt` and `captions.srt` all update from it (duration = words / 2.5 + 1 second per part). If a scene gets shorter, an animation may no longer fit before its beat and the render will stop with a clear message. Shorten that `run_time` in `scenes.py`.
- **Scene titles:** `SCENE_TITLES` in `config.py`.
- **On-screen labels:** in `scenes.py` (for example `SOURCES`, `postures`, `agents`).
- **Scene 4 numbers:** change `SPEND`, `OLD_CAP`, `NEW_CAP` in `config.py`, then update the asserts and the narration sentences to match. The asserts check that the narration and the screen agree.
- **Colors and fonts:** top of `config.py`. Titles use Noto Serif Display and labels use Inter. To swap the coral alert color for a brand red, change `CORAL`.

## Line up a voiceover

1. Record each scene from `output/narration.txt` at about 150 words per minute (2.5 words per second). Each sentence's start time inside its scene is in `captions.srt`, minus the scene's offset.
2. Easiest path: lay each scene's audio on the matching per-scene MP4, starting at 0:00. Every animation is keyed to the start of a narration sentence, and each scene ends with 1 second of quiet.
3. For Scene 4, use `04a_dollars_part1.mp4` and `04b_dollars_part2.mp4` if you record the two parts separately.
4. For the combined video, scenes overlap by 0.5 seconds at each cross-fade. Scene start times in the combined video are:

| Scene | Starts at |
|---|---|
| 0 | 0:00.0 |
| 1 | 0:04.5 |
| 2 | 0:19.4 |
| 3 | 0:34.7 |
| 4 | 0:52.8 (part 2 at 1:13.8) |
| 5 | 1:23.5 |
| 6 | 1:38.0 |

   `captions.srt` already uses this timeline, so it can be loaded straight onto `explainer_combined.mp4`.
5. If a real read runs longer or shorter than the plan, either trim the audio's pauses or change the wording in `config.py` and re-render. The video will retime itself.
