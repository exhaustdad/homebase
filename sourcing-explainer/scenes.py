"""Manim scenes for the sourcing explainer.

Render with build.py, or directly:
    manim -ql scenes.py ProblemScene
"""

import random

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, UR, ORIGIN,
    Arrow, Create, Dot, FadeIn,
    GrowFromEdge, LaggedStart, Line, Rectangle, RoundedRectangle, Scene, Text, VGroup,
    config as manim_config,
)

from config import (
    AGENTS, BADGE_TEXT, BG, BLUE, CHOSEN_POSTURE, CORAL, FLAGGED, GOLD,
    GRID_COLS, GRID_ROWS, INK, LINE, MUTED, NEW_CAP, OLD_CAP, PANEL, POSTURES,
    RENEWAL_DAYS, SANS, SERIF, SOURCES, SPEND, TEAL, VENDOR, VENDOR_COUNT,
    gap, money, new_max, old_max, pct, scene_timing,
)

manim_config.background_color = BG


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


def box(width, height, stroke=LINE, fill=PANEL, stroke_width=2.5, radius=0.14):
    return RoundedRectangle(
        width=width, height=height, corner_radius=radius,
        stroke_color=stroke, stroke_width=stroke_width,
        fill_color=fill, fill_opacity=1,
    )


def labeled_box(heading, sub, width, height, stroke, heading_size=26, sub_size=20):
    frame = box(width, height, stroke=stroke)
    h = sans(heading, heading_size, INK, weight="MEDIUM")
    s = sans(sub, sub_size, MUTED)
    text = stack([h, s], frame.get_center(), gap=0.2)
    return VGroup(frame, text)


def chip(label, width=3.0, height=0.58, size=22, color=INK, stroke=LINE):
    frame = box(width, height, stroke=stroke, radius=height / 2)
    t = stack([sans(label, size, color)], frame.get_center())[0]
    return VGroup(frame, t)


class ExplainerScene(Scene):
    """Base scene: badge, title, and narration-locked timing.

    Each animation step is anchored to the start of a narration sentence with
    at(i), so the visuals stay in step with the voiceover timing.
    """

    KEY = None
    TITLE = None

    def setup(self):
        self.frame_count = 0
        self._waiting = False
        self.total_time, cues, self.part_starts = scene_timing(self.KEY)
        self.cue_starts = [c[0] for c in cues]
        self.add(self.make_badge())
        if self.TITLE:
            title = serif(self.TITLE, 40)
            title.to_corner(UL, buff=0.55)
            self.add(title)

    def make_badge(self):
        label = sans(BADGE_TEXT, 16, MUTED)
        frame = box(label.width + 0.4, label.height + 0.26, radius=0.1, stroke_width=1.5)
        label.move_to(frame)
        self.badge = VGroup(frame, label).to_corner(UR, buff=0.35)
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


def arrow(a, b, color=MUTED):
    return Arrow(a, b, buff=0.08, color=color, stroke_width=3,
                 max_tip_length_to_length_ratio=0.2, tip_length=0.16)


def left_at(mob, x):
    """Move mob so its left edge sits at x."""
    return mob.shift(RIGHT * (x - mob.get_left()[0]))


