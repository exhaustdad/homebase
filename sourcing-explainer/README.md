# Supplier Intelligence Hub explainer

A silent, 8 scene explainer (2:04) built with Manim Community Edition. It sells what a CFO wants: no surprises, faster yeses, and every yes backed by data. Three examples prove the promise, a data scene shows where each number comes from, and the close explains how AI fits in. Earlier versions are kept in `output/v2/` (2:31) and `output/v3/` (1:53). All data is synthetic and the vendor ("Vendor X") is fictional. Every scene carries the badge "Illustrative data only. Fictional vendor."

## Files

| File | What it holds |
|---|---|
| `config.py` | Palette, fonts, narration (one list of sentences per scene part), timing math, example numbers and asserts |
| `common.py` | Shared base scene: background, top-left title, corner badge, beat clock, automatic text overlap and off-screen check |
| `scenes.py` | The 8 scene classes |
| `build.py` | Renders scenes, splits any multi-part scene, joins with cross-fades, writes `narration.txt` and `captions.srt`, extracts still frames, checks for em dashes |
| `output/` | Final deliverables (see below) |

Outputs: `00_want.mp4` to `07_close.mp4`, `explainer_combined.mp4`, `narration.txt`, `captions.srt`, `stills/`. Previews (480p15) live in `output/preview/`.

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

A render fails on purpose if any text overlaps other text or leaves the frame, if an animation would run past its narration beat, or if the math or narration-to-screen asserts fail.

## Change the text

- **Narration:** edit `NARRATION` in `config.py`. Keep one sentence per list item. Scene length, animation beats, `narration.txt` and `captions.srt` all update from it (duration = words / 2.5 + 1 second per part). If a scene gets shorter, an animation may no longer fit before its beat and the render will stop with a clear message. Shorten that `run_time` in `scenes.py`.
- **Vendor Z's role:** `VENDOR_Z_ROLE` in `config.py` ("ad delivery" today; "payments" or "search" would suit a travel business). It feeds both the narration and the screen.
- **Scene titles:** `SCENE_TITLES` in `config.py`.
- **On-screen labels:** in `scenes.py` (for example the `stages` and `rules` lists). `SOURCES` is in `config.py`.
- **Example numbers:** Margin uses `SPEND`, `OLD_CAP`, `NEW_CAP`; growth uses `TYPICAL_WEEKS`, `HUB_WEEKS`; revenue uses `USAGE`, `DAYS_TO_PEAK`. The data scene reuses all three results. `PROMISE` holds the three promise lines. Change them in `config.py`, then update the asserts and the narration sentences to match. The asserts check that the narration and the screen agree.
- **Colors and fonts:** top of `config.py`. Titles use Noto Serif Display and labels use Inter. To swap the coral alert color for a brand red, change `CORAL`.

## Line up a voiceover

1. Record each scene from `output/narration.txt` at about 150 words per minute (2.5 words per second). Each sentence's start time inside its scene is in `captions.srt`, minus the scene's offset.
2. Easiest path: lay each scene's audio on the matching per-scene MP4, starting at 0:00. Every animation is keyed to the start of a narration sentence, and each scene ends with 1 second of quiet.
3. If a scene ever has two narration parts, `build.py final` also exports each part as `<scene>_partN.mp4`.
4. For the combined video, scenes overlap by 0.5 seconds at each cross-fade. Scene start times in the combined video are:

| Scene | Starts at |
|---|---|
| 0 want | 0:00.0 |
| 1 promise | 0:06.1 |
| 2 growth | 0:12.6 |
| 3 revenue | 0:32.7 |
| 4 margin | 0:52.8 |
| 5 data | 1:11.7 |
| 6 how | 1:29.0 |
| 7 close | 1:51.5 |

   `captions.srt` already uses this timeline, so it can be loaded straight onto `explainer_combined.mp4`.
5. If a real read runs longer or shorter than the plan, either trim the audio's pauses or change the wording in `config.py` and re-render. The video will retime itself.
