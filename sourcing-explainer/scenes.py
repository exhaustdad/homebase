"""The eight scenes, value first. Every animation starts on a narration sentence beat."""

import random

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Create, DashedVMobject, Dot, FadeIn,
    FadeOut, GrowFromEdge, LaggedStart, Line, RoundedRectangle, Text,
    Transform, VGroup,
)

import config as C
from common import BeatScene, card, chip, label


def vendor_tag(name, desc):
    """A gold pill such as 'Vendor Y  .  Data partner for a launch', pinned top-left."""
    n = label(name, size=26, color=C.GOLD, weight="SEMIBOLD")
    d = label(desc, size=24)
    t = VGroup(n, Dot(radius=0.045, color=C.MUTED), d).arrange(RIGHT, buff=0.3)
    b = card(t.width + 0.7, 0.66, stroke=C.GOLD, width=2.5, radius=0.33)
    b.move_to([-6.6 + b.width / 2, 2.3, 0])
    t.move_to(b)
    return b, t


class S00Want(BeatScene):
    key = "00_want"

    def construct(self):
        lead = Text("Every CFO wants two things.", font=C.SERIF, font_size=44, color=C.MUTED)
        one = Text("No surprises.", font=C.SERIF, font_size=76, color=C.INK)
        two = Text("Spend that moves the business forward.", font=C.SERIF, font_size=48, color=C.INK)
        VGroup(lead, one, two).arrange(DOWN, buff=0.6).move_to([0, -0.1, 0])

        self.beat(0)  # Every CFO wants two things.
        self.run(FadeIn(lead, shift=UP * 0.12), run_time=0.9)
        self.beat(1)  # No surprises.
        self.run(FadeIn(one, shift=UP * 0.15), run_time=0.7)
        self.beat(2)  # Spend that moves the business forward.
        self.run(FadeIn(two, shift=UP * 0.15), run_time=0.9)
        self.finish()


class S01Promise(BeatScene):
    key = "01_promise"

    def construct(self):
        colors = [C.INK, C.INK, C.GOLD]
        lines = VGroup(*[Text(t, font=C.SERIF, font_size=72, color=c) for t, c in zip(C.PROMISE, colors)])
        lines.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rule = Line(ORIGIN, RIGHT * 1.4, stroke_color=C.GOLD, stroke_width=4)
        hub = label("The Supplier Intelligence Hub", size=30, color=C.MUTED)
        VGroup(lines, rule, hub).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to([0, -0.1, 0])

        # "So here is the promise: no surprises, faster yeses, and every yes backed by data."
        for line, word_index in zip(lines, (5, 7, 11)):
            self.at(C.beats(self.key)[0] + word_index / C.WORDS_PER_SECOND)
            self.run(FadeIn(line, shift=UP * 0.15), run_time=0.7)
        self.run(Create(rule), FadeIn(hub), run_time=0.8)
        self.finish()


