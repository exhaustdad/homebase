"""Manim scenes for the sourcing explainer.

The story follows one week of a sourcing pin board: it fills up, the hub sorts
it, one pin (the fictional Vendor X) turns into dollars, then into a plan.

Render with build.py, or directly:
    manim -ql scenes.py BoardScene
"""

import random

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, UR, DEGREES,
    AnimationGroup, Circle, Create, Dot, FadeIn, FadeOut, GrowFromEdge, LaggedStart,
    Line, Rectangle, ReplacementTransform, RoundedRectangle, Scene, Text, Transform,
    ValueTracker, VGroup, VMobject, always_redraw, config as manim_config,
    rate_functions as rf,
)

from config import (
    BADGE_TEXT, BG, BLUE, BOARD_COLS, CHOSEN_POSTURE, CORAL, GOLD, INK, LANES, LINE,
    MUTED, NEW_CAP, OLD_CAP, PANEL, PLAN_STEPS, RED, RENEWAL_DAYS, SANS, SEED,
    SERIF, SHADOW, SOURCE_COLORS, SOURCES, SPEND, TEAL, VENDOR, VENDOR_COUNT,
    gap, money, new_max, old_max, pct, scene_timing,
)

manim_config.background_color = BG

X_LEFT, X_RIGHT = -6.55, 6.55


# Text ----------------------------------------------------------------------

_CAP = {}


def _text(text, font, size, color, weight):
    t = Text(text, font=font, font_size=size, color=color, weight=weight)
    key = (font, size, weight)
    if key not in _CAP:
        _CAP[key] = Text("H", font=font, font_size=size, weight=weight).height
    t.cap = _CAP[key]
    return t


def serif(text, size=40, color=INK, weight="MEDIUM"):
    return _text(text, SERIF, size, color, weight)


def sans(text, size=24, color=INK, weight="NORMAL"):
    return _text(text, SANS, size, color, weight)


def stack(lines, center, gap=0.16):
    """Stack lines of text so their capital letters are evenly spaced and the
    block is centered on `center`, regardless of descenders like g, p or y."""
    total = sum(t.cap for t in lines) + gap * (len(lines) - 1)
    top = center[1] + total / 2
    for t in lines:
        t.set_x(center[0])
        t.shift(UP * (top - t.get_top()[1]))
        top -= t.cap + gap
    return VGroup(*lines)


def left_at(mob, x):
    return mob.shift(RIGHT * (x - mob.get_left()[0]))


def right_at(mob, x):
    return mob.shift(RIGHT * (x - mob.get_right()[0]))


# Shapes --------------------------------------------------------------------

def box(width, height, stroke=LINE, fill=PANEL, stroke_width=2, radius=0.14):
    return RoundedRectangle(
        width=width, height=height, corner_radius=radius,
        stroke_color=stroke, stroke_width=stroke_width,
        fill_color=fill, fill_opacity=1,
    )


def pill(label, color, size=17, text_color=INK, pad=0.32, height=0.42):
    t = sans(label, size, text_color, weight="MEDIUM")
    frame = RoundedRectangle(width=t.width + 2 * pad, height=height, corner_radius=height / 2,
                             stroke_width=0, fill_color=color, fill_opacity=1)
    stack([t], frame.get_center())
    return VGroup(frame, t)


def make_pin(w, h, color, img_frac=0.62, stroke=LINE, stroke_width=1.2, bars=True):
    """A Pinterest-style pin: shadow, white card, image block, two text bars.

    Every pin has the same five parts, so any pin can Transform into any other.
    """
    r = min(0.12, 0.18 * w, 0.18 * h)
    shadow = RoundedRectangle(width=w, height=h, corner_radius=r, stroke_width=0,
                              fill_color=SHADOW, fill_opacity=1)
    shadow.shift([0.02 + 0.015 * w, -0.03 - 0.015 * h, 0])
    card = RoundedRectangle(width=w, height=h, corner_radius=r, stroke_color=stroke,
                            stroke_width=stroke_width, fill_color=PANEL, fill_opacity=1)
    m = 0.07 * w
    ih = h * img_frac - m
    img = RoundedRectangle(width=w - 2 * m, height=ih, corner_radius=r * 0.75,
                           stroke_width=0, fill_color=color, fill_opacity=1)
    img.move_to(card.get_top() + DOWN * (m + ih / 2))
    bh = max(0.025, 0.05 * h)
    bar1 = RoundedRectangle(width=(w - 2 * m) * 0.8, height=bh, corner_radius=bh / 2,
                            stroke_width=0, fill_color=LINE, fill_opacity=1 if bars else 0)
    bar2 = RoundedRectangle(width=(w - 2 * m) * 0.5, height=bh, corner_radius=bh / 2,
                            stroke_width=0, fill_color=LINE, fill_opacity=1 if bars else 0)
    left_at(bar1.move_to([0, img.get_bottom()[1] - m - bh / 2, 0]), card.get_left()[0] + m)
    left_at(bar2.move_to([0, bar1.get_y() - 2 * bh, 0]), card.get_left()[0] + m)
    return VGroup(shadow, card, img, bar1, bar2)


