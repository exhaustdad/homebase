"""Manim scenes for the sourcing explainer.

Render with build.py, or directly:
    manim -ql scenes.py VendorsScene
"""

import random

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, UR, ORIGIN,
    AnimationGroup, Arrow, Circle, Create, DashedVMobject, Dot, FadeIn, FadeOut,
    GrowFromEdge, LaggedStart, Line, Rectangle, RoundedRectangle, Scene, Text, VGroup,
    config as manim_config, smooth,
)
import numpy as np

from config import (
    AGENTS, BADGE_TEXT, BG, BLUE, CHOSEN_POSTURE, CORAL, CORAL_SIGNALS, GOLD,
    GOLD_SIGNALS, GRID_COLS, GRID_ROWS, INK, LINE, MUTED, NEW_CAP, OLD_CAP,
    PANEL, POSTURES, RENEWAL_DAYS, SANS, SERIF, SOURCES, SPEND, TEAL, VENDOR,
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


def chip(label, width=3.0):
    frame = box(width, 0.58, radius=0.29)
    t = stack([sans(label, 22, INK)], frame.get_center())[0]
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


class TitleScene(ExplainerScene):
    KEY = "00_title"

    def construct(self):
        l1 = serif("From Vendor Noise", 78)
        l2 = serif("to Sourcing Decisions", 78)
        sub = sans("The Supplier Intelligence Hub", 30, BLUE)
        block = VGroup(l1, l2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        sub.next_to(block, DOWN, buff=0.6, aligned_edge=LEFT)
        VGroup(block, sub).move_to(ORIGIN + DOWN * 0.1)

        self.play(FadeIn(l1, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(l2, shift=UP * 0.15), run_time=1.2)
        self.wait(0.3)
        self.play(FadeIn(sub), run_time=1.0)
        self.finish()


class VendorsScene(ExplainerScene):
    KEY = "01_vendors"
    TITLE = "Too many vendors, too many places"

    def construct(self):
        step = 0.4
        dots = VGroup(*[
            Dot(radius=0.075, color=MUTED, fill_opacity=0.55)
            for _ in range(GRID_COLS * GRID_ROWS)
        ])
        dots.arrange_in_grid(rows=GRID_ROWS, cols=GRID_COLS, buff=step - 0.15)
        dots.move_to([-2.7, -0.25, 0])

        rng = random.Random(7)
        picks = rng.sample(range(len(dots)), GOLD_SIGNALS + CORAL_SIGNALS)
        gold_idx, coral_idx = picks[:GOLD_SIGNALS], picks[GOLD_SIGNALS:]

        chips = VGroup(*[chip(s, 3.1) for s in SOURCES]).arrange(DOWN, buff=0.26)
        chips.move_to([4.55, -0.25, 0])

        warning = sans("No single view of all signals.", 30, CORAL, weight="MEDIUM")
        warning.move_to([0, -3.15, 0])

        # 150 vendors appear.
        self.at(0)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.012), run_time=2.6)

        # One dot is one vendor.
        self.at(1)
        one = dots[GRID_COLS * 4 + 3]
        ring = Circle(radius=0.2, color=INK, stroke_width=2).move_to(one)
        self.play(Create(ring), one.animate.set_fill(INK, opacity=1), run_time=0.9)

        # Signals: gold first, then coral for action now.
        self.at(2)
        self.play(
            FadeOut(ring), one.animate.set_fill(MUTED, opacity=0.55),
            *[dots[i].animate.set_fill(GOLD, opacity=1).scale(1.35) for i in gold_idx],
            run_time=1.3,
        )
        self.at(3)
        self.play(*[dots[i].animate.set_fill(CORAL, opacity=1).scale(1.35) for i in coral_idx], run_time=1.3)

        # Signals live in separate systems.
        self.at(4)
        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.25), run_time=2.0)

        self.at(5)
        self.play(FadeIn(warning, shift=UP * 0.1), run_time=1.2)
        self.finish()