class S02Growth(BeatScene):
    key = "02_growth"

    UNIT = 0.6  # scene units per week
    X0 = -2.1

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        tag_b, tag_t = vendor_tag("Vendor Y", "Data partner for a launch")

        y1, y2, ya = 1.0, -0.3, -1.15

        def bar(weeks, color, y):
            w = weeks * self.UNIT
            return RoundedRectangle(width=w, height=0.5, corner_radius=0.08, stroke_width=0,
                                    fill_color=color, fill_opacity=1).move_to([self.X0 + w / 2, y, 0])

        def row_label(text, y):
            t = label(text, size=26)
            return t.move_to([self.X0 - 0.3 - t.width / 2, y, 0])

        b1, b2 = bar(C.TYPICAL_WEEKS, C.MUTED, y1), bar(C.HUB_WEEKS, C.TEAL, y2)
        assert abs(b1.width / b2.width - C.TYPICAL_WEEKS / C.HUB_WEEKS) < 1e-9
        l1 = row_label(f"Typical cycle: {C.TYPICAL_WEEKS} weeks", y1)
        l2 = row_label(f"With the hub: {C.HUB_WEEKS} weeks", y2)

        axis = Line([self.X0, ya, 0], [self.X0 + C.TYPICAL_WEEKS * self.UNIT, ya, 0],
                    stroke_color=C.LINE, stroke_width=2.5)
        ticks, tick_labels = VGroup(), VGroup()
        for wk in range(0, C.TYPICAL_WEEKS + 1, C.HUB_WEEKS):
            x = self.X0 + wk * self.UNIT
            ticks.add(Line([x, ya - 0.08, 0], [x, ya + 0.08, 0], stroke_color=C.MUTED, stroke_width=2))
            tick_labels.add(label(str(wk), size=20, color=C.MUTED).move_to([x, ya - 0.35, 0]))
        weeks_lab = label("weeks", size=20, color=C.MUTED).next_to(tick_labels[-1], RIGHT, buff=0.25)

        gx0 = self.X0 + C.HUB_WEEKS * self.UNIT
        gx1 = self.X0 + C.TYPICAL_WEEKS * self.UNIT
        assert abs((gx1 - gx0) - C.WEEKS_SAVED * self.UNIT) < 1e-9
        gap_box = RoundedRectangle(width=gx1 - gx0, height=0.62, corner_radius=0.1,
                                   stroke_color=C.GOLD, stroke_width=4, fill_color=C.TEAL, fill_opacity=0)
        gap_box.move_to([(gx0 + gx1) / 2, y2, 0])
        gap_lab = label(f"{C.WEEKS_SAVED} weeks earlier to launch", size=28, color=C.GOLD, weight="SEMIBOLD")
        gap_lab.move_to([(gx0 + gx1) / 2, -2.35, 0])
        rev_lab = label(f"+{C.WEEKS_SAVED} weeks of revenue", size=24, color=C.INK, weight="SEMIBOLD")
        rev_lab.move_to(gap_box)

        self.beat(0)  # First, a faster yes.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.beat(1)  # Vendor Y.
        self.run(FadeIn(tag_b), FadeIn(tag_t), run_time=0.8)
        self.run(Create(axis), FadeIn(ticks), FadeIn(tick_labels), FadeIn(weeks_lab), run_time=1.0)
        self.beat(2)  # Typical cycle: 12 weeks.
        self.run(FadeIn(l1), GrowFromEdge(b1, LEFT), run_time=1.6)
        self.beat(3)  # With the hub: 4 weeks.
        self.run(FadeIn(l2), GrowFromEdge(b2, LEFT), run_time=1.0)
        self.beat(4)  # The launch ships 8 weeks earlier.
        self.run(Create(gap_box), run_time=0.9)
        self.run(FadeIn(gap_lab, shift=UP * 0.1), run_time=0.7)
        self.beat(5)  # 8 more weeks of revenue.
        self.run(gap_box.animate.set_fill(C.TEAL, opacity=0.35), FadeIn(rev_lab), run_time=1.2)
        self.finish()


