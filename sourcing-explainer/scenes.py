"""The seven scenes. Every animation starts on a narration sentence beat."""

import random

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, PI, RIGHT, UP, AnimationGroup, Circle, Create,
    CubicBezier, DashedVMobject, Dot, FadeIn, FadeOut, GrowFromEdge,
    LaggedStart, Line, Arrow, RoundedRectangle, Text, Transform, Triangle,
    VGroup, there_and_back,
)

import config as C
from common import BeatScene, card, chip, label

SOURCES = ["Contracts", "Renewal dates", "Security reviews", "Usage data", "Market news"]


def flow_curve(p0, p3, color=C.LINE, width=2.5):
    """A calm horizontal S-curve with a small arrowhead at the end."""
    p0, p3 = np.array(p0), np.array(p3)
    k = (p3[0] - p0[0]) * 0.5
    curve = CubicBezier(p0, p0 + RIGHT * k, p3 + LEFT * k, p3, stroke_color=color, stroke_width=width)
    tip = Triangle(fill_color=color, fill_opacity=1, stroke_width=0).scale(0.08).rotate(-PI / 2)
    tip.move_to(p3 + LEFT * 0.07)
    return VGroup(curve, tip)


class S00Title(BeatScene):
    key = "00_title"

    def construct(self):
        l1 = Text("From Vendor Noise", font=C.SERIF, font_size=80, color=C.INK)
        l2 = Text("to Sourcing Decisions", font=C.SERIF, font_size=80, color=C.INK)
        sub = label("The Supplier Intelligence Hub", size=34, color=C.MUTED)
        l2.next_to(l1, DOWN, buff=0.3, aligned_edge=LEFT)
        rule = Line(ORIGIN, RIGHT * 1.4, stroke_color=C.GOLD, stroke_width=4)
        rule.next_to(l2, DOWN, buff=0.55, aligned_edge=LEFT)
        sub.next_to(rule, DOWN, buff=0.4, aligned_edge=LEFT)
        VGroup(l1, l2, rule, sub).move_to(ORIGIN).shift(DOWN * 0.1)

        self.beat(0)
        self.run(FadeIn(l1, shift=UP * 0.15), run_time=1.0)
        self.run(FadeIn(l2, shift=UP * 0.15), run_time=1.0)
        self.run(Create(rule), run_time=0.6)
        self.run(FadeIn(sub), run_time=0.9)
        self.finish()


class S01Vendors(BeatScene):
    key = "01_vendors"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        dots = VGroup(*[Dot(radius=0.075, color=C.MUTED) for _ in range(C.VENDOR_COUNT)])
        dots.arrange_in_grid(rows=C.GRID_ROWS, cols=C.GRID_COLS, buff=0.27)
        dots.move_to([-2.5, -0.15, 0])

        rng = random.Random(7)
        flagged = rng.sample(range(C.VENDOR_COUNT), C.FLAGGED)
        colors = [C.CORAL] * C.FLAGGED_CORAL + [C.GOLD] * C.FLAGGED_GOLD
        rng.shuffle(colors)

        chips = VGroup(*[chip(s) for s in SOURCES]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        chips.move_to([4.6, -0.15, 0])
        note = label("No single view of all signals.", size=32, color=C.CORAL)
        note.move_to([0, -3.05, 0])

        self.beat(0)
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.run(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.012), run_time=2.4)

        self.beat(1)  # Each dot is one vendor.
        one = dots[C.GRID_COLS * 4 + 7]
        ring = Circle(radius=0.2, stroke_color=C.INK, stroke_width=2.5).move_to(one)
        self.run(Create(ring), one.animate.set_color(C.INK), run_time=0.8)
        self.run(FadeOut(ring), one.animate.set_color(C.MUTED), run_time=0.6)

        self.beat(2)  # Some need action now.
        self.run(LaggedStart(*[dots[i].animate.set_color(c).scale(1.35) for i, c in zip(flagged, colors)],
                             lag_ratio=0.12), run_time=1.5)

        self.beat(3)  # Separate systems.
        self.run(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.25), run_time=1.8)

        self.beat(4)
        self.run(FadeIn(note, shift=UP * 0.1), run_time=1.0)
        self.finish()