def check_mark(center, r=0.17):
    c = Circle(radius=r, stroke_width=0, fill_color=TEAL, fill_opacity=1).move_to(center)
    tick = VMobject(stroke_color=PANEL, stroke_width=3.5)
    tick.set_points_as_corners([
        center + [-0.45 * r, 0.0, 0], center + [-0.1 * r, -0.35 * r, 0], center + [0.5 * r, 0.4 * r, 0],
    ])
    return VGroup(c, tick)


# The board -------------------------------------------------------------------

BOARD_TOP = 2.3
COL_W, COL_GAP = 0.78, 0.1


def board_layout():
    """Masonry layout: each new pin goes to the column with the most room."""
    rng = random.Random(SEED)
    total = BOARD_COLS * COL_W + (BOARD_COLS - 1) * COL_GAP
    x0 = -total / 2 + COL_W / 2
    tops = [BOARD_TOP] * BOARD_COLS
    out = []
    for _ in range(VENDOR_COUNT):
        c = max(range(BOARD_COLS), key=lambda k: (tops[k], -k))
        h = rng.uniform(0.36, 0.6)
        src = rng.randrange(len(SOURCES))
        x = x0 + c * (COL_W + COL_GAP)
        out.append({"x": x, "y": tops[c] - h / 2, "h": h, "src": src})
        tops[c] -= h + COL_GAP
    return out


LAYOUT = board_layout()
VX = min(range(VENDOR_COUNT), key=lambda i: (LAYOUT[i]["x"] - 0.4) ** 2 + (LAYOUT[i]["y"] - 0.0) ** 2)
VX_COLOR = SOURCE_COLORS[LAYOUT[VX]["src"]]


def build_board():
    return VGroup(*[
        make_pin(COL_W, p["h"], SOURCE_COLORS[p["src"]]).move_to([p["x"], p["y"], 0]) for p in LAYOUT
    ])


def mess_moves():
    rng = random.Random(SEED + 1)
    return [(rng.uniform(-9, 9), rng.uniform(-0.2, 0.2), rng.uniform(-0.15, 0.15)) for _ in LAYOUT]


def messy(pin, move, i):
    angle, dx, dy = move
    pin.rotate(angle * DEGREES).shift([dx, dy, 0])
    if i == VX:  # the one that matters gets buried
        pin.scale(0.85).set_opacity(0.35)
    return pin


def legend_row():
    pills = VGroup(*[pill(s, c) for s, c in zip(SOURCES, SOURCE_COLORS)]).arrange(RIGHT, buff=0.14)
    left_at(pills.move_to([0, 2.62, 0]), X_LEFT)
    return pills


def counter_text(n):
    t = sans(f"{n} signals this week", 20, MUTED, weight="MEDIUM")
    return right_at(t.move_to([0, 2.62, 0]), X_RIGHT)


# Lanes the hub sorts into.
LANE_X = [-4.55, 0.0, 4.55]
LANE_W = 4.3
LANE_TOP, LANE_BOTTOM = 2.3, -3.55
LANE_GRID = [  # cols, tile w, tile h, gap
    (6, 0.6, 1.2, 0.1),
    (8, 0.42, 0.78, 0.085),
    (12, 0.28, 0.5, 0.055),
]