class S03Revenue(BeatScene):
    key = "03_revenue"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        tag_b, tag_t = vendor_tag("Vendor Z", f"Supports {C.VENDOR_Z_ROLE}")

        yl, x_today = -1.0, -5.4
        scale = 10.8 / C.DAYS_TO_PEAK
        x_peak = x_today + C.DAYS_TO_PEAK * scale
        line = Line([x_today, yl, 0], [x_peak, yl, 0], stroke_color=C.LINE, stroke_width=3)
        d_today = Dot([x_today, yl, 0], radius=0.09, color=C.INK)
        d_peak = Dot([x_peak, yl, 0], radius=0.09, color=C.GOLD)
        t_today = label("Today", size=22, color=C.MUTED).move_to([x_today, yl - 0.4, 0])
        t_peak = label("Peak season", size=22, color=C.GOLD).next_to(d_peak, DOWN, buff=0.25)
        t_peak.align_to(d_peak, RIGHT).shift(RIGHT * 0.09)

        sigs = VGroup(
            chip(f"Usage at {C.pct(C.USAGE)} of capacity", stroke=C.CORAL),
            chip("Vendor acquired", stroke=C.GOLD),
            chip(f"Peak season in {C.DAYS_TO_PEAK} days", stroke=C.BLUE),
        ).arrange(RIGHT, buff=0.3).move_to([0, 0.85, 0])

        act = chip("Act now", color=C.GOLD, stroke=C.GOLD, size=24)
        act.move_to([x_today + 0.35, yl + 0.65, 0])
        span = Line([x_today, yl, 0], [x_peak, yl, 0], stroke_color=C.TEAL, stroke_width=6)
        span_lab = label(f"{C.DAYS_TO_PEAK} days to act", size=24, color=C.TEAL, weight="SEMIBOLD")
        span_lab.move_to([0, yl - 0.45, 0])
        x_sec = x_today + 0.75 * C.DAYS_TO_PEAK * scale
        d_sec = Dot([x_sec, yl, 0], radius=0.09, color=C.TEAL)
        secured = chip("Capacity and backup secured", color=C.TEAL, stroke=C.TEAL)
        secured.move_to([x_sec - 0.4, yl + 0.65, 0])
        final = Text("Peak revenue protected.", font=C.SERIF, font_size=46, color=C.GOLD)
        final.move_to([0, -2.75, 0])

        self.beat(0)  # Next, no surprises.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.7)
        self.beat(1)  # Vendor Z supports ad delivery.
        self.run(FadeIn(tag_b), FadeIn(tag_t), run_time=0.6)
        self.run(Create(line), FadeIn(d_today), FadeIn(t_today), FadeIn(d_peak), FadeIn(t_peak), run_time=1.1)
        for i in range(3):  # Three signals, one per sentence.
            self.beat(2 + i)
            self.run(FadeIn(sigs[i], shift=DOWN * 0.15), run_time=0.7)
        self.beat(5)  # Alone, each signal is noise.
        self.run(sigs.animate.set_opacity(0.45), run_time=0.8)
        self.beat(6)  # Together, they say act now.
        self.run(*[sg.animate.move_to(act).scale(0.4).set_opacity(0) for sg in sigs], run_time=0.8)
        self.remove(sigs)
        self.run(FadeIn(act, scale=1.2), run_time=0.5)
        self.beat(7)  # Capacity and a backup before the peak.
        self.run(Create(span), FadeIn(span_lab), run_time=1.3)
        self.run(FadeIn(d_sec, scale=0.5), FadeIn(secured, shift=UP * 0.1), run_time=0.8)
        self.beat(7, delay=2.5)
        self.run(FadeIn(final, shift=UP * 0.12), run_time=1.0)
        self.finish()