class FlowScene(ExplainerScene):
    KEY = "02_flow"
    TITLE = "One flow, two speeds"

    def construct(self):
        chips = VGroup(*[chip(s, 2.9) for s in SOURCES]).arrange(DOWN, buff=0.26)
        chips.move_to([-5.0, -0.3, 0])

        bus_x = -3.05
        feeds = VGroup(*[
            Line(c.get_right(), [bus_x, c.get_y(), 0], color=MUTED, stroke_width=2.5) for c in chips
        ])

        weekly = labeled_box("Weekly brief", "The full picture", 3.3, 1.25, BLUE)
        warn = labeled_box("Early warning", "Always on", 3.3, 1.25, CORAL)
        weekly.move_to([0.2, 1.05, 0])
        warn.move_to([0.2, -1.65, 0])

        hub = labeled_box("Slack hub", "One place", 2.9, 1.25, GOLD)
        hub.move_to([4.85, -0.3, 0])

        def arrow(a, b, color=MUTED):
            return Arrow(a, b, buff=0.08, color=color, stroke_width=3,
                         max_tip_length_to_length_ratio=0.12, tip_length=0.18)

        a_weekly = arrow([bus_x, weekly.get_y(), 0], weekly.get_left())
        a_warn = arrow([bus_x, warn.get_y(), 0], warn.get_left())
        bus_top = max(chips[0].get_y(), weekly.get_y())
        bus_bottom = min(chips[-1].get_y(), warn.get_y())
        bus_full = Line([bus_x, bus_top, 0], [bus_x, bus_bottom, 0], color=MUTED, stroke_width=2.5)
        a_w_hub = arrow(weekly.get_right(), hub.get_left() + UP * 0.25)
        a_e_hub = arrow(warn.get_right(), hub.get_left() + DOWN * 0.25)

        self.at(0)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in chips], lag_ratio=0.2), run_time=1.8)

        # Reads the sources.
        self.at(1)
        self.play(Create(feeds), run_time=0.9)
        self.play(Create(bus_full), run_time=0.7)

        self.at(2)
        self.play(Create(a_weekly), run_time=0.8)
        self.play(FadeIn(weekly), run_time=0.9)

        self.at(3)
        self.play(Create(a_warn), run_time=0.8)
        self.play(FadeIn(warn), run_time=0.9)

        # Both send output to one place.
        self.at(4)
        self.play(Create(a_w_hub), Create(a_e_hub), run_time=1.0)
        self.play(FadeIn(hub), run_time=1.0)
        self.finish()


class PostureScene(ExplainerScene):
    KEY = "03_posture"
    TITLE = "Every signal gets a posture"

    def construct(self):
        w, h = 4.15, 1.6
        cells = []
        for name, desc in POSTURES:
            frame = box(w, h)
            head = sans(name, 27, INK, weight="MEDIUM")
            sub = sans(desc, 21, MUTED)
            stack([head, sub], frame.get_center() + DOWN * 0.08, gap=0.3)
            cells.append(VGroup(frame, head, sub))
        grid = VGroup(*cells).arrange_in_grid(rows=2, cols=2, buff=(0.35, 0.45))
        grid.move_to([-2.35, -0.35, 0])

        tag_frame = box(2.1, 0.56, stroke=GOLD, radius=0.28)
        tag_label = sans(VENDOR, 23, GOLD, weight="MEDIUM").move_to(tag_frame)
        tag = VGroup(tag_frame, tag_label)
        fact1 = sans(f"Renews in {RENEWAL_DAYS} days", 22, INK)
        fact2 = sans("Draft raises the price cap", 22, INK)
        facts = VGroup(fact1, fact2).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        card = VGroup(tag, facts).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        card.move_to([4.75, -0.35, 0])

        target = cells[[p[0] for p in POSTURES].index(CHOSEN_POSTURE)]
        others = [c for c in cells if c is not target]

        self.at(1)
        self.play(LaggedStart(*[draw_cell(c) for c in cells], lag_ratio=0.2), run_time=1.6)

        self.at(2)
        self.play(LaggedStart(*[FadeIn(c[2]) for c in cells], lag_ratio=0.2), run_time=1.6)

        self.at(3)
        self.play(FadeIn(tag, shift=LEFT * 0.2), run_time=0.9)

        self.at(4)
        self.play(FadeIn(fact1), run_time=0.8)
        self.at(4, offset=2.2)
        self.play(FadeIn(fact2), run_time=0.8)

        # The tag glides onto Increase Leverage.
        self.at(5)
        self.play(FadeOut(facts), run_time=0.5)
        self.play(
            tag.animate.move_to(target[0].get_top()),
            target[0].animate.set_stroke(GOLD, width=3.5),
            *[c.animate.set_opacity(0.4) for c in others],
            run_time=1.4, rate_func=smooth,
        )

        self.at(6)
        self.play(target[2].animate.set_color(GOLD), run_time=0.9)
        self.finish()


def draw_cell(cell):
    """Draw a posture box and fade in its heading (descriptor comes later)."""
    return AnimationGroup(FadeIn(cell[0]), FadeIn(cell[1]))


