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
# Scene 4 has two parts, and each part gets its own padding.
NARRATION = {
    "00_title": [[
        "From vendor noise to sourcing decisions: the Supplier Intelligence Hub.",
    ]],
    "01_vendors": [[
        "One sourcing portfolio can hold more than 150 vendors.",
        "Each dot is one vendor.",
        "Every vendor produces signals.",
        "Some need action now.",
        "The signals live in separate systems.",
        "No one person can watch all of them.",
    ]],
    "02_flow": [[
        "The Supplier Intelligence Hub collects these signals in one flow.",
        "First, it reads the sources.",
        "A weekly brief gives the full picture.",
        "An always-on early warning watches for sudden changes.",
        "Both send their output to one place.",
    ]],
    "03_posture": [[
        "Each signal gets a posture.",
        "There are four postures.",
        "Each one tells the team what to do next.",
        "Take Vendor X.",
        "It renews in 90 days, and the draft raises the price cap.",
        "The posture is Increase Leverage.",
        "The team uses timing and options.",
    ]],
    "04_dollars": [
        [
            "Now a worked example.",
            "Vendor X is fictional.",
            "All numbers are illustrative.",
            "Vendor X costs 1 million dollars a year.",
            "The old contract capped the yearly increase at 2 percent.",
            "That is at most 20,000 dollars.",
            "The new draft caps it at 6 percent.",
            "That is at most 60,000 dollars.",
        ],
        [
            "The gap is 40,000 dollars of added exposure each year.",
            "The action: ask to restore the 2 percent cap before the renewal date.",
        ],
    ],
    "05_agents": [[
        "Next, how the work happens.",
        "Everything runs in one Slack hub.",
        "Six agents work there.",
        "Each agent has one job.",
        "Together they turn signals into briefs, risk checks, deal support, spend views, and waste checks.",
    ]],
    "06_ahead": [[
        "Today the hub tells us what happened.",
        "Next, it tells us what is coming.",
        "We see the renewal, the risk, and the price change before they arrive.",
        "Early sight gives us time to act.",
        "Early action drives the business.",
    ]],
}

SCENE_ORDER = list(NARRATION.keys())
SCENE_HEADINGS = {
    "00_title": "Scene 0, title card",
    "01_vendors": "Scene 1, Too many vendors, too many places",
    "02_flow": "Scene 2, One flow, two speeds",
    "03_posture": "Scene 3, Every signal gets a posture",
    "04_dollars": "Scene 4, From signal to dollars",
    "05_agents": "Scene 5, Six agents, one hub",
    "06_ahead": "Scene 6, From reacting to seeing ahead",
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
GOLD_SIGNALS = 11
CORAL_SIGNALS = 7
FLAGGED = GOLD_SIGNALS + CORAL_SIGNALS
SOURCES = ["Contracts", "Renewal dates", "Security reviews", "Usage data", "Market news"]

# Scene 3: postures and the Vendor X example
POSTURES = [
    ("Protect Margin", "Hold price and terms"),
    ("Increase Leverage", "Use timing and options"),
    ("Reduce Hidden Risk", "Find gaps early"),
    ("Improve Resilience", "Plan backups and exits"),
]
VENDOR = "Vendor X"
RENEWAL_DAYS = 90
CHOSEN_POSTURE = "Increase Leverage"

# Scene 4: the worked example
SPEND = 1000000
OLD_CAP = 0.02
NEW_CAP = 0.06
old_max = SPEND * OLD_CAP
new_max = SPEND * NEW_CAP
gap = new_max - old_max

# Scene 5: agents
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
    n = NARRATION
    assert f"more than {VENDOR_COUNT} vendors" in n["01_vendors"][0][0]
    assert f"renews in {RENEWAL_DAYS} days" in " ".join(n["03_posture"][0])
    a, b = n["04_dollars"]
    assert f"{SPEND // 1000000} million dollars" in " ".join(a)
    assert f"{round(OLD_CAP * 100)} percent" in " ".join(a)
    assert f"{round(NEW_CAP * 100)} percent" in " ".join(a)
    assert f"{int(old_max):,} dollars" in " ".join(a)
    assert f"{int(new_max):,} dollars" in " ".join(a)
    assert f"{int(gap):,} dollars" in " ".join(b)
    assert f"{round(OLD_CAP * 100)} percent cap" in " ".join(b)

    # No em dash anywhere in narration.
    for parts in n.values():
        for part in parts:
            for s in part:
                assert "\u2014" not in s
                assert re.match(r"^.*[.!?]$", s), s


assert_data()