def lane_assignment():
    """Which pins land in which lane; Vendor X is third in Act now."""
    rng = random.Random(SEED + 2)
    rest = [i for i in range(VENDOR_COUNT) if i != VX]
    rng.shuffle(rest)
    counts = [n for _, n, _ in LANES]
    flagged = rest[:counts[0] - 1]
    flagged.insert(2, VX)
    watch = rest[counts[0] - 1:counts[0] - 1 + counts[1]]
    track = rest[counts[0] - 1 + counts[1]:]
    assert [len(flagged), len(watch), len(track)] == counts
    return [flagged, watch, track]


def lane_frames():
    lanes = []
    for (name, count, color), x in zip(LANES, LANE_X):
        panel = RoundedRectangle(width=LANE_W, height=LANE_TOP - LANE_BOTTOM, corner_radius=0.2,
                                 stroke_color=LINE, stroke_width=1.5, fill_color=PANEL, fill_opacity=0.6)
        panel.move_to([x, (LANE_TOP + LANE_BOTTOM) / 2, 0])
        head = sans(name, 24, color, weight="SEMIBOLD")
        left_at(head.move_to([0, LANE_TOP - 0.42, 0]), x - LANE_W / 2 + 0.25)
        badge = pill(str(count), color, 18, PANEL, pad=0.2, height=0.4)
        badge.next_to(head, RIGHT, buff=0.18)
        badge.shift(UP * (head.get_y() - badge.get_y()))
        lanes.append(VGroup(panel, head, badge))
    return lanes


def lane_targets(assignment):
    """Target pin (shape and place) for every board pin, keyed by index."""
    targets = {}
    for lane, (idxs, x, (cols, w, h, g)) in enumerate(zip(assignment, LANE_X, LANE_GRID)):
        width = cols * w + (cols - 1) * g
        x0 = x - width / 2 + w / 2
        top = LANE_TOP - 0.85
        for k, i in enumerate(idxs):
            r, c = divmod(k, cols)
            pos = [x0 + c * (w + g), top - h / 2 - r * (h + g), 0]
            targets[i] = make_pin(w, h, SOURCE_COLORS[LAYOUT[i]["src"]]).move_to(pos)
    return targets


# Vendor X card -------------------------------------------------------------

CARD_W, CARD_H = 3.2, 4.2


def vx_card(center, cap=OLD_CAP, struck=False):
    """The big Vendor X pin: frame (same parts as a board pin) and its content."""
    frame = make_pin(CARD_W, CARD_H, VX_COLOR, img_frac=0.42, stroke=RED, stroke_width=2.5, bars=False)
    frame.move_to(center)
    img = frame[2]
    name = serif(VENDOR, 40, INK)
    doc = sans("Renewal draft", 19, INK)
    stack([name, doc], img.get_center() + DOWN * 0.2, gap=0.2)
    tag = pill("Act now", RED, 15, PANEL, pad=0.18, height=0.34)
    tag.move_to(img.get_corner(UL) + [tag.width / 2 + 0.14, -0.3, 0])
    low_top = img.get_bottom()[1]
    label = sans("Annual price increase cap", 17, MUTED)
    label.move_to([frame.get_x(), low_top - 0.42, 0])
    value = serif(pct(cap), 66, CORAL if cap == NEW_CAP else INK)
    value.move_to([frame.get_x(), low_top - 1.25, 0])
    content = VGroup(tag, name, doc, label, value)
    if struck:
        was = sans(f"was {pct(OLD_CAP)}", 17, MUTED).move_to([frame.get_x(), low_top - 2.0, 0])
        content.add(was)
    return frame, content


# Base scene ------------------------------------------------------------------