class DollarsScene(ExplainerScene):
    KEY = "04_dollars"
    TITLE = "From signal to dollars"

    def construct(self):
        x0 = -3.6
        unit = 6.0 / new_max  # scene units per dollar; one scale for both bars
        bar_h = 0.5
        y_old, y_new = 1.25, -0.35

        spend = sans(f"{VENDOR}, annual spend: {money(SPEND)} (illustrative)", 26, INK)
        spend.move_to([0, 2.35, 0]).align_to([-6.55, 0, 0], LEFT)

        def bar(value, color, y):
            r = Rectangle(width=value * unit, height=bar_h, stroke_width=0,
                          fill_color=color, fill_opacity=0.9)
            r.move_to([x0, y, 0], aligned_edge=LEFT)
            return r

        old_bar = bar(old_max, BLUE, y_old)
        new_bar = bar(new_max, CORAL, y_new)
        assert abs(new_bar.width - 3 * old_bar.width) < 1e-9

        old_label = sans(f"Old cap: {pct(OLD_CAP)}", 24, BLUE, weight="MEDIUM")
        new_label = sans(f"Draft cap: {pct(NEW_CAP)}", 24, CORAL, weight="MEDIUM")
        old_label.move_to([0, y_old, 0]).align_to([-6.55, 0, 0], LEFT)
        new_label.move_to([0, y_new, 0]).align_to([-6.55, 0, 0], LEFT)

        old_val = sans(money(old_max), 26, INK, weight="MEDIUM").next_to(old_bar, RIGHT, buff=0.25)
        new_val = sans(money(new_max), 26, INK, weight="MEDIUM").next_to(new_bar, RIGHT, buff=0.25)

        old_f = sans(f"{money(SPEND)} × {pct(OLD_CAP)} = {money(old_max)}", 20, MUTED)
        new_f = sans(f"{money(SPEND)} × {pct(NEW_CAP)} = {money(new_max)}", 20, MUTED)
        old_f.next_to(old_bar, DOWN, buff=0.18).align_to(old_bar, LEFT)
        new_f.next_to(new_bar, DOWN, buff=0.18).align_to(new_bar, LEFT)

        gap_left = x0 + old_max * unit
        gap_box = Rectangle(width=gap * unit, height=bar_h + 0.2, stroke_color=GOLD,
                            stroke_width=3.5, fill_opacity=0)
        gap_box.move_to([gap_left, y_new, 0], aligned_edge=LEFT)
        gap_label = sans(f"{money(gap)} more exposure each year", 24, GOLD, weight="MEDIUM")
        gap_f = sans(f"{money(new_max)} - {money(old_max)} = {money(gap)}", 20, MUTED)
        gap_group = VGroup(gap_label, gap_f).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        gap_group.next_to(new_f, DOWN, buff=0.38).align_to(gap_box, LEFT)

        note = sans("Annual view. Multi-year compounding is not shown.", 17, MUTED)
        note.next_to(gap_group, DOWN, buff=0.22).align_to(gap_box, LEFT)

        action_text = sans(
            f"Action: ask to restore the {pct(OLD_CAP)} cap before the renewal date.", 24, INK,
        )
        action_frame = box(action_text.width + 0.6, action_text.height + 0.45, stroke=GOLD)
        action = VGroup(action_frame, action_text.move_to(action_frame))
        action.move_to([0, -3.3, 0])

        part_b = self.part_starts[1]

        # Part 1. Fictional, illustrative: the badge lifts briefly.
        self.at(1)
        self.play(self.badge[0].animate.set_stroke(GOLD), self.badge[1].animate.set_color(INK), run_time=0.8)
        self.at(2, offset=0.8)
        self.play(self.badge[0].animate.set_stroke(LINE), self.badge[1].animate.set_color(MUTED), run_time=0.8)

        self.at(3)
        self.play(FadeIn(spend), run_time=1.0)

        self.at(4)
        self.play(FadeIn(old_label), run_time=0.7)
        self.play(GrowFromEdge(old_bar, LEFT), run_time=1.4)

        self.at(5)
        self.play(FadeIn(old_val), FadeIn(old_f), run_time=1.0)

        self.at(6)
        self.play(FadeIn(new_label), run_time=0.7)
        self.play(GrowFromEdge(new_bar, LEFT), run_time=1.8)

        self.at(7)
        self.play(FadeIn(new_val), FadeIn(new_f), run_time=1.0)

        # Part 2 starts at part_b; nothing moves before its first sentence.
        self.hold_until(part_b)
        self.at(8)
        self.play(Create(gap_box), run_time=1.3)
        self.play(FadeIn(gap_group), run_time=1.0)
        self.play(FadeIn(note), run_time=0.8)

        self.at(9)
        self.play(FadeIn(action, shift=UP * 0.1), run_time=1.2)
        self.finish()