class TitleScene(ExplainerScene):
    KEY = "00_title"

    def construct(self):
        l1 = serif("From Vendor Noise", 78)
        l2 = serif("to Sourcing Decisions", 78)
        sub = sans("The Supplier Intelligence Hub", 30, BLUE)
        block = VGroup(l1, l2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        sub.next_to(block, DOWN, buff=0.6, aligned_edge=LEFT)
        VGroup(block, sub).move_to(ORIGIN + DOWN * 0.1)

        self.play(FadeIn(l1, shift=UP * 0.15), run_time=0.8)
        self.play(FadeIn(l2, shift=UP * 0.15), run_time=0.8)
        self.play(FadeIn(sub), run_time=0.7)
        self.finish()


class ProblemScene(ExplainerScene):
    KEY = "01_problem"
    TITLE = "Too many vendors, too many places"

    def construct(self):
        dots = VGroup(*[
            Dot(radius=0.075, color=MUTED, fill_opacity=0.55)
            for _ in range(GRID_COLS * GRID_ROWS)
        ])
        dots.arrange_in_grid(rows=GRID_ROWS, cols=GRID_COLS, buff=0.25)
        dots.move_to([-2.7, 0.05, 0])
        assert len(dots) == VENDOR_COUNT

        flagged = random.Random(7).sample(range(len(dots)), FLAGGED)

        def legend(color, label, opacity=1.0):
            d = Dot(radius=0.075, color=color, fill_opacity=opacity)
            t = sans(label, 21, INK)
            return VGroup(d, t).arrange(RIGHT, buff=0.18)

        all_key = legend(MUTED, f"{VENDOR_COUNT} vendors", 0.55)
        flag_key = legend(CORAL, f"{FLAGGED} need action now")
        left_at(all_key.move_to([0, -2.25, 0]), dots.get_left()[0])
        flag_key.move_to([0, -2.25, 0])
        left_at(flag_key, all_key.get_right()[0] + 0.6)

        chips = VGroup(*[chip(s, 3.1) for s in SOURCES]).arrange(DOWN, buff=0.22)
        chips.move_to([4.55, 0.05, 0])
        chips_label = sans(f"{len(SOURCES)} separate systems", 20, MUTED)
        chips_label.next_to(chips, DOWN, buff=0.3)

        warning = sans("No single view of all signals.", 30, CORAL, weight="MEDIUM")
        warning.move_to([0, -3.2, 0])

        self.at(0)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.01),
                  FadeIn(all_key), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.2),
                  FadeIn(chips_label), run_time=1.5)

        self.at(1)
        self.play(*[dots[i].animate.set_fill(CORAL, opacity=1).scale(1.4) for i in flagged],
                  FadeIn(flag_key), run_time=1.0)

        self.at(2)
        self.play(FadeIn(warning, shift=UP * 0.1), run_time=0.9)
        self.finish()


class FlowScene(ExplainerScene):
    KEY = "02_flow"
    TITLE = "One flow, four postures"

    def construct(self):
        flow_y = 0.8
        chips = VGroup(*[chip(s, 2.55, 0.46, 19) for s in SOURCES]).arrange(DOWN, buff=0.13)
        chips.move_to([-5.3, flow_y, 0])

        bus_x = -3.75
        feeds = VGroup(*[
            Line(c.get_right(), [bus_x, c.get_y(), 0], color=MUTED, stroke_width=2.5) for c in chips
        ])
        bus = Line([bus_x, chips[0].get_y(), 0], [bus_x, chips[-1].get_y(), 0], color=MUTED, stroke_width=2.5)

        weekly = labeled_box("Weekly brief", "The full picture", 2.9, 1.0, BLUE, 23, 18)
        warn = labeled_box("Early warning", "Always on", 2.9, 1.0, CORAL, 23, 18)
        weekly.move_to([-1.35, flow_y + 0.72, 0])
        warn.move_to([-1.35, flow_y - 0.72, 0])
        a_weekly = arrow([bus_x, weekly.get_y(), 0], weekly.get_left())
        a_warn = arrow([bus_x, warn.get_y(), 0], warn.get_left())

        hub = labeled_box("Slack hub", f"{len(AGENTS)} agents", 2.5, 1.1, GOLD, 24, 18)
        hub.move_to([2.15, flow_y, 0])
        a_w_hub = arrow(weekly.get_right(), hub.get_left() + UP * 0.22)
        a_e_hub = arrow(warn.get_right(), hub.get_left() + DOWN * 0.22)

        names = VGroup(*[sans(n, 18, INK) for n, _ in AGENTS])
        names.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        names.move_to([0, flow_y, 0])
        left_at(names, 4.75)
        spokes = VGroup(*[
            Line(hub.get_right(), [n.get_left()[0] - 0.12, n.get_y(), 0], color=LINE, stroke_width=2.5)
            for n in names
        ])

        tiles = []
        for name, desc in POSTURES:
            frame = box(3.1, 1.15)
            head = sans(name, 21, INK, weight="MEDIUM")
            sub = sans(desc, 17, MUTED)
            stack([head, sub], frame.get_center(), gap=0.2)
            tiles.append(VGroup(frame, head, sub))
        tiles = VGroup(*tiles).arrange(RIGHT, buff=0.25).move_to([0, -2.55, 0])

        drop_y = tiles.get_top()[1] + 0.32
        drop = Line(hub.get_bottom(), [hub.get_x(), drop_y, 0], color=GOLD, stroke_width=2.5)
        rail = Line([tiles[0].get_x(), drop_y, 0], [tiles[-1].get_x(), drop_y, 0], color=GOLD, stroke_width=2.5)
        ticks = VGroup(*[
            Line([t.get_x(), drop_y, 0], [t.get_x(), t.get_top()[1], 0], color=GOLD, stroke_width=2.5)
            for t in tiles
        ])

        # Reads every source.
        self.at(0)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.15) for c in chips], lag_ratio=0.15), run_time=1.0)
        self.play(Create(feeds), Create(bus), run_time=0.7)

        # Two speeds into one hub with six agents.
        self.at(1)
        self.play(Create(a_weekly), Create(a_warn), run_time=0.6)
        self.play(FadeIn(weekly), FadeIn(warn), run_time=0.7)
        self.play(Create(a_w_hub), Create(a_e_hub), run_time=0.6)
        self.play(FadeIn(hub), run_time=0.7)
        self.play(LaggedStart(*[Create(l) for l in spokes], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.12), run_time=1.5)

        # Four postures.
        self.at(2)
        self.play(Create(drop), run_time=0.5)
        self.play(Create(rail), Create(ticks), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tiles], lag_ratio=0.2), run_time=1.6)
        self.finish()