class S04Margin(BeatScene):
    key = "04_margin"

    UNIT = 120.0  # scene units per 1.0 of cap (so 6% is 7.2 units)
    X0 = -3.2
    BAR_H = 0.5

    def bar(self, cap, color, y):
        w = cap * self.UNIT
        return RoundedRectangle(width=w, height=self.BAR_H, corner_radius=0.08, stroke_width=0,
                                fill_color=color, fill_opacity=1).move_to([self.X0 + w / 2, y, 0])

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        spend_txt = f"Vendor X, annual spend: {C.usd(C.SPEND)} (illustrative)"
        spend = Text(spend_txt, font=C.SANS, font_size=30, color=C.INK,
                     t2c={"(illustrative)": C.MUTED})
        spend.move_to([-6.6 + spend.width / 2, 2.3, 0])

        y_old, y_new = 1.3, -0.05
        old_bar = self.bar(C.OLD_CAP, C.BLUE, y_old)
        new_bar = self.bar(C.NEW_CAP, C.CORAL, y_new)
        assert abs(new_bar.width - 3 * old_bar.width) < 1e-9

        def row_label(text, y):
            t = label(text, size=26)
            return t.move_to([self.X0 - 0.3 - t.width / 2, y, 0])

        old_lab = row_label(f"Old cap: {C.pct(C.OLD_CAP)}", y_old)
        new_lab = row_label(f"Draft cap: {C.pct(C.NEW_CAP)}", y_new)
        old_val = label(C.usd(C.old_max), size=28, color=C.BLUE, weight="SEMIBOLD").next_to(old_bar, RIGHT, buff=0.25)
        new_val = label(C.usd(C.new_max), size=28, color=C.CORAL, weight="SEMIBOLD").next_to(new_bar, RIGHT, buff=0.25)
        old_f = label(f"{C.usd(C.SPEND)} × {C.pct(C.OLD_CAP)} = {C.usd(C.old_max)}", size=22, color=C.MUTED)
        new_f = label(f"{C.usd(C.SPEND)} × {C.pct(C.NEW_CAP)} = {C.usd(C.new_max)}", size=22, color=C.MUTED)
        old_f.next_to(old_bar, DOWN, buff=0.18).align_to(old_bar, LEFT)
        new_f.next_to(new_bar, DOWN, buff=0.18).align_to(new_bar, LEFT)

        gx0, gx1 = self.X0 + C.OLD_CAP * self.UNIT, self.X0 + C.NEW_CAP * self.UNIT
        assert abs((gx1 - gx0) - C.gap / C.SPEND * self.UNIT) < 1e-9
        gap_box = RoundedRectangle(width=gx1 - gx0 + 0.12, height=self.BAR_H + 0.18, corner_radius=0.1,
                                   stroke_color=C.GOLD, stroke_width=4, fill_opacity=0)
        gap_box.move_to([(gx0 + gx1) / 2, y_new, 0])
        gap_lab = label(f"{C.usd(C.gap)} more exposure each year", size=28, color=C.GOLD, weight="SEMIBOLD")
        gap_lab.next_to(gap_box, DOWN, buff=0.55).align_to(gap_box, RIGHT)
        gap_f = label(f"{C.usd(C.new_max)} - {C.usd(C.old_max)} = {C.usd(C.gap)}", size=22, color=C.MUTED)
        gap_f.next_to(gap_lab, DOWN, buff=0.16).align_to(gap_lab, RIGHT)
        note = label("Annual view. Multi-year compounding is not shown.", size=20, color=C.MUTED)
        note.move_to([-6.6 + note.width / 2, gap_f.get_y() - 0.55, 0])

        act_txt = label(f"Action: ask to restore the {C.pct(C.OLD_CAP)} cap before the renewal date.", size=28)
        act_box = card(act_txt.width + 0.8, 0.85, stroke=C.GOLD, width=3)
        act_box.move_to([-6.6 + act_box.width / 2, -3.15, 0])
        act_txt.move_to(act_box)

        self.beat(0)  # And no leakage.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.beat(1)  # Draft raises the cap from 2 to 6 percent.
        self.run(FadeIn(spend), run_time=0.7)
        self.run(FadeIn(old_lab), GrowFromEdge(old_bar, LEFT), run_time=1.0)
        self.beat(1, delay=3.2)
        self.run(FadeIn(new_lab), GrowFromEdge(new_bar, LEFT), run_time=1.2)
        self.beat(2)  # On 1 million dollars, 40,000 a year.
        self.run(FadeIn(old_val), FadeIn(old_f), FadeIn(new_val), FadeIn(new_f), run_time=1.0)
        self.run(Create(gap_box), run_time=0.8)
        self.run(FadeIn(gap_lab, shift=UP * 0.1), run_time=0.7)
        self.run(FadeIn(gap_f), run_time=0.5)
        self.beat(3)  # The move.
        self.run(FadeIn(note), FadeIn(act_box), FadeIn(act_txt), run_time=1.2)
        self.finish()