class AgentsScene(ExplainerScene):
    KEY = "05_agents"
    TITLE = "Six agents, one hub"

    def construct(self):
        center = np.array([0, -0.4, 0])
        hub_circle = Circle(radius=1.0, stroke_color=GOLD, stroke_width=3.5,
                            fill_color=PANEL, fill_opacity=1).move_to(center)
        hub_text = sans("Slack hub", 26, INK, weight="MEDIUM").move_to(center)

        a, b = 4.75, 2.35
        angles = [90, 30, -30, -90, -150, 150]
        boxes, lines = [], []
        for (name, role), ang in zip(AGENTS, angles):
            th = np.deg2rad(ang)
            pos = center + np.array([a * np.cos(th), b * np.sin(th), 0])
            frame = box(2.85, 0.95)
            n = sans(name, 22, INK, weight="MEDIUM")
            r = sans(role, 18, MUTED)
            stack([n, r], pos, gap=0.16)
            frame.move_to(pos)
            boxes.append(VGroup(frame, n, r))
            direction = (pos - center) / np.linalg.norm(pos - center)
            start = center + direction * 1.0
            end = self.edge_point(frame, center)
            lines.append(Line(start, end, color=LINE, stroke_width=3))

        self.at(1)
        self.play(Create(hub_circle), FadeIn(hub_text), run_time=1.3)

        self.at(2)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15), run_time=1.4)

        self.at(3)
        self.play(LaggedStart(*[FadeIn(VGroup(bx[0], bx[1])) for bx in boxes], lag_ratio=0.12), run_time=1.6)

        # Together: roles appear and every line lights up toward the hub.
        self.at(4)
        self.play(LaggedStart(*[FadeIn(bx[2]) for bx in boxes], lag_ratio=0.15), run_time=2.0)
        self.play(LaggedStart(*[l.animate.set_color(GOLD) for l in lines], lag_ratio=0.15), run_time=2.0)
        self.finish()

    @staticmethod
    def edge_point(frame, center):
        """Point where the line from center meets the box edge."""
        p = frame.get_center()
        d = p - center
        hw, hh = frame.width / 2, frame.height / 2
        tx = hw / abs(d[0]) if abs(d[0]) > 1e-9 else np.inf
        ty = hh / abs(d[1]) if abs(d[1]) > 1e-9 else np.inf
        return p - d * min(tx, ty)


class AheadScene(ExplainerScene):
    KEY = "06_ahead"
    TITLE = "From reacting to seeing ahead"

    def card(self, heading, items, color, dashed):
        w, h = 6.0, 2.9
        frame = RoundedRectangle(width=w, height=h, corner_radius=0.16,
                                 stroke_color=color, stroke_width=2.5)
        if dashed:
            frame = DashedVMobject(frame, num_dashes=70, dashed_ratio=0.55)
        else:
            frame.set_fill(PANEL, opacity=1)
        head = serif(heading, 34, color if not dashed else INK)
        head.align_to(frame.get_left() + RIGHT * 0.45, LEFT)
        head.shift(UP * (frame.get_top()[1] - 0.45 - head.get_top()[1]))
        rows = []
        for i, item in enumerate(items):
            t = sans(item, 20, INK if not dashed else MUTED)
            line_top = head.get_top()[1] - head.cap - 0.55 - i * 0.6
            t.shift(UP * (line_top - t.get_top()[1]))
            t.align_to(head, LEFT).shift(RIGHT * 0.3)
            d = Dot(radius=0.05, color=color).move_to([t.get_left()[0] - 0.2, line_top - t.cap / 2, 0])
            row = VGroup(d, t)
            rows.append(row)
        return VGroup(frame, head, *rows)

    def construct(self):
        today = self.card("Today", ["Reacts to signals", "Finds issues as they arrive"], MUTED, True)
        nxt = self.card("Next", ["Sees what is coming", "Flags renewals and price changes early"], TEAL, False)
        today.move_to([-3.6, 0.35, 0])
        nxt.move_to([3.6, 0.35, 0])
        arrow = Arrow(today.get_right(), nxt.get_left(), buff=0.12, color=MUTED, stroke_width=3,
                      max_tip_length_to_length_ratio=0.25, tip_length=0.2)

        final = serif("Early action drives the business.", 44, GOLD)
        final.move_to([0, -2.6, 0])

        self.at(0)
        self.play(Create(today[0]), FadeIn(today[1]), run_time=1.2)
        self.play(FadeIn(today[2]), FadeIn(today[3]), run_time=1.0)

        self.at(1)
        self.play(Create(arrow), run_time=0.9)
        self.play(FadeIn(nxt[0]), FadeIn(nxt[1]), FadeIn(nxt[2]), run_time=1.1)

        self.at(2)
        self.play(FadeIn(nxt[3]), run_time=1.0)

        self.at(3)
        self.play(today.animate.set_opacity(0.45), arrow.animate.set_color(TEAL), run_time=1.2)

        self.at(4)
        self.play(FadeIn(final, shift=UP * 0.1), run_time=1.2)
        self.finish()


SCENES = {
    "00_title": TitleScene,
    "01_vendors": VendorsScene,
    "02_flow": FlowScene,
    "03_posture": PostureScene,
    "04_dollars": DollarsScene,
    "05_agents": AgentsScene,
    "06_ahead": AheadScene,
}