class S02Flow(BeatScene):
    key = "02_flow"

    def box(self, head, sub, stroke, w=3.6, h=1.5):
        b = card(w, h, stroke=stroke, width=3)
        t1 = label(head, size=30, weight="SEMIBOLD")
        t2 = label(sub, size=22, color=C.MUTED)
        VGroup(t1, t2).arrange(DOWN, buff=0.16).move_to(b)
        return VGroup(b, t1, t2)

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        chips = VGroup(*[chip(s) for s in SOURCES]).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        chips.move_to([-4.9, -0.3, 0])
        weekly = self.box("Weekly brief", "The full picture", C.BLUE).move_to([0.2, 1.05, 0])
        early = self.box("Early warning", "Always on", C.CORAL).move_to([0.2, -1.65, 0])
        hub = self.box("Slack hub", "One place", C.GOLD, w=3.0).move_to([4.85, -0.3, 0])

        to_weekly = VGroup(*[flow_curve(c.get_right() + RIGHT * 0.08, weekly.get_left(), C.BLUE, 2)
                             for c in chips])
        to_early = VGroup(*[flow_curve(c.get_right() + RIGHT * 0.08, early.get_left(), C.CORAL, 2)
                            for c in chips])
        to_hub = VGroup(flow_curve(weekly.get_right(), hub.get_left() + UP * 0.25, C.GOLD, 3),
                        flow_curve(early.get_right(), hub.get_left() + DOWN * 0.25, C.GOLD, 3))

        self.beat(0)
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.run(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in chips], lag_ratio=0.2), run_time=1.6)

        self.beat(1)  # Weekly brief.
        self.run(LaggedStart(*[Create(f) for f in to_weekly], lag_ratio=0.1), run_time=1.2)
        self.run(FadeIn(weekly), run_time=0.8)

        self.beat(2)  # Early warning.
        self.run(LaggedStart(*[Create(f) for f in to_early], lag_ratio=0.1), run_time=1.2)
        self.run(FadeIn(early), run_time=0.8)

        self.beat(3)  # Both land in one place.
        self.run(Create(to_hub), run_time=1.0)
        self.run(FadeIn(hub, scale=0.95), run_time=0.8)
        self.finish()