class S06How(BeatScene):
    key = "06_how"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])

        dots = VGroup(*[Dot(radius=0.05, color=C.MUTED) for _ in range(C.VENDOR_COUNT)])
        dots.arrange_in_grid(rows=C.GRID_ROWS, cols=C.GRID_COLS, buff=0.13)
        cap1 = label(f"{C.VENDOR_COUNT} vendors", size=30, weight="SEMIBOLD")
        cap2 = label(f"Signals in {len(C.SOURCES)} systems", size=24, color=C.MUTED)
        cap3 = label("No one can watch them all.", size=24, color=C.CORAL)
        caps = VGroup(cap1, cap2, cap3).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        VGroup(dots, caps).arrange(RIGHT, buff=0.7).move_to([0, 1.25, 0])

        rng = random.Random(7)
        flagged = rng.sample(range(C.VENDOR_COUNT), C.FLAGGED)
        colors = [C.CORAL] * C.FLAGGED_CORAL + [C.GOLD] * C.FLAGGED_GOLD
        rng.shuffle(colors)

        stages = [
            ("Read", "Contracts, reviews, news", C.BLUE),
            ("Score", "Signal, posture, source", C.CORAL),
            ("Recommend", "Brief and next move", C.TEAL),
            ("Decide", "A person makes the call", C.GOLD),
        ]
        cards, inner = VGroup(), []
        for name, sub, color in stages:
            c = card(3.15, 1.45, stroke=C.LINE)
            n = label(name, size=30, weight="SEMIBOLD")
            s = label(sub, size=18, color=C.MUTED)
            VGroup(n, s).arrange(DOWN, buff=0.16)
            cards.add(c)
            inner.append(VGroup(n, s).set_z_index(1))
        cards.arrange(RIGHT, buff=0.3).move_to([0, -1.75, 0])
        for c, g in zip(cards, inner):
            g.move_to(c)
        arrows = VGroup(*[
            Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.04, stroke_width=3,
                  stroke_color=C.MUTED, max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=20)
            for i in range(3)
        ])

        def bracket(left, right, text, color):
            y = cards.get_top()[1] + 0.3
            ln = Line([left, y, 0], [right, y, 0], stroke_color=color, stroke_width=2.5)
            ends = VGroup(Line([left, y, 0], [left, y - 0.15, 0], stroke_color=color, stroke_width=2.5),
                          Line([right, y, 0], [right, y - 0.15, 0], stroke_color=color, stroke_width=2.5))
            t = label(text, size=22, color=color, weight="SEMIBOLD").move_to([(left + right) / 2, y + 0.27, 0])
            return VGroup(ln, ends), t

        ai_br, ai_t = bracket(cards[0].get_left()[0], cards[2].get_right()[0], "AI agents", C.TEAL)
        hu_br, hu_t = bracket(cards[3].get_left()[0], cards[3].get_right()[0], "A person", C.GOLD)

        self.beat(0)  # How AI fits in.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.beat(1)  # 150 vendors, five systems.
        self.run(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.01), run_time=1.8)
        self.run(FadeIn(cap1), FadeIn(cap2), run_time=0.8)
        self.beat(2)  # No person can watch them all.
        self.run(LaggedStart(*[dots[i].animate.set_color(c).scale(1.4) for i, c in zip(flagged, colors)],
                             lag_ratio=0.08), FadeIn(cap3), run_time=1.4)
        self.beat(3)  # AI agents read.
        self.run(Create(ai_br), FadeIn(ai_t), run_time=0.8)
        self.run(FadeIn(cards[0]), FadeIn(inner[0]), run_time=0.6)
        self.run(cards[0].animate.set_stroke(C.BLUE, width=3), run_time=0.4)
        for i in (1, 2):  # Score, then recommend.
            self.beat(3 + i)
            self.run(Create(arrows[i - 1]), FadeIn(cards[i]), FadeIn(inner[i]), run_time=0.8)
            self.run(cards[i].animate.set_stroke(stages[i][2], width=3), run_time=0.4)
        self.beat(6)  # A person makes the call.
        self.run(Create(arrows[2]), FadeIn(cards[3]), FadeIn(inner[3]), Create(hu_br), FadeIn(hu_t),
                 run_time=0.9)
        self.run(cards[3].animate.set_stroke(C.GOLD, width=4.5), run_time=0.5)
        self.finish()