class ExplainerScene(Scene):
    """Base scene: badge, title, and narration-locked timing.

    Each animation step is anchored to the start of a narration sentence with
    at(i), so the visuals stay in step with the voiceover timing. FROM_TO titles
    show the "from" half first; reveal_to() brings in the "to" half.
    """

    KEY = None
    TITLE = None
    FROM_TO = None

    def setup(self):
        self.frame_count = 0
        self._waiting = False
        self.total_time, cues, self.part_starts = scene_timing(self.KEY)
        self.cue_starts = [c[0] for c in cues]
        self.add(self.make_badge())
        if self.TITLE:
            self.add(serif(self.TITLE, 40).to_corner(UL, buff=0.55))
        if self.FROM_TO:
            frm, to = self.FROM_TO
            full = serif(f"{frm} {to}", 40).to_corner(UL, buff=0.55)
            n = len(frm.replace(" ", ""))
            self.title_from = VGroup(*full.submobjects[:n])
            self.title_to = VGroup(*full.submobjects[n:])
            self.title_to.set_color(RED)
            self.add(self.title_from)

    def reveal_to(self, run_time=0.6):
        self.play(FadeIn(self.title_to, shift=LEFT * 0.3), run_time=run_time)

    def make_badge(self):
        label = sans(BADGE_TEXT, 16, MUTED)
        frame = box(label.width + 0.4, label.height + 0.26, radius=0.1, stroke_width=1.5)
        label.move_to(frame)
        self.badge = VGroup(frame, label).to_corner(UR, buff=0.35)
        self.badge.set_z_index(10)
        return self.badge

    # Manim counts frames for an animation with numpy.arange and for a still
    # wait with int(), and both can gain or drop a frame on float durations.
    # Every step is snapped to whole frames here and counted, so a scene ends
    # on exactly the planned frame.

    def n_frames(self, t):
        return max(round(t * manim_config.frame_rate), 1)

    def play(self, *animations, run_time=None, **kwargs):
        if self._waiting:  # Scene.wait calls play internally
            return super().play(*animations, **kwargs) if run_time is None else \
                super().play(*animations, run_time=run_time, **kwargs)
        n = self.n_frames(1.0 if run_time is None else run_time)
        super().play(*animations, run_time=(n - 0.5) / manim_config.frame_rate, **kwargs)
        self.frame_count += n

    def wait(self, duration=1.0, **kwargs):
        n = self.n_frames(duration)
        self._waiting = True
        super().wait((n + 0.5) / manim_config.frame_rate, frozen_frame=True)
        self._waiting = False
        self.frame_count += n

    @property
    def now(self):
        return self.frame_count / manim_config.frame_rate

    def hold_until(self, t):
        dt = t - self.now
        assert dt > -1e-6, f"{type(self).__name__}: step at {t:.2f}s starts late (now {self.now:.2f}s)"
        if dt > 0.5 / manim_config.frame_rate:
            self.wait(dt)

    def at(self, i, offset=0.0):
        self.hold_until(self.cue_starts[i] + offset)

    def finish(self):
        self.hold_until(self.total_time)


# Scenes ----------------------------------------------------------------------

class BoardScene(ExplainerScene):
    KEY = "01_board"
    TITLE = "Every week, a full board"

    def construct(self):
        board = build_board()
        pills = legend_row()
        count = ValueTracker(0)
        counter = always_redraw(lambda: counter_text(round(count.get_value())))
        self.add(counter)

        # 150 pins land on the board.
        self.at(0)
        self.play(
            LaggedStart(*[FadeIn(p, shift=DOWN * 0.45, scale=0.8, rate_func=rf.ease_out_back)
                          for p in board], lag_ratio=0.02),
            count.animate(rate_func=rf.linear).set_value(VENDOR_COUNT),
            run_time=3.4,
        )
        counter.clear_updaters()
        self.remove(counter)
        self.add(counter_text(VENDOR_COUNT))

        # Five sources, each lighting up its own pins.
        self.at(1)
        for k, p in enumerate(pills):
            mine = [pin for pin, lay in zip(board, LAYOUT) if lay["src"] == k]
            self.play(
                FadeIn(p, scale=0.6, rate_func=rf.ease_out_back),
                *[pin.animate(rate_func=rf.there_and_back).scale(1.18) for pin in mine],
                run_time=0.48,
            )

        # It piles up; Vendor X gets buried.
        self.at(2)
        vx = board[VX]
        ring = RoundedRectangle(width=vx.width + 0.14, height=vx.height + 0.14, corner_radius=0.14,
                                stroke_color=RED, stroke_width=4).move_to(vx[1])
        self.play(Create(ring), vx.animate.scale(1.15), run_time=0.6)
        self.play(FadeOut(ring), vx.animate.scale(1 / 1.15), run_time=0.4)
        moves = mess_moves()
        self.play(
            AnimationGroup(*[
                Transform(p, messy(p.copy(), mv, i)) for i, (p, mv) in enumerate(zip(board, moves))
            ]),
            run_time=1.6, rate_func=rf.ease_in_out_cubic,
        )
        self.finish()