class S03Posture(BeatScene):
    key = "03_posture"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        postures = [
            ("Protect Margin", "Hold price and terms"),
            ("Increase Leverage", "Use timing and options"),
            ("Reduce Hidden Risk", "Find gaps early"),
            ("Improve Resilience", "Plan backups and exits"),
        ]
        centers = [[-2.75, 1.0, 0], [2.75, 1.0, 0], [-2.75, -1.15, 0], [2.75, -1.15, 0]]
        boxes, heads, descs = VGroup(), VGroup(), VGroup()
        for (h, d), c in zip(postures, centers):
            b = card(5.2, 1.85).move_to(c)
            ht = label(h, size=32, weight="SEMIBOLD")
            dt = label(d, size=24, color=C.MUTED)
            ht.move_to(b.get_corner(UP + LEFT) + RIGHT * (0.35 + ht.width / 2) + DOWN * (0.55 + ht.height / 2) * 1)
            dt.next_to(ht, DOWN, buff=0.22, aligned_edge=LEFT)
            boxes.add(b), heads.add(ht), descs.add(dt)
        lev_box, lev_desc = boxes[1], descs[1]

        tag_name = label("Vendor X", size=32, color=C.GOLD, weight="SEMIBOLD")
        tag_l1 = label(f"Renews in {C.RENEWAL_DAYS} days", size=24)
        tag_l2 = label("Draft raises the price cap", size=24)
        seps = VGroup(Dot(radius=0.045, color=C.MUTED), Dot(radius=0.045, color=C.MUTED))
        tag_text = VGroup(tag_name, seps[0], tag_l1, seps[1], tag_l2).arrange(RIGHT, buff=0.35)
        tag_box = card(tag_text.width + 0.8, 0.8, stroke=C.GOLD, width=3)
        tag_box.move_to([0, -3.05, 0])
        tag_text.move_to(tag_box)

        pill_text = label("Vendor X", size=22, color=C.GOLD, weight="SEMIBOLD")
        pill_box = card(pill_text.width + 0.5, 0.46, stroke=C.GOLD, width=2.5, radius=0.23)
        pill_box.move_to(lev_box.get_corner(UP + RIGHT) + LEFT * (pill_box.width / 2 + 0.3))
        pill_text.move_to(pill_box)

        self.beat(0)
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)

        self.run(LaggedStart(*[FadeIn(VGroup(b, h), shift=UP * 0.15) for b, h in zip(boxes, heads)],
                             lag_ratio=0.2), run_time=1.4)
        self.at(3.4)  # "...tells the team what to do next."
        self.run(LaggedStart(*[FadeIn(d) for d in descs], lag_ratio=0.2), run_time=1.2)

        self.beat(1)  # Take Vendor X.
        self.run(FadeIn(tag_box), FadeIn(tag_name), run_time=0.8)

        self.beat(2)  # Renews in 90 days, draft raises the cap.
        self.run(FadeIn(seps[0]), FadeIn(tag_l1, shift=LEFT * 0.1), run_time=0.7)
        self.run(FadeIn(seps[1]), FadeIn(tag_l2, shift=LEFT * 0.1), run_time=0.7)

        self.beat(3)  # The posture: Increase Leverage.
        self.run(FadeOut(tag_l1), FadeOut(tag_l2), FadeOut(seps), run_time=0.4)
        self.run(Transform(tag_box, pill_box), Transform(tag_name, pill_text),
                 lev_box.animate.set_stroke(C.GOLD, width=4), run_time=1.1)

        self.beat(4)  # Use timing and options.
        self.run(lev_desc.animate.set_color(C.GOLD), run_time=0.8)
        self.finish()


class S04Dollars(BeatScene):
    key = "04_dollars"

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
        # Underline the dollar figure. Text glyphs skip spaces, so index without them.
        s_no_space = spend_txt.replace(" ", "")
        i0 = s_no_space.index(C.usd(C.SPEND))
        figure = spend[i0:i0 + len(C.usd(C.SPEND))]
        underline = Line(figure.get_corner(DOWN + LEFT), figure.get_corner(DOWN + RIGHT),
                         stroke_color=C.GOLD, stroke_width=3).shift(DOWN * 0.1)

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

        # Part 1
        self.beat(0)  # Here is what that is worth.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.beat(1)  # Vendor X is fictional.
        self.run(FadeIn(spend), run_time=1.0)
        self.beat(2)  # Costs 1 million a year.
        self.run(Create(underline), run_time=0.8)
        self.beat(3)  # Old cap 2 percent: at most 20,000.
        self.run(FadeIn(old_lab), GrowFromEdge(old_bar, LEFT), run_time=1.2)
        self.beat(3, delay=3.4)
        self.run(FadeIn(old_val, shift=LEFT * 0.1), FadeIn(old_f), run_time=1.0)
        self.beat(4)  # Draft cap 6 percent: at most 60,000.
        self.run(FadeIn(new_lab), GrowFromEdge(new_bar, LEFT), run_time=1.4)
        self.beat(4, delay=2.2)
        self.run(FadeIn(new_val, shift=LEFT * 0.1), FadeIn(new_f), run_time=1.0)

        # Part 2 starts exactly at beat 5, so the halves cut cleanly.
        self.beat(5)  # That is 40,000 of added exposure.
        self.run(Create(gap_box), run_time=1.0)
        self.run(FadeIn(gap_lab, shift=UP * 0.1), run_time=0.8)
        self.run(FadeIn(gap_f), run_time=0.7)
        self.run(FadeIn(note), run_time=0.6)
        self.beat(6)  # The move.
        self.run(FadeIn(act_box), FadeIn(act_txt), run_time=1.2)
        self.finish()


