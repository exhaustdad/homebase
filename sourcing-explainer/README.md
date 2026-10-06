# Sourcing explainer video

A silent, 3Blue1Brown-style explainer of the Supplier Intelligence Hub, built with
Manim Community Edition. All data is synthetic and the vendor ("Vendor X") is fictional.
Every scene carries the badge "Illustrative data only. Fictional vendor."

## Files

| File | What it holds |
| --- | --- |
| `config.py` | Palette, fonts, narration (one Python list per scene), timing rule, and every number shown on screen, with asserts |
| `scenes.py` | The seven Manim scenes and the shared base class (badge, title, narration-locked timing) |
| `build.py` | Renders the scenes, splits scene 4, joins everything with cross-fades, writes captions and narration, saves stills |
| `output/` | Final MP4s, `explainer_combined.mp4`, `narration.txt`, `captions.srt`, and `stills/` |

## Requirements

* Python 3.10 or newer, FFmpeg, and the Pango and Cairo development headers
  (on Ubuntu: `apt-get install libpango1.0-dev libcairo2-dev pkg-config ffmpeg`).
* Manim Community Edition: `pip install manim` (built and tested with 0.21.0).
  On Debian or Ubuntu system Python, install into a virtual environment
  (`python3 -m venv .venv && .venv/bin/pip install manim`), since the system
  setuptools cannot build one of Manim's dependencies.
* Fonts: Newsreader (titles) and IBM Plex Sans (labels). Newsreader is on Google Fonts;
  IBM Plex Sans is in the Ubuntu package `fonts-ibm-plex`. To use other fonts, change
  `SERIF` and `SANS` in `config.py`. Text is rendered with `Text`, so LaTeX is not needed.

## Re-render

```bash
cd sourcing-explainer
python build.py --preview          # fast 480p, 15 fps pass into output/preview
python build.py                    # final 1920x1080, 30 fps pass into output
python build.py --only 04_dollars  # re-render one scene, then rebuild the joined files
```

`build.py` stops before rendering if any assert in `config.py` fails. It prints the
planned and rendered length of each scene so you can spot drift.

To render a single scene by hand: `manim -qh scenes.py DollarsScene`.

## Change the text

* **Narration**: edit `NARRATION` in `config.py`. Each scene is a list of parts, and each
  part is a list of sentences. Scene length, animation cue times, captions and
  `narration.txt` all follow from this, so nothing else needs to change.
* **Numbers**: change the variables in `config.py` (for example `SPEND`, `OLD_CAP`,
  `NEW_CAP`, `RENEWAL_DAYS`). Then update the asserts in `assert_data()`, which check
  both the math and that the narration speaks the same numbers.
* **On-screen labels**: titles and box labels live in `scenes.py` (titles as `TITLE`
  on each scene class) and in the lists in `config.py` (`SOURCES`, `POSTURES`, `AGENTS`).
  After any text change, run the preview and look at `output/preview/stills/` for
  overlaps.

## Timing rule

Each narration part lasts `words / 2.5 + 1` seconds (about 150 words per minute plus
1 second of padding). Half the padding sits before the first sentence and half after
the last, so the 0.5 second cross-fades fall in silence. Each animation step starts at
the start of a narration sentence (`self.at(i)` in `scenes.py`).

| Scene | File | Seconds |
| --- | --- | --- |
| 0 Title | `00_title.mp4` | 5.0 |
| 1 Too many vendors | `01_vendors.mp4` | 15.4 |
| 2 One flow, two speeds | `02_flow.mp4` | 15.8 |
| 3 Every signal gets a posture | `03_posture.mp4` | 18.6 |
| 4 From signal to dollars | `04_dollars.mp4` (halves `04a`, `04b`: 21.0 and 10.2) | 31.2 |
| 5 Six agents, one hub | `05_agents.mp4` | 15.0 |
| 6 From reacting to seeing ahead | `06_ahead.mp4` | 16.6 |

Scenes total 117.6 seconds. The joined video is 114.6 seconds, because each of the six
cross-fades overlaps two scenes by 0.5 seconds.

## Line up a voiceover

1. Record each scene's narration from `output/narration.txt`, at a calm pace near
   150 words per minute.
2. `output/captions.srt` gives every sentence's start and end in the joined video.
   Place each recorded sentence (or each scene's take) at its caption start time.
3. If a real take runs longer than its slot, either trim pauses, or raise the slot:
   lower `WORDS_PER_SECOND` in `config.py` (for example 2.3) and re-render. The
   animation cues and captions move with it.
4. To mux audio onto the joined video:
   `ffmpeg -i output/explainer_combined.mp4 -i voiceover.wav -c:v copy -c:a aac -shortest explainer_with_voice.mp4`
5. Or load per-scene MP4s and `captions.srt` into an editor; the per-scene files start
   at the same times the captions assume, minus the 0.5 second overlaps.
