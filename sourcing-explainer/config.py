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
# Only Scene 4 has two parts.
NARRATION = {
    "00_title": [[
        "From vendor noise to sourcing decisions: the Supplier Intelligence Hub.",
    ]],
    "01_vendors": [[
        "One sourcing portfolio can hold more than 150 vendors.",
        "Each dot is one vendor.",
        "Some need action now.",
        "But the signals live in separate systems.",
        "No one can watch them all.",
    ]],
    "02_flow": [[
        "The Supplier Intelligence Hub pulls these signals into one flow.",
        "A weekly brief gives the full picture.",
        "An always-on early warning catches sudden changes.",
        "Both land in one place.",
    ]],
    "03_posture": [[
        "Every signal gets a posture, and each posture tells the team what to do next.",
        "Take Vendor X.",
        "It renews in 90 days, and the draft raises the price cap.",
        "The posture: Increase Leverage.",
        "Use timing and options.",
    ]],
    "04_dollars": [
        [
            "Here is what that is worth.",
            "Vendor X is fictional, and all numbers are illustrative.",
            "Vendor X costs 1 million dollars a year.",
            "The old cap on yearly increases was 2 percent: at most 20,000 dollars.",
            "The draft cap is 6 percent: at most 60,000 dollars.",
        ],
        [
            "That is 40,000 dollars of added exposure every year.",
            "The move: restore the 2 percent cap before renewal.",
        ],
    ],
    "05_speed": [[
        "Savings are only half the story.",
        "Speed is revenue.",
        "A product team needs Vendor Y, a fictional data partner, to launch.",
        "A typical sourcing cycle takes 12 weeks.",
        "With reviews and a shortlist already in the hub, it takes 4 weeks.",
        "The launch ships 8 weeks earlier.",
        "That is 8 more weeks of revenue.",
    ]],
    "06_corner": [[
        "Now look around the corner.",
        f"Vendor Z, also fictional, supports {VENDOR_Z_ROLE}.",
        "Usage is at 85 percent of capacity.",
        "The vendor was just acquired.",
        "Peak season is 120 days out.",
        "Each signal alone is noise.",
        "Together, they say act now.",
        "The team locks in capacity and a backup before the peak.",
        "Peak revenue is protected.",
    ]],
    "07_agents": [[
        "Behind it, six agents work in one Slack hub.",
        "Each has one job: briefs, risk checks, deal support, spend views, and waste checks.",
    ]],
    "08_levers": [[
        "Three levers, one hub.",
        "Protect margin: 40,000 dollars a year.",
        "Speed growth: launches 8 weeks sooner.",
        "Protect revenue: 120 days of warning.",
    ]],
    "09_ahead": [[
        "Today the hub tells us what happened.",
        "Next, it tells us what is coming: the renewal, the risk, and the opportunity, before they arrive.",
        "Early sight buys time to act.",
        "Early action drives the business.",
    ]],
}

SCENE_ORDER = list(NARRATION.keys())
SCENE_TITLES = {
    "00_title": None,
    "01_vendors": "Too many vendors, too many places",
    "02_flow": "One flow, two speeds",
    "03_posture": "Every signal gets a posture",
    "04_dollars": "From signal to dollars",
    "05_speed": "Speed is revenue",
    "06_corner": "Looking around the corner",
    "07_agents": "Six agents, one hub",
    "08_levers": "Three levers, one hub",
    "09_ahead": "From reacting to seeing ahead",
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


# Scene 1 data
GRID_COLS, GRID_ROWS = 15, 10
VENDOR_COUNT = GRID_COLS * GRID_ROWS
FLAGGED_GOLD, FLAGGED_CORAL = 12, 6
FLAGGED = FLAGGED_GOLD + FLAGGED_CORAL
assert VENDOR_COUNT == 150
assert FLAGGED == 18

# Scene 3 data
RENEWAL_DAYS = 90

# Scene 4 math
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

# The narration must agree with the numbers on screen.
_n4 = " ".join(NARRATION["04_dollars"][0] + NARRATION["04_dollars"][1])
assert f"{int(old_max):,} dollars" in _n4
assert f"{int(new_max):,} dollars" in _n4
assert f"{int(gap):,} dollars" in _n4
assert f"{round(OLD_CAP * 100)} percent" in _n4
assert f"{round(NEW_CAP * 100)} percent" in _n4
assert f"{SPEND // 1000000} million dollars" in _n4
assert f"more than {VENDOR_COUNT} vendors" in NARRATION["01_vendors"][0][0]
assert f"{RENEWAL_DAYS} days" in NARRATION["03_posture"][0][2]

# Scene 5 data (weeks only, no revenue figure)
TYPICAL_WEEKS = 12
HUB_WEEKS = 4
WEEKS_SAVED = TYPICAL_WEEKS - HUB_WEEKS
assert WEEKS_SAVED == 8
_n5 = " ".join(NARRATION["05_speed"][0])
assert f"takes {TYPICAL_WEEKS} weeks" in _n5 and f"takes {HUB_WEEKS} weeks" in _n5
assert f"{WEEKS_SAVED} weeks earlier" in _n5 and f"{WEEKS_SAVED} more weeks" in _n5

# Scene 6 data
USAGE = 0.85
DAYS_TO_PEAK = 120
_n6 = " ".join(NARRATION["06_corner"][0])
assert f"{round(USAGE * 100)} percent" in _n6 and f"{DAYS_TO_PEAK} days" in _n6

# Scene 8 pulls its numbers from Scenes 4 to 6
_n8 = " ".join(NARRATION["08_levers"][0])
assert f"{int(gap):,} dollars" in _n8
assert f"{WEEKS_SAVED} weeks" in _n8
assert f"{DAYS_TO_PEAK} days" in _n8