class S07Agents(BeatScene):
    key = "07_agents"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        center = np.array([0, -0.4, 0])
        hub_c = Circle(radius=1.0, stroke_color=C.GOLD, stroke_width=4, fill_color=C.PANEL, fill_opacity=1)
        hub_c.move_to(center)
        hub_t = label("Slack hub", size=28, weight="SEMIBOLD").move_to(center)

        agents = [
            ("Sourcing Signal", "Weekly brief"),
            ("Category Brief", "Category view"),
            ("Supplier Risk", "Risk checks"),
            ("Deal Desk", "Deal support"),
            ("Spend Pulse", "Spend view"),
            ("Ghostbuster", "Waste checks"),
        ]
        angles = [90, 30, -30, -90, -150, 150]
        a, b = 4.7, 2.45
        bw, bh = 3.1, 1.1
        boxes, names, roles, lines = VGroup(), VGroup(), VGroup(), VGroup()
        for (name, role), deg in zip(agents, angles):
            th = np.deg2rad(deg)
            pos = center + np.array([a * np.cos(th), b * np.sin(th), 0])
            box = card(bw, bh).move_to(pos)
            nt = label(name, size=26, weight="SEMIBOLD")
            rt = label(role, size=21, color=C.MUTED)
            VGroup(nt, rt).arrange(DOWN, buff=0.12).move_to(box)
            d = (pos - center) / np.linalg.norm(pos - center)
            s = min((bw / 2) / max(abs(d[0]), 1e-9), (bh / 2) / max(abs(d[1]), 1e-9))
            ln = Line(center + d * 1.05, pos - d * (s + 0.08), stroke_color=C.MUTED, stroke_width=2.5)
            boxes.add(box), names.add(nt), roles.add(rt), lines.add(ln)

        self.beat(0)  # Six agents in one Slack hub.
        self.run(FadeIn(title, shift=RIGHT * 0.2), Create(hub_c), FadeIn(hub_t), run_time=1.0)
        self.run(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.12), run_time=0.9)
        self.run(LaggedStart(*[FadeIn(VGroup(bx, n), scale=0.95) for bx, n in zip(boxes, names)],
                             lag_ratio=0.1), run_time=0.8)
        self.beat(1)  # Each has one job: briefs, risk checks...
        self.run(LaggedStart(*[FadeIn(r) for r in roles], lag_ratio=0.15), run_time=0.9)
        self.run(LaggedStart(*[AnimationGroup(r.animate.set_color(C.INK), l.animate.set_stroke(C.GOLD))
                               for r, l in zip(roles, lines)], lag_ratio=0.6), run_time=3.8)
        self.finish()