class SortScene(ExplainerScene):
    KEY = "02_sort"
    FROM_TO = ("From noise", "to priorities")

    def construct(self):
        board = build_board()
        clean = [p.copy() for p in board]
        for i, (p, mv) in enumerate(zip(board, mess_moves())):
            messy(p, mv, i)
        pills = legend_row()
        counter = counter_text(VENDOR_COUNT)
        self.add(board, pills, counter)

        assignment = lane_assignment()
        targets = lane_targets(assignment)
        lanes = lane_frames()
        scan = Line([0, BOARD_TOP + 0.1, 0], [0, -3.8, 0], color=RED, stroke_width=5)
        scan.set_x(-7.4)

        # The hub reads every pin...
        self.at(0)
        self.add(scan)
        self.play(
            scan.animate.set_x(7.4),
            LaggedStart(*[Transform(board[i], clean[i]) for i in
                          sorted(range(VENDOR_COUNT), key=lambda i: LAYOUT[i]["x"])], lag_ratio=0.006),
            run_time=1.0, rate_func=rf.linear,
        )
        self.remove(scan)
        # ...and sorts the board.
        for lane in lanes:
            lane.set_z_index(-1)
        self.play(FadeOut(pills), FadeOut(counter), *[FadeIn(lane[0]) for lane in lanes], run_time=0.4)
        self.reveal_to(0.4)
        order = [i for idxs in assignment for i in idxs]
        self.play(
            LaggedStart(*[Transform(board[i], targets[i], path_arc=0.6) for i in order], lag_ratio=0.004),
            run_time=2.1, rate_func=rf.smooth,
        )
        self.play(*[FadeIn(VGroup(lane[1], lane[2]), shift=DOWN * 0.15) for lane in lanes], run_time=0.4)

        # Most can wait.
        self.at(1)
        waiting = [board[i] for idxs in assignment[1:] for i in idxs]
        self.play(*[m.animate.set_opacity(0.25) for m in waiting + list(lanes[1]) + list(lanes[2])],
                  run_time=0.8)

        # 18 need action now; one of them is Vendor X.
        self.at(2)
        self.play(lanes[0][2].animate(rate_func=rf.there_and_back).scale(1.5), run_time=0.6)
        frame, content = vx_card([0, -0.45, 0])
        others = [board[i] for i in range(VENDOR_COUNT) if i != VX]
        board[VX].set_z_index(5)
        content.set_z_index(6)
        self.play(
            Transform(board[VX], frame, path_arc=0.4),
            *[FadeOut(m) for m in others], *[FadeOut(lane) for lane in lanes],
            run_time=1.3, rate_func=rf.ease_in_out_cubic,
        )
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in content], lag_ratio=0.15), run_time=0.9)
        self.finish()


