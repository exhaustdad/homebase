"""Single source of truth: palette, fonts, narration, timing, and Scene 4 math.

Edit narration here. Scene durations, animation beats, narration.txt and
captions.srt are all derived from these lists.
"""

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

# Fonts. Newsreader is not installable here, so titles use Noto Serif Display.
# Labels use Inter, the closest open match to the Pinterest product type.
SERIF = "Noto Serif Display"
SANS = "Inter"

# Shape language: rounded "pin" cards and pill chips.
CARD_RADIUS = 0.28

BADGE_TEXT = "Illustrative data only. Fictional vendor."

# Timing
WORDS_PER_SECOND = 2.5
PADDING_SECONDS = 1.0
CROSSFADE_SECONDS = 0.5
FPS_FINAL = 30

# Vendor Z's role. Swap for another business (for example "payments" or "search").
VENDOR_Z_ROLE = "ad delivery"

# Narration. Each scene is a list of parts; each part is a list of sentences.
# Story order: value first (hook, growth, revenue, margin), then how AI fits in.
NARRATION = {
    "00_hook": [[
        "Most people think sourcing saves money.",
        "Great sourcing makes money.",
        "Here is what that looks like.",
    ]],
    "01_built": [[
        "I built the Supplier Intelligence Hub, an AI system that turns vendor noise into business decisions.",
    ]],
    "02_growth": [[
        "Start with growth.",
        "A product team needs Vendor Y, a fictional data partner, to launch.",
        "A typical sourcing cycle takes 12 weeks.",
        "With reviews and a shortlist already in the hub, it takes 4 weeks.",
        "The launch ships 8 weeks earlier.",
        "That is 8 more weeks of revenue.",
    ]],
    "03_revenue": [[
        "Then revenue.",
        f"Vendor Z, also fictional, supports {VENDOR_Z_ROLE}.",
        "Usage is at 85 percent of capacity.",
        "The vendor was just acquired.",
        "Peak season is 120 days out.",
        "Alone, each signal is noise.",
        "Together, they say act now.",
        "The team locks in capacity and a backup before the peak.",
    ]],
    "04_margin": [[
        "And yes, margin.",
        "Vendor X's renewal draft raises the price cap from 2 percent to 6 percent.",
        "On 1 million dollars of spend, that is 40,000 dollars a year.",
        "The move: restore the 2 percent cap before renewal.",
    ]],
    "05_how": [[
        "Here is how AI fits in.",
        "One portfolio holds more than 150 vendors, with signals spread across five systems.",
        "No person can watch them all.",
        "AI agents read every contract, renewal, review, and news item.",
        "They score each signal and assign a posture.",
        "They draft the brief and the next move.",
        "A person makes the call.",
    ]],
    "06_rules": [[
        "Three rules make it work.",
        "AI does the reading, and people make the decisions.",
        "Every number traces back to a source.",
        "And it runs in Slack, where the team already works.",
    ]],
    "07_close": [[
        "That is the shift, from reacting to seeing ahead.",
        "Sourcing becomes a growth function.",
        "Early action drives the business.",
    ]],
}

SCENE_ORDER = list(NARRATION.keys())
SCENE_TITLES = {
    "00_hook": None,
    "01_built": None,
    "02_growth": "Speed is revenue",
    "03_revenue": "Looking around the corner",
    "04_margin": "From signal to dollars",
    "05_how": "How AI fits in",
    "06_rules": "Three rules",
    "07_close": "From reacting to seeing ahead",
}


def words(text):
    return len(text.split())


def sentence_seconds(sentence):
    return words(sentence) / WORDS_PER_SECOND


def part_duration(part):
    return sum(sentence_seconds(s) for s in part) + PADDING_SECONDS


def scene_duration(key):
    return sum(part_duration(p) for p in NARRATION[key])


def sentence_timeline(key):
    """(start, end, sentence) for every sentence, in seconds from scene start."""
    out, offset = [], 0.0
    for part in NARRATION[key]:
        t = offset
        for s in part:
            d = sentence_seconds(s)
            out.append((t, t + d, s))
            t += d
        offset += part_duration(part)
    return out


def beats(key):
    """Start time of each sentence. Animations are keyed to these."""
    return [round(start, 6) for start, _, _ in sentence_timeline(key)]


def scene_offsets():
    """Start time of each scene inside the cross-faded combined video."""
    offsets, t = {}, 0.0
    for i, key in enumerate(SCENE_ORDER):
        offsets[key] = t
        t += scene_duration(key) - CROSSFADE_SECONDS
    return offsets


def combined_duration():
    total = sum(scene_duration(k) for k in SCENE_ORDER)
    return total - CROSSFADE_SECONDS * (len(SCENE_ORDER) - 1)


# Vendor portfolio (How AI fits in)
GRID_COLS, GRID_ROWS = 15, 10
VENDOR_COUNT = GRID_COLS * GRID_ROWS
FLAGGED_GOLD, FLAGGED_CORAL = 12, 6
FLAGGED = FLAGGED_GOLD + FLAGGED_CORAL
SOURCES = ["Contracts", "Renewal dates", "Security reviews", "Usage data", "Market news"]
assert VENDOR_COUNT == 150
assert FLAGGED == 18
assert len(SOURCES) == 5

# Margin math (Vendor X)
SPEND = 1000000
OLD_CAP = 0.02
NEW_CAP = 0.06
old_max = SPEND * OLD_CAP
new_max = SPEND * NEW_CAP
gap = new_max - old_max
assert old_max == 20000
assert new_max == 60000
assert gap == 40000
assert new_max == 3 * old_max  # the coral bar must be three times the blue bar


def usd(v):
    assert v == int(v), f"non-integer dollar amount {v}"
    return f"${int(v):,}"


def pct(v):
    p = round(v * 100)
    assert abs(v * 100 - p) < 1e-9, f"non-integer percent {v}"
    return f"{p}%"


assert usd(SPEND) == "$1,000,000"
assert usd(old_max) == "$20,000" and usd(new_max) == "$60,000" and usd(gap) == "$40,000"
assert pct(OLD_CAP) == "2%" and pct(NEW_CAP) == "6%"

# Growth data (Vendor Y), weeks only, no revenue figure
TYPICAL_WEEKS = 12
HUB_WEEKS = 4
WEEKS_SAVED = TYPICAL_WEEKS - HUB_WEEKS
assert WEEKS_SAVED == 8

# Revenue data (Vendor Z)
USAGE = 0.85
DAYS_TO_PEAK = 120

# The narration must agree with the numbers on screen.
_j = lambda k: " ".join(s for p in NARRATION[k] for s in p)
_m, _g, _r, _h = _j("04_margin"), _j("02_growth"), _j("03_revenue"), _j("05_how")
assert f"{int(gap):,} dollars" in _m
assert f"{round(OLD_CAP * 100)} percent to {round(NEW_CAP * 100)} percent" in _m
assert f"restore the {round(OLD_CAP * 100)} percent cap" in _m
assert f"{SPEND // 1000000} million dollars" in _m
assert f"takes {TYPICAL_WEEKS} weeks" in _g and f"takes {HUB_WEEKS} weeks" in _g
assert f"{WEEKS_SAVED} weeks earlier" in _g and f"{WEEKS_SAVED} more weeks" in _g
assert f"{round(USAGE * 100)} percent" in _r and f"{DAYS_TO_PEAK} days" in _r
assert f"more than {VENDOR_COUNT} vendors" in _h and "five systems" in _h