class S09Ahead(BeatScene):
    key = "09_ahead"

    def make_card(self, head, items, stroke, dashed, head_color, x, w):
        h = 3.0
        fill = RoundedRectangle(width=w, height=h, corner_radius=C.CARD_RADIUS,
                                fill_color=C.PANEL, fill_opacity=1, stroke_width=0)
        outline = RoundedRectangle(width=w, height=h, corner_radius=C.CARD_RADIUS,
                                   stroke_color=stroke, stroke_width=3)
        if dashed:
            outline = DashedVMobject(outline, num_dashes=70, dashed_ratio=0.55)
        ht = Text(head, font=C.SERIF, font_size=44, color=head_color)
        rows = VGroup()
        for it in items:
            dot = Dot(radius=0.06, color=head_color)
            t = label(it, size=21)
            rows.add(VGroup(dot, t).arrange(RIGHT, buff=0.22))
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        content = VGroup(ht, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        grp = VGroup(fill, outline).move_to([x, -0.3, 0])
        content.move_to(grp).align_to(fill, LEFT).shift(RIGHT * 0.42)
        return grp, ht, rows

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        today, t_head, t_rows = self.make_card(
            "Today", ["Reacts to signals", "Finds issues as they arrive"], C.MUTED, True, C.MUTED, -3.85, 5.6)
        nxt, n_head, n_rows = self.make_card(
            "Next", ["Sees what is coming", "Flags risks and openings early"], C.TEAL, False, C.TEAL, 3.55, 6.6)
        arrow = Arrow(today.get_right() + RIGHT * 0.08, nxt.get_left() + LEFT * 0.08, buff=0,
                      stroke_color=C.INK, stroke_width=4, max_tip_length_to_length_ratio=0.3)
        arrow.get_tip().set_fill(C.INK)
        final = Text("Early action drives the business.", font=C.SERIF, font_size=46, color=C.GOLD)
        final.move_to([0, -2.85, 0])

        self.beat(0)  # Today: what happened.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.run(FadeIn(today), FadeIn(t_head), FadeIn(t_rows), run_time=1.2)
        self.beat(1)  # Next: what is coming.
        self.run(Create(arrow), run_time=0.8)
        self.run(FadeIn(nxt, shift=LEFT * 0.15), FadeIn(n_head, shift=LEFT * 0.15), run_time=1.0)
        self.beat(1, delay=2.4)  # The renewal, the risk, and the opportunity.
        self.run(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in n_rows], lag_ratio=0.5), run_time=1.6)
        self.beat(3)  # Early action drives the business.
        self.run(FadeIn(final, shift=UP * 0.12), run_time=1.2)
        self.finish()


class S05Speed(BeatScene):
    key = "05_speed"

    UNIT = 0.6  # scene units per week
    X0 = -2.1

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        recap_v = Text(C.usd(C.gap), font=C.SERIF, font_size=72, color=C.GOLD)
        recap_l = label("a year in margin, protected", size=26, color=C.MUTED)
        recap = VGroup(recap_v, recap_l).arrange(DOWN, buff=0.25).move_to([0, 0.1, 0])

        tag_n = label("Vendor Y", size=26, color=C.GOLD, weight="SEMIBOLD")
        tag_d = label("Data partner for a launch", size=24)
        tag_t = VGroup(tag_n, Dot(radius=0.045, color=C.MUTED), tag_d).arrange(RIGHT, buff=0.3)
        tag_b = card(tag_t.width + 0.7, 0.66, stroke=C.GOLD, width=2.5, radius=0.33)
        tag_b.move_to([-6.6 + tag_b.width / 2, 2.3, 0])
        tag_t.move_to(tag_b)

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

        self.beat(0)  # Savings are only half the story.
        self.run(FadeIn(recap, shift=UP * 0.1), run_time=0.9)
        self.beat(1)  # Speed is revenue.
        self.run(FadeOut(recap), FadeIn(title, shift=RIGHT * 0.2), run_time=0.9)
        self.beat(2)  # Vendor Y.
        self.run(FadeIn(tag_b), FadeIn(tag_t), run_time=0.8)
        self.run(Create(axis), FadeIn(ticks), FadeIn(tick_labels), FadeIn(weeks_lab), run_time=1.0)
        self.beat(3)  # Typical cycle: 12 weeks.
        self.run(FadeIn(l1), GrowFromEdge(b1, LEFT), run_time=1.6)
        self.beat(4)  # With the hub: 4 weeks.
        self.run(FadeIn(l2), GrowFromEdge(b2, LEFT), run_time=1.0)
        self.beat(5)  # The launch ships 8 weeks earlier.
        self.run(Create(gap_box), run_time=0.9)
        self.run(FadeIn(gap_lab, shift=UP * 0.1), run_time=0.7)
        self.beat(6)  # 8 more weeks of revenue.
        self.run(gap_box.animate.set_fill(C.TEAL, opacity=0.35), FadeIn(rev_lab), run_time=1.2)
        self.finish()