class DollarsScene(ExplainerScene):
    KEY = "03_dollars"
    FROM_TO = ("From a clause", "to dollars")

    def construct(self):
        frame, content = vx_card([0, -0.45, 0])
        card = VGroup(frame, content)
        self.add(card)
        dest = [-4.75, -0.45, 0]

        # The clause changes: 2% becomes 6%.
        self.at(0)
        self.play(card.animate.move_to(dest), run_time=0.8, rate_func=rf.ease_in_out_cubic)
        old = content[4]
        new_frame, new_content = vx_card(dest, cap=NEW_CAP, struck=True)
        strike = Line(old.get_left() + LEFT * 0.1, old.get_right() + RIGHT * 0.1, color=CORAL, stroke_width=5)
        self.play(Create(strike), run_time=0.35)
        self.play(FadeOut(strike), ReplacementTransform(old, new_content[4]),
                  run_time=0.7, rate_func=rf.ease_out_back)
        self.play(FadeIn(new_content[5], shift=UP * 0.1), run_time=0.4)

        # Dollars: one scale for both bars.
        x0 = -2.0
        unit = 6.2 / new_max
        y_old, y_new = 0.85, -0.75
        spend = pill(f"Annual spend: {money(SPEND)}", "#EDE7DE", 20, INK, pad=0.3, height=0.5)
        left_at(spend.move_to([0, 2.15, 0]), x0)

        def row(cap, value, color, y, label):
            lab = sans(label, 21, color, weight="SEMIBOLD")
            left_at(lab.move_to([0, y + 0.5, 0]), x0)
            bar = Rectangle(width=value * unit, height=0.5, stroke_width=0, fill_color=color, fill_opacity=1)
            bar.move_to([x0, y, 0], aligned_edge=LEFT)
            f = sans(f"{money(SPEND)} × {pct(cap)} = {money(value)}", 17, MUTED)
            left_at(f.move_to([0, y - 0.55, 0]), x0)
            return lab, bar, f

        o_lab, o_bar, o_f = row(OLD_CAP, old_max, BLUE, y_old, f"Old cap {pct(OLD_CAP)}: most it can add")
        n_lab, n_bar, n_f = row(NEW_CAP, new_max, CORAL, y_new, f"Draft cap {pct(NEW_CAP)}: most it can add")
        assert abs(n_bar.width - 3 * o_bar.width) < 1e-9

        def counter(tracker, bar):
            return always_redraw(lambda: sans(money(round(tracker.get_value())), 26, INK, weight="SEMIBOLD")
                                 .next_to(bar, RIGHT, buff=0.22))

        t_old, t_new = ValueTracker(0), ValueTracker(0)
        c_old, c_new = counter(t_old, o_bar), counter(t_new, n_bar)

        self.at(1)
        self.reveal_to(0.5)
        self.play(FadeIn(spend, shift=RIGHT * 0.4), run_time=0.5)
        self.play(FadeIn(o_lab), run_time=0.3)
        self.add(c_old)
        self.play(GrowFromEdge(o_bar, LEFT), t_old.animate.set_value(old_max), run_time=1.0)
        self.play(FadeIn(n_lab), run_time=0.3)
        self.add(c_new)
        self.play(GrowFromEdge(n_bar, LEFT), t_new.animate.set_value(new_max), run_time=1.4)
        self.play(FadeIn(o_f), FadeIn(n_f), run_time=0.4)
        for c, v, b in [(c_old, old_max, o_bar), (c_new, new_max, n_bar)]:
            c.clear_updaters()
            c.become(sans(money(v), 26, INK, weight="SEMIBOLD").next_to(b, RIGHT, buff=0.22))

        # The gap: 40,000 dollars a year.
        self.at(2)
        gap_box = Rectangle(width=gap * unit, height=0.62, stroke_color=GOLD, stroke_width=4, fill_opacity=0)
        gap_box.move_to([x0 + old_max * unit, y_new, 0], aligned_edge=LEFT)
        t_gap = ValueTracker(0)
        big = always_redraw(lambda: left_at(
            serif(f"{money(round(t_gap.get_value()))} a year", 48, GOLD).move_to([0, -2.1, 0]),
            gap_box.get_left()[0]))
        g_f = sans(f"{money(new_max)} - {money(old_max)} = {money(gap)}", 17, MUTED)
        left_at(g_f.move_to([0, -2.72, 0]), gap_box.get_left()[0])
        note = sans("Annual view. Multi-year compounding is not shown.", 15, MUTED)
        left_at(note.move_to([0, -3.08, 0]), gap_box.get_left()[0])
        self.play(Create(gap_box), run_time=0.5)
        self.add(big)
        self.play(t_gap.animate.set_value(gap), run_time=0.9, rate_func=rf.ease_out_cubic)
        big.clear_updaters()
        big.become(left_at(serif(f"{money(gap)} a year", 48, GOLD).move_to([0, -2.1, 0]), gap_box.get_left()[0]))
        self.play(FadeIn(g_f), FadeIn(note), run_time=0.4)
        self.finish()


