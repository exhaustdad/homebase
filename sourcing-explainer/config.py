"""Shared settings for the sourcing explainer: palette, fonts, narration, timing, data.

Every number shown on screen is defined here and checked by assert_data().
"""

import re

# Palette: a warm pin board. Cards are white with soft shadows, and each
# signal source has its own pastel so pins read as a board, not a chart.
BG = "#F7F4EF"
PANEL = "#FFFFFF"
SHADOW = "#E4DDD2"
INK = "#1B1B1F"
MUTED = "#6F6A64"
LINE = "#E3DDD4"
RED = "#E60023"
BLUE = "#3A7BD5"
GOLD = "#E3A008"
CORAL = "#E8634A"
TEAL = "#1F9E89"

# Fonts (installed system fonts; see README)
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
    "01_board": [[
        "Every week, 150 vendors pin fresh signals to our sourcing board.",
        "Contracts, renewals, security reviews, usage, market news.",
        "It piles up fast, and the important ones get buried.",
    ]],
    "02_sort": [[
        "The Supplier Intelligence Hub reads every pin and sorts the board.",
        "Most can wait.",
        "18 need action now, and one of them is our fictional Vendor X.",
    ]],
    "03_dollars": [[
        "Its renewal draft quietly lifts the price cap from 2 to 6 percent.",
        "On 1 million dollars of spend, the ceiling jumps from 20,000 to 60,000.",
        "That is 40,000 dollars a year.",
    ]],
    "04_plan": [[
        "The hub tags it Increase Leverage, with 90 days left before renewal.",
        "The team asks to restore the 2 percent cap and uses the time to compare options.",
    ]],
    "05_ahead": [[
        "Caught early, a surprise cost becomes a negotiation.",
        "Every week, the board gets sorted before it piles up, so nothing costly hides.",
        "Early action drives the business.",
    ]],
}

SCENE_ORDER = list(NARRATION.keys())
SCENE_HEADINGS = {
    "01_board": "Scene 1, Every week, a full board",
    "02_sort": "Scene 2, From noise to priorities",
    "03_dollars": "Scene 3, From a clause to dollars",
    "04_plan": "Scene 4, From a deadline to a plan",
    "05_ahead": "Scene 5, From reacting to seeing ahead",
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


# The board: one pin per vendor this week, colored by its source.
VENDOR_COUNT = 150
SOURCES = ["Contracts", "Renewals", "Security reviews", "Usage", "Market news"]
SOURCE_COLORS = ["#F6C9C0", "#F7DFA6", "#C9DCF2", "#CFE8CF", "#E2D4F0"]
BOARD_COLS = 15
SEED = 11

# How the hub sorts the board.
FLAGGED = 18      # act now
WATCH = 40
ON_TRACK = VENDOR_COUNT - FLAGGED - WATCH
LANES = [("Act now", FLAGGED, RED), ("Watch", WATCH, GOLD), ("On track", ON_TRACK, TEAL)]

# The Vendor X call.
VENDOR = "Vendor X"
RENEWAL_DAYS = 90
CHOSEN_POSTURE = "Increase Leverage"
PLAN_STEPS = [  # (day on the timeline, step)
    (8, "Ask to restore the 2% cap"),
    (45, "Compare options"),
    (82, "Decide before renewal"),
]

# The worked example.
SPEND = 1000000
OLD_CAP = 0.02
NEW_CAP = 0.06
old_max = SPEND * OLD_CAP
new_max = SPEND * NEW_CAP
gap = new_max - old_max


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
    assert ON_TRACK > 0 and FLAGGED + WATCH + ON_TRACK == VENDOR_COUNT
    assert len(SOURCES) == len(SOURCE_COLORS) == 5
    assert all(0 < d < RENEWAL_DAYS for d, _ in PLAN_STEPS)
    assert f"restore the {pct(OLD_CAP)} cap" in PLAN_STEPS[0][1]

    # Spoken numbers must match the variables.
    n = {k: " ".join(s for part in v for s in part) for k, v in NARRATION.items()}
    assert f"{VENDOR_COUNT} vendors" in n["01_board"]
    assert f"{FLAGGED} need action now" in n["02_sort"]
    assert VENDOR in n["02_sort"]
    a = n["03_dollars"]
    assert f"from {round(OLD_CAP * 100)} to {round(NEW_CAP * 100)} percent" in a
    assert f"{SPEND // 1000000} million dollars of spend" in a
    assert f"from {int(old_max):,} to {int(new_max):,}" in a
    assert f"{int(gap):,} dollars a year" in a
    b = n["04_plan"]
    assert f"tags it {CHOSEN_POSTURE}" in b
    assert f"{RENEWAL_DAYS} days left" in b
    assert f"restore the {round(OLD_CAP * 100)} percent cap" in b

    # No em dash anywhere in narration.
    for parts in NARRATION.values():
        for part in parts:
            for s in part:
                assert "\u2014" not in s
                assert re.match(r"^.*[.!?]$", s), s


assert_data()