class S06Corner(BeatScene):
    key = "06_corner"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        tag_n = label("Vendor Z", size=26, color=C.GOLD, weight="SEMIBOLD")
        tag_d = label(f"Supports {C.VENDOR_Z_ROLE}", size=24)
        tag_t = VGroup(tag_n, Dot(radius=0.045, color=C.MUTED), tag_d).arrange(RIGHT, buff=0.3)
        tag_b = card(tag_t.width + 0.7, 0.66, stroke=C.GOLD, width=2.5, radius=0.33)
        tag_b.move_to([-6.6 + tag_b.width / 2, 2.3, 0])
        tag_t.move_to(tag_b)

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

        self.beat(0)  # Look around the corner.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.8)
        self.run(Create(line), FadeIn(d_today), FadeIn(t_today), FadeIn(d_peak), FadeIn(t_peak), run_time=1.1)
        self.beat(1)  # Vendor Z.
        self.run(FadeIn(tag_b), FadeIn(tag_t), run_time=0.8)
        for i in range(3):  # Three signals, one per sentence.
            self.beat(2 + i)
            self.run(FadeIn(sigs[i], shift=DOWN * 0.15), run_time=0.7)
        self.beat(5)  # Each signal alone is noise.
        self.run(sigs.animate.set_opacity(0.45), run_time=0.8)
        self.beat(6)  # Together, they say act now.
        self.run(*[sg.animate.move_to(act).scale(0.4).set_opacity(0) for sg in sigs], run_time=0.8)
        self.remove(sigs)
        self.run(FadeIn(act, scale=1.2), run_time=0.5)
        self.beat(7)  # Lock in capacity and a backup.
        self.run(Create(span), FadeIn(span_lab), run_time=1.4)
        self.run(FadeIn(d_sec, scale=0.5), FadeIn(secured, shift=UP * 0.1), run_time=0.9)
        self.beat(8)  # Peak revenue is protected.
        self.run(FadeIn(final, shift=UP * 0.12), run_time=1.0)
        self.finish()


class S08Levers(BeatScene):
    key = "08_levers"

    def construct(self):
        title = self.title(C.SCENE_TITLES[self.key])
        levers = [
            ("Protect margin", C.usd(C.gap), "a year, Vendor X", C.GOLD),
            ("Speed growth", f"{C.WEEKS_SAVED} weeks", "sooner to launch, Vendor Y", C.TEAL),
            ("Protect revenue", f"{C.DAYS_TO_PEAK} days", "of warning, Vendor Z", C.BLUE),
        ]
        cards, contents = VGroup(), []
        for (name, value, sub, color), x in zip(levers, [-4.55, 0, 4.55]):
            c = card(4.35, 2.9).move_to([x, -0.35, 0])
            n = label(name, size=28, weight="SEMIBOLD")
            v = Text(value, font=C.SERIF, font_size=54, color=color)
            s = label(sub, size=21, color=C.MUTED)
            VGroup(n, v, s).arrange(DOWN, buff=0.28).move_to(c)
            cards.add(c)
            contents.append((VGroup(n, v, s), color))

        self.beat(0)  # Three levers, one hub.
        self.run(FadeIn(title, shift=RIGHT * 0.2), run_time=0.8)
        self.run(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cards], lag_ratio=0.2), run_time=0.7)
        for i, (grp, color) in enumerate(contents):
            self.beat(1 + i)
            self.run(FadeIn(grp, shift=UP * 0.1), cards[i].animate.set_stroke(color, width=3.5), run_time=0.9)
        self.finish()
