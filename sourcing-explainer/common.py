"""Shared base scene: background, title, badge, beat clock, layout check."""

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, UR, Create, FadeIn, RoundedRectangle, Scene,
    Text, VGroup, config as mconfig,
)

import config as C


def label(text, size=26, color=C.INK, weight="NORMAL", font=C.SANS):
    return Text(text, font=font, font_size=size, color=color, weight=weight)


def card(w, h, stroke=C.LINE, fill=C.PANEL, width=2.5, radius=C.CARD_RADIUS):
    return RoundedRectangle(
        width=w, height=h, corner_radius=radius,
        stroke_color=stroke, stroke_width=width,
        fill_color=fill, fill_opacity=1,
    )


def chip(text, color=C.INK, stroke=C.LINE, size=22, pad_x=0.32, h=0.56):
    t = label(text, size=size, color=color).set_z_index(1)
    box = card(t.width + 2 * pad_x, h, stroke=stroke, radius=h / 2, width=2)
    t.move_to(box)
    return VGroup(box, t)


class BeatScene(Scene):
    """A scene whose animations are pinned to narration sentence starts."""

    key = None

    def setup(self):
        self.camera.background_color = C.BG
        self.clock = 0.0
        self.beats = C.beats(self.key)
        self.total = C.scene_duration(self.key)
        badge = label(C.BADGE_TEXT, size=15, color=C.MUTED)
        badge.to_corner(UR, buff=0.32)
        self.badge = badge
        self.add(badge)

    def at(self, t):
        """Wait until time t (seconds from scene start)."""
        assert t + 1e-6 >= self.clock, f"{self.key}: beat {t:.2f}s already passed (clock {self.clock:.2f}s)"
        # Snap to the real renderer time so frame rounding never drifts.
        gap = t - self.time
        if gap > 0.5 / self.camera.frame_rate:
            self.wait(gap + 0.5 / self.camera.frame_rate)
        self.clock = max(self.clock, t)

    def run(self, *anims, run_time=1.0, **kw):
        self.play(*anims, run_time=run_time, **kw)
        self.clock += run_time

    def beat(self, i, delay=0.0):
        self.at(self.beats[i] + delay)

    def title(self, text):
        t = Text(text, font=C.SERIF, font_size=38, color=C.INK)
        t.to_corner(UL, buff=0.5)
        return t

    def finish(self):
        self.check_layout()
        self.at(self.total)

    def check_layout(self):
        """Fail the render if any text leaves the frame or overlaps other text."""
        fw, fh = mconfig.frame_width / 2, mconfig.frame_height / 2
        texts = [m for m in self.mobjects_family() if isinstance(m, Text)]
        problems = []
        for t in texts:
            if (t.get_left()[0] < -fw + 0.1 or t.get_right()[0] > fw - 0.1
                    or t.get_bottom()[1] < -fh + 0.1 or t.get_top()[1] > fh - 0.1):
                problems.append(f"off screen: {t.text!r}")
        for i, a in enumerate(texts):
            for b in texts[i + 1:]:
                if (a.get_left()[0] < b.get_right()[0] and b.get_left()[0] < a.get_right()[0]
                        and a.get_bottom()[1] < b.get_top()[1] and b.get_bottom()[1] < a.get_top()[1]):
                    problems.append(f"overlap: {a.text!r} / {b.text!r}")
        assert not problems, f"{self.key} layout: " + "; ".join(problems)

    def mobjects_family(self):
        seen = []
        for m in self.mobjects:
            for f in m.get_family():
                if f not in seen:
                    seen.append(f)
        return seen