class PlanScene(ExplainerScene):
    KEY = "04_plan"
    FROM_TO = ("From a deadline", "to a plan")

    def construct(self):
        frame, content = vx_card([-4.75, -0.45, 0], cap=NEW_CAP, struck=True)
        card = VGroup(frame, content)
        self.add(card)

        sticker_t = sans(CHOSEN_POSTURE, 19, INK, weight="SEMIBOLD")
        sticker = VGroup(
            RoundedRectangle(width=sticker_t.width + 0.5, height=0.52, corner_radius=0.26,
                             stroke_width=0, fill_color=GOLD, fill_opacity=1),
            sticker_t,
        )
        stack([sticker_t], sticker[0].get_center())

        x_a, x_b, y_t = -2.9, 6.2, -1.2

        def day_x(d):
            return x_a + d / RENEWAL_DAYS * (x_b - x_a)

        track = Line([x_a, y_t, 0], [x_b, y_t, 0], color=LINE, stroke_width=8)
        start = Dot([x_a, y_t, 0], radius=0.13, color=TEAL)
        end = Dot([x_b, y_t, 0], radius=0.13, color=RED)
        start_l = sans("Today", 18, TEAL, weight="MEDIUM").move_to([x_a, y_t - 0.45, 0])
        end_l = right_at(sans(f"Renewal, day {RENEWAL_DAYS}", 18, RED, weight="MEDIUM")
                         .move_to([0, y_t - 0.45, 0]), 6.6)
        runway = sans(f"{RENEWAL_DAYS} days to renewal", 18, GOLD, weight="SEMIBOLD")
        runway.move_to([(x_a + x_b) / 2, y_t - 0.45, 0])

        day = ValueTracker(0)
        walker = Dot([x_a, y_t, 0], radius=0.11, color=INK)
        walker.add_updater(lambda m: m.move_to([day_x(day.get_value()), y_t, 0]))
        progress = always_redraw(lambda: Line([x_a, y_t, 0], [day_x(day.get_value()) + 1e-3, y_t, 0],
                                              color=TEAL, stroke_width=8))
        day_label = always_redraw(lambda: serif(f"Day {round(day.get_value())} of {RENEWAL_DAYS}", 34, INK)
                                  .move_to([(x_a + x_b) / 2, -2.6, 0]))

        steps = []
        for i, (d, text) in enumerate(PLAN_STEPS):
            t = sans(text, 16, INK, weight="MEDIUM")
            w = max(2.2, t.width + 0.5)
            p = make_pin(w, 1.25, SOURCE_COLORS[i + 1], img_frac=0.42, bars=False)
            p.move_to([day_x(d), 0.45, 0])
            stack([t], [p.get_x(), p[2].get_bottom()[1] - 0.33, 0])
            step_no = sans(f"Step {i + 1}", 14, INK, weight="SEMIBOLD").move_to(p[2])
            stem = Line(p.get_bottom(), [day_x(d), y_t, 0], color=LINE, stroke_width=2.5)
            check = check_mark(p[1].get_corner(UR) + [-0.05, -0.05, 0])
            steps.append((d, VGroup(p, t, step_no), stem, check))

        # Tag it, and lay out the 90 days.
        self.at(0)
        self.play(card.animate.scale(0.78).move_to([-5.25, 0.15, 0]), run_time=0.7, rate_func=rf.ease_in_out_cubic)
        sticker.rotate(6 * DEGREES).move_to(frame[1].get_bottom() + DOWN * 0.22)
        self.play(FadeIn(sticker, scale=1.9, rate_func=rf.ease_out_back), run_time=0.5)
        self.play(Create(track), FadeIn(start, scale=0.3), FadeIn(end, scale=0.3), run_time=0.7)
        self.play(FadeIn(start_l), FadeIn(end_l), FadeIn(runway), run_time=0.5)

        # Walk the 90 days: each step lands on the timeline.
        self.at(1)
        self.reveal_to(0.4)
        self.add(progress, walker, day_label)
        prev = 0
        for d, pin, stem, check in steps:
            self.play(day.animate.set_value(d), run_time=max(0.3, (d - prev) / RENEWAL_DAYS * 2.9),
                      rate_func=rf.linear)
            self.play(FadeIn(pin, shift=DOWN * 0.5, rate_func=rf.ease_out_back), Create(stem), run_time=0.5)
            self.play(FadeIn(check, scale=0.3, rate_func=rf.ease_out_back), run_time=0.25)
            prev = d
        self.play(day.animate.set_value(RENEWAL_DAYS), run_time=0.3, rate_func=rf.linear)
        for m in (walker, progress, day_label):
            m.clear_updaters()
        self.play(end.animate(rate_func=rf.there_and_back).scale(1.8), run_time=0.4)
        self.finish()


