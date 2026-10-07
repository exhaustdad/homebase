"""Shared settings for the sourcing explainer: palette, fonts, narration, timing, data.

Every number shown on screen is defined here and checked by assert_data().
"""

import re

# Palette
BG = "#0E1422"
PANEL = "#17213A"
INK = "#E9EDF5"
MUTED = "#8A96AD"
LINE = "#2A3550"
BLUE = "#5AA9E6"
GOLD = "#F2C14E"
CORAL = "#EF7A63"
TEAL = "#56C3A5"

# Fonts (installed system fonts; see README for fallbacks)
SERIF = "Newsreader"
SANS = "IBM Plex Sans"

BADGE_TEXT = "Illustrative data only. Fictional vendor."

# Timing rule: words / WORDS_PER_SECOND + PADDING seconds.
# Half of the padding leads the narration and half trails it, so the
# 0.5 second cross-fades between scenes never land on a spoken sentence.
WORDS_PER_SECOND = 2.5
PADDING = 1.0
LEAD = PADDING / 2
CROSSFADE = 0.5

# Narration. Each entry is one narration part; each part is a list of sentences.
# A scene with more than one part gets padding per part and is also exported
# as one file per part. Total runtime is about one minute.
NARRATION = {
    "00_title": [[
        "From vendor noise to sourcing decisions.",
    ]],
    "01_problem": [[
        "One portfolio holds 150 vendors, with signals in five separate systems.",
        "18 need action now.",
        "No one can see them all.",
    ]],
    "02_flow": [[
        "The hub reads every source.",
        "A weekly brief and an always-on warning feed one Slack hub with six agents.",
        "Every signal gets one of four postures that say what to do next.",
    ]],
    "03_dollars": [[
        "Take Vendor X: fictional, with 1 million dollars of annual spend.",
        "Its renewal draft raises the price cap from 2 to 6 percent.",
        "The most it can add each year rises from 20,000 to 60,000 dollars.",
        "That is 40,000 dollars of new exposure.",
    ]],
    "04_action": [[
        "With 90 days to renewal, the posture is Increase Leverage: ask to restore the 2 percent cap.",
        "The hub flags renewals, risks, and price changes early.",
        "Early sight turns a surprise cost into a negotiation.",
        "Early action drives the business.",
    ]],
}

SCENE_ORDER = list(NARRATION.keys())
SCENE_HEADINGS = {
    "00_title": "Scene 0, title card",
    "01_problem": "Scene 1, Too many vendors, too many places",
    "02_flow": "Scene 2, One flow, four postures",
    "03_dollars": "Scene 3, From signal to dollars",
    "04_action": "Scene 4, Early sight, better terms",
}


def word_count(text):
    return len(text.split())


def sentence_seconds(text):
    return word_count(text) / WORDS_PER_SECOND


def part_duration(sentences):
    return sum(sentence_seconds(s) for s in sentences) + PADDING


def scene_timing(key):
    """Return (duration, cues, part_starts) for one scene.

    cues is a list of (start, end, sentence) relative to the start of the scene.
    part_starts is the start time of each narration part.
    """
    t = 0.0
    cues = []
    part_starts = []
    for part in NARRATION[key]:
        part_starts.append(t)
        s = t + LEAD
        for sentence in part:
            e = s + sentence_seconds(sentence)
            cues.append((s, e, sentence))
            s = e
        t += part_duration(part)
    return t, cues, part_starts


def scene_duration(key):
    return scene_timing(key)[0]


# Scene 1: vendor grid
GRID_COLS = 15
GRID_ROWS = 10
VENDOR_COUNT = GRID_COLS * GRID_ROWS
FLAGGED = 18  # vendors that need action now
SOURCES = ["Contracts", "Renewal dates", "Security reviews", "Usage data", "Market news"]

# Scene 2: postures; scene 4: the Vendor X call
POSTURES = [
    ("Protect Margin", "Hold price and terms"),
    ("Increase Leverage", "Use timing and options"),
    ("Reduce Hidden Risk", "Find gaps early"),
    ("Improve Resilience", "Plan backups and exits"),
]
VENDOR = "Vendor X"
RENEWAL_DAYS = 90
CHOSEN_POSTURE = "Increase Leverage"

# Scene 3: the worked example
SPEND = 1000000
OLD_CAP = 0.02
NEW_CAP = 0.06
old_max = SPEND * OLD_CAP
new_max = SPEND * NEW_CAP
gap = new_max - old_max

# Scene 2: agents
AGENTS = [
    ("Sourcing Signal", "Weekly brief"),
    ("Category Brief", "Category view"),
    ("Supplier Risk", "Risk checks"),
    ("Deal Desk", "Deal support"),
    ("Spend Pulse", "Spend view"),
    ("Ghostbuster", "Waste checks"),
]


def money(x):
    """Format a dollar amount, refusing anything that is not a whole dollar."""
    assert float(x).is_integer(), f"{x} is not a whole dollar amount"
    return f"${int(x):,}"


def pct(x):
    """Format a cap as a whole percent, refusing anything that would round."""
    p = x * 100
    assert abs(p - round(p)) < 1e-9, f"{x} is not a whole percent"
    return f"{round(p)}%"


def assert_data():
    """Check every on-screen number and its link to the narration."""
    assert old_max == 20000, old_max
    assert new_max == 60000, new_max
    assert gap == 40000, gap
    assert new_max == 3 * old_max  # the 6% bar is three times the 2% bar

    assert VENDOR_COUNT == 150
    assert FLAGGED == 18
    assert len(SOURCES) == 5
    assert len(POSTURES) == 4
    assert CHOSEN_POSTURE in [p[0] for p in POSTURES]
    assert len(AGENTS) == 6

    # Spoken numbers must match the variables.
    words = {4: "four", 5: "five", 6: "six"}
    n = {k: " ".join(s for part in v for s in part) for k, v in NARRATION.items()}
    assert f"{VENDOR_COUNT} vendors" in n["01_problem"]
    assert f"{words[len(SOURCES)]} separate systems" in n["01_problem"]
    assert f"{FLAGGED} need action now" in n["01_problem"]
    assert f"{words[len(AGENTS)]} agents" in n["02_flow"]
    assert f"{words[len(POSTURES)]} postures" in n["02_flow"]
    a = n["03_dollars"]
    assert f"{SPEND // 1000000} million dollars" in a
    assert f"from {round(OLD_CAP * 100)} to {round(NEW_CAP * 100)} percent" in a
    assert f"from {int(old_max):,} to {int(new_max):,} dollars" in a
    assert f"{int(gap):,} dollars of new exposure" in a
    b = n["04_action"]
    assert f"{RENEWAL_DAYS} days to renewal" in b
    assert f"posture is {CHOSEN_POSTURE}" in b
    assert f"restore the {round(OLD_CAP * 100)} percent cap" in b

    # No em dash anywhere in narration.
    for parts in NARRATION.values():
        for part in parts:
            for s in part:
                assert "\u2014" not in s
                assert re.match(r"^.*[.!?]$", s), s


assert_data()