class DollarsScene(ExplainerScene):
    KEY = "03_dollars"
    TITLE = "From signal to dollars"

    def construct(self):
        x0 = -3.6
        unit = 6.0 / new_max  # scene units per dollar; one scale for both bars
        bar_h = 0.55
        y_old, y_new = 1.0, -0.75

        spend = sans(f"{VENDOR}, annual spend: {money(SPEND)} (illustrative)", 27, INK)
        left_at(spend.move_to([0, 2.3, 0]), -6.55)

        def bar(value, color, y):
            r = Rectangle(width=value * unit, height=bar_h, stroke_width=0,
                          fill_color=color, fill_opacity=0.9)
            r.move_to([x0, y, 0], aligned_edge=LEFT)
            return r

        old_bar = bar(old_max, BLUE, y_old)
        new_bar = bar(new_max, CORAL, y_new)
        assert abs(new_bar.width - 3 * old_bar.width) < 1e-9

        old_label = sans(f"Old cap: {pct(OLD_CAP)}", 25, BLUE, weight="MEDIUM")
        new_label = sans(f"Draft cap: {pct(NEW_CAP)}", 25, CORAL, weight="MEDIUM")
        left_at(old_label.move_to([0, y_old, 0]), -6.55)
        left_at(new_label.move_to([0, y_new, 0]), -6.55)

        old_val = sans(money(old_max), 27, INK, weight="MEDIUM").next_to(old_bar, RIGHT, buff=0.25)
        new_val = sans(money(new_max), 27, INK, weight="MEDIUM").next_to(new_bar, RIGHT, buff=0.25)

        old_f = sans(f"{money(SPEND)} × {pct(OLD_CAP)} = {money(old_max)}", 20, MUTED)
        new_f = sans(f"{money(SPEND)} × {pct(NEW_CAP)} = {money(new_max)}", 20, MUTED)
        old_f.next_to(old_bar, DOWN, buff=0.2).align_to(old_bar, LEFT)
        new_f.next_to(new_bar, DOWN, buff=0.2).align_to(new_bar, LEFT)

        gap_left = x0 + old_max * unit
        gap_box = Rectangle(width=gap * unit, height=bar_h + 0.2, stroke_color=GOLD,
                            stroke_width=3.5, fill_opacity=0)
        gap_box.move_to([gap_left, y_new, 0], aligned_edge=LEFT)
        gap_label = sans(f"{money(gap)} more exposure each year", 26, GOLD, weight="MEDIUM")
        gap_f = sans(f"{money(new_max)} - {money(old_max)} = {money(gap)}", 20, MUTED)
        gap_group = VGroup(gap_label, gap_f).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        gap_group.next_to(new_f, DOWN, buff=0.45).align_to(gap_box, LEFT)

        note = sans("Annual view. Multi-year compounding is not shown.", 17, MUTED)
        note.next_to(gap_group, DOWN, buff=0.25).align_to(gap_box, LEFT)

        # Fictional vendor: the badge lifts while the vendor is introduced.
        self.at(0)
        self.play(FadeIn(spend),
                  self.badge[0].animate.set_stroke(GOLD), self.badge[1].animate.set_color(INK),
                  run_time=0.9)
        self.at(0, offset=3.0)
        self.play(self.badge[0].animate.set_stroke(LINE), self.badge[1].animate.set_color(MUTED), run_time=0.7)

        # Caps: 2% to 6%.
        self.at(1)
        self.play(FadeIn(old_label), GrowFromEdge(old_bar, LEFT), run_time=1.1)
        self.play(FadeIn(new_label), GrowFromEdge(new_bar, LEFT), run_time=1.5)

        # Dollar ceilings.
        self.at(2)
        self.play(FadeIn(old_val), FadeIn(old_f), run_time=0.8)
        self.at(2, offset=2.0)
        self.play(FadeIn(new_val), FadeIn(new_f), run_time=0.8)

        # The gap.
        self.at(3)
        self.play(Create(gap_box), run_time=0.9)
        self.play(FadeIn(gap_group), run_time=0.7)
        self.play(FadeIn(note), run_time=0.5)
        self.finish()