class S05Data(BeatScene):
    key = "05_data"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        rows_spec = [
            (f"{C.WEEKS_SAVED} weeks", "sooner to launch", C.TEAL, "Sourcing cycle log", "Vendor Y"),
            (C.pct(C.USAGE), "of capacity used", C.BLUE, "Usage data", "Vendor Z"),
            (C.usd(C.gap), "a year in added exposure", C.GOLD, "Contract draft, price cap clause", "Vendor X"),
        ]
        values, sources, arrows = VGroup(), VGroup(), VGroup()
        for i, (val, sub, color, src, vendor) in enumerate(rows_spec):
            y = 1.35 - i * 1.45
            v = Text(val, font=C.SERIF, font_size=54, color=color)
            sb = label(sub, size=20, color=C.MUTED)
            vg = VGroup(v, sb).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            vg.move_to([-6.4 + vg.width / 2, y, 0])
            head = label(f"Source: {vendor}", size=18, color=C.MUTED)
            rec = label(src, size=24, weight="SEMIBOLD")
            txt = VGroup(head, rec).arrange(DOWN, buff=0.1, aligned_edge=LEFT).set_z_index(1)
            box = card(6.3, 1.05, stroke=color, width=2.5).move_to([3.65, y, 0])
            txt.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.35)
            values.add(vg)
            sources.add(VGroup(box, txt))
            arrows.add(Arrow(box.get_left(), [-1.9, y, 0], buff=0.1, stroke_width=3, stroke_color=color,
                             max_tip_length_to_length_ratio=0.15))

        claim = chip("Claim with no source", color=C.MUTED, stroke=C.CORAL, size=24)
        strike = Line(claim.get_left(), claim.get_right(), stroke_color=C.CORAL, stroke_width=4)
        rule = Text("No source, no number.", font=C.SERIF, font_size=46, color=C.GOLD)
        VGroup(VGroup(claim, strike), rule).arrange(RIGHT, buff=0.9).move_to([0, -3.0, 0])
        strike.move_to(claim)

        self.beat(0)  # Every yes is backed by data.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.run(LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in values], lag_ratio=0.3), run_time=1.2)
        self.beat(1)  # Each number links to the record it came from.
        self.run(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.3), run_time=1.2)
        for i in range(3):  # Sourcing log, usage data, contract draft.
            self.beat(2 + i)
            self.run(FadeIn(sources[i], shift=LEFT * 0.15), run_time=0.8)
        self.beat(5)  # No source, no number.
        self.run(FadeIn(claim), run_time=0.3)
        self.run(Create(strike), claim.animate.set_opacity(0.4), run_time=0.4)
        self.run(FadeIn(rule, shift=UP * 0.1), run_time=0.7)
        self.finish()


class S07Close(BeatScene):
    key = "07_close"

    def construct(self):
        hub = Text("The Supplier Intelligence Hub", font=C.SERIF, font_size=56, color=C.INK)
        rule = Line(ORIGIN, RIGHT * 1.4, stroke_color=C.GOLD, stroke_width=4)
        ask = Text("“Did we see this coming?”", font=C.SERIF, font_size=48, color=C.MUTED)
        yes = Text("Yes.", font=C.SERIF, font_size=84, color=C.GOLD)
        colors = [C.TEAL, C.BLUE, C.GOLD]
        pills = VGroup(*[chip(t, color=c, stroke=c, size=28, h=0.7) for t, c in zip(C.PROMISE, colors)])
        pills.arrange(RIGHT, buff=0.45)
        VGroup(hub, rule, ask, yes, pills).arrange(DOWN, buff=0.45).move_to([0, -0.05, 0])

        self.beat(0)  # I built the Supplier Intelligence Hub.
        self.run(FadeIn(hub, shift=UP * 0.12), Create(rule), run_time=1.0)
        self.beat(1)  # When the CFO asks, did we see this coming...
        self.run(FadeIn(ask, shift=UP * 0.1), run_time=0.9)
        self.beat(1, delay=10 / C.WORDS_PER_SECOND)  # ...the answer is yes.
        self.run(FadeIn(yes, scale=1.15), run_time=0.8)
        for i in range(3):  # No surprises. Faster yeses. Backed by data.
            self.beat(2 + i)
            self.run(FadeIn(pills[i], shift=UP * 0.1), run_time=0.6)
        self.finish()