class AheadScene(ExplainerScene):
    KEY = "05_ahead"
    FROM_TO = ("From reacting", "to seeing ahead")

    def outcome(self, head, sub, color, y=0.6):
        frame = box(6.0, 1.9, stroke=color, stroke_width=3.5, radius=0.22)
        h = serif(head, 40, color)
        s = sans(sub, 21, MUTED)
        stack([h, s], frame.get_center(), gap=0.3)
        return VGroup(frame, h, s).move_to([0, y, 0])

    def mini_board(self, rng):
        cols, w, g, top = 12, 0.62, 0.12, 0.2
        x0 = -(cols * w + (cols - 1) * g) / 2 + w / 2
        tops = [top] * cols
        pins = []
        for _ in range(36):
            c = max(range(cols), key=lambda k: (tops[k], -k))
            h = rng.uniform(0.4, 0.75)
            pins.append(make_pin(w, h, rng.choice(SOURCE_COLORS)).move_to([x0 + c * (w + g), tops[c] - h / 2, 0]))
            tops[c] -= h + g
        return VGroup(*pins)

    def mini_sort(self, pins, rng):
        heads, targets = [], []
        counts = [3, 9, 24]
        idx = list(range(len(pins)))
        rng.shuffle(idx)
        k = 0
        for (name, _, color), x, n, (cols, w, h, g) in zip(LANES, LANE_X, counts,
                                                            [(3, 0.62, 0.8, 0.12), (5, 0.5, 0.6, 0.1),
                                                             (8, 0.36, 0.44, 0.08)]):
            head = sans(name, 20, color, weight="SEMIBOLD").move_to([x, 0.0, 0])
            heads.append(head)
            width = cols * w + (cols - 1) * g
            for j in range(n):
                r, c = divmod(j, cols)
                pos = [x - width / 2 + w / 2 + c * (w + g), -0.45 - h / 2 - r * (h + g), 0]
                i = idx[k]
                targets.append((i, make_pin(w, h, pins[i][2].get_fill_color()).move_to(pos)))
                k += 1
        return heads, targets

    def construct(self):
        before = self.outcome("Surprise cost", f"{money(gap)} a year, found at renewal", CORAL)
        after = self.outcome("Negotiation", f"{money(gap)} a year on the table, {RENEWAL_DAYS} days to act", TEAL)

        # A surprise cost becomes a negotiation.
        self.at(0)
        self.play(FadeIn(before, scale=0.85, rate_func=rf.ease_out_back), run_time=0.6)
        self.wait(0.5)
        self.play(ReplacementTransform(before[0], after[0]),
                  FadeOut(VGroup(before[1], before[2]), shift=UP * 0.25),
                  FadeIn(VGroup(after[1], after[2]), shift=UP * 0.25),
                  run_time=0.9, rate_func=rf.ease_in_out_cubic)
        self.reveal_to(0.5)

        # Every week, the board gets sorted before it piles up.
        self.at(1)
        rng = random.Random(SEED + 3)
        self.play(after.animate.scale(0.7).move_to([0, 1.75, 0]), run_time=0.6)
        week = pill("Every week", "#EDE7DE", 18, INK, pad=0.3, height=0.44)
        left_at(week.move_to([0, 0.75, 0]), X_LEFT)
        for round_no in range(2):
            pins = self.mini_board(rng)
            new_heads, targets = self.mini_sort(pins, rng)
            if round_no == 0:
                heads = new_heads
            anims = [FadeIn(week, scale=0.7)] if round_no == 0 else []
            self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.4, rate_func=rf.ease_out_back) for p in pins],
                                  lag_ratio=0.03), *anims, run_time=1.0 if round_no == 0 else 0.7)
            head_anims = [FadeIn(h) for h in heads] if round_no == 0 else []
            self.play(LaggedStart(*[Transform(pins[i], t, path_arc=0.5) for i, t in targets], lag_ratio=0.01),
                      *head_anims, run_time=1.1 if round_no == 0 else 0.8)
            if round_no == 0:
                self.wait(0.3)
                self.play(FadeOut(pins, shift=DOWN * 0.3), run_time=0.35)
            last = pins

        # Early action drives the business.
        self.at(2)
        pins = last
        final = serif("Early action drives the business.", 54, INK)
        sub = sans("The Supplier Intelligence Hub", 26, RED, weight="SEMIBOLD")
        VGroup(final, sub).arrange(DOWN, buff=0.35).move_to([0, -0.3, 0])
        self.play(FadeOut(pins), *[FadeOut(h) for h in heads], FadeOut(after), FadeOut(week),
                  FadeIn(final, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.5)
        self.finish()


SCENES = {
    "01_board": BoardScene,
    "02_sort": SortScene,
    "03_dollars": DollarsScene,
    "04_plan": PlanScene,
    "05_ahead": AheadScene,
}