class ActionScene(ExplainerScene):
    KEY = "04_action"
    TITLE = "Early sight, better terms"

    def construct(self):
        x_left = -6.55

        tag = chip(VENDOR, 1.8, 0.5, 21, GOLD, GOLD)
        posture = sans(f"Posture: {CHOSEN_POSTURE}", 25, INK, weight="MEDIUM")
        row = VGroup(tag, posture).arrange(RIGHT, buff=0.3)
        left_at(row.move_to([0, 2.2, 0]), x_left)

        action_text = sans(
            f"Action: ask to restore the {pct(OLD_CAP)} cap before the renewal date.", 23, INK,
        )
        action_frame = box(action_text.width + 0.6, action_text.height + 0.42, stroke=GOLD)
        action = VGroup(action_frame, action_text.move_to(action_frame))
        left_at(action.move_to([0, 1.3, 0]), x_left)

        # 90-day runway from the flag to the renewal date.
        tl_y, x_a, x_b = -0.55, -5.2, 5.2
        track = Line([x_a, tl_y, 0], [x_b, tl_y, 0], color=LINE, stroke_width=4)
        start = Dot([x_a, tl_y, 0], radius=0.11, color=TEAL)
        end = Dot([x_b, tl_y, 0], radius=0.11, color=CORAL)
        start.set_z_index(2)
        end.set_z_index(2)
        start_label = sans("Flagged today", 20, TEAL).next_to(start, DOWN, buff=0.22)
        end_label = sans(f"Renewal, day {RENEWAL_DAYS}", 20, CORAL).next_to(end, DOWN, buff=0.22)
        kinds = VGroup(*[chip(k, w, 0.44, 18) for k, w in
                         [("Renewals", 1.6), ("Risks", 1.1), ("Price changes", 2.1)]])
        kinds.arrange(RIGHT, buff=0.15)
        kinds.next_to(start, UP, buff=0.3)
        left_at(kinds, x_a - 0.2)

        band = Rectangle(width=x_b - x_a, height=0.16, stroke_width=0, fill_color=GOLD, fill_opacity=0.9)
        band.move_to([x_a, tl_y, 0], aligned_edge=LEFT)
        runway = sans(f"{RENEWAL_DAYS} days to negotiate", 22, GOLD, weight="MEDIUM")
        runway.move_to([2.6, tl_y + 0.5, 0])

        value = sans(
            f"Restoring the {pct(OLD_CAP)} cap removes up to {money(gap)} a year of exposure.", 23, INK,
        )
        value.move_to([0, -1.9, 0])

        final = serif("Early action drives the business.", 44, GOLD)
        final.move_to([0, -3.05, 0])

        self.at(0)
        self.play(FadeIn(tag, shift=RIGHT * 0.15), FadeIn(posture), run_time=0.8)
        self.at(0, offset=2.6)
        self.play(FadeIn(action, shift=UP * 0.1), run_time=0.9)

        # Flags arrive early.
        self.at(1)
        self.play(Create(track), FadeIn(start), FadeIn(end), run_time=0.8)
        self.play(FadeIn(start_label), FadeIn(end_label),
                  LaggedStart(*[FadeIn(k, shift=DOWN * 0.1) for k in kinds], lag_ratio=0.2), run_time=1.0)

        # Time to negotiate, and what it is worth.
        self.at(2)
        self.play(GrowFromEdge(band, LEFT), run_time=1.2)
        self.play(FadeIn(runway), run_time=0.5)
        self.play(FadeIn(value), run_time=0.8)

        self.at(3)
        self.play(FadeIn(final, shift=UP * 0.1), run_time=1.0)
        self.finish()


SCENES = {
    "00_title": TitleScene,
    "01_problem": ProblemScene,
    "02_flow": FlowScene,
    "03_dollars": DollarsScene,
    "04_action": ActionScene,
}
