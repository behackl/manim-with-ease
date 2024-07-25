from manim import *
# changed with v0.18.0: we no longer need the colour module
# and use our own ManimColor class instead.
from manim import ManimColor as Color
import random


class SweepingLine(Scene):
    def construct(self):
        growing_circle = Circle(radius=0.001)

        moving_line = Line([-7, -5, 0], [-6, 5, 0])
        moving_line.normal_vector = moving_line.copy().rotate(90*DEGREES).get_vector()

        def opacity_updater(obj):
            if (  # check whether dot is inside circle
                sum((growing_circle.points[0] - growing_circle.get_center())**2)
                >= sum((obj.get_center() - growing_circle.get_center())**2)
                #  round(  # more general winding number approach!
                #      get_winding_number(growing_circle.get_anchors() - obj.get_center())
                #  ) > 0
            ):
                obj.set_fill(BLUE, opacity=1)
                obj.clear_updaters()  # removes opacity_updater, ...
                obj.add_updater(color_updater)  # and attaches the color_updater function
                self.add_sound("assets/click.wav")

        def color_updater(obj):
            if (  # check whether point is *right* of the line
                np.dot(obj.get_center(), moving_line.normal_vector)
                < np.dot(moving_line.get_start(), moving_line.normal_vector)
            ):
                if obj.color != Color(BLUE):
                    obj.set_color(BLUE)
                    self.add_sound("assets/click.wav")
            else:  # otherwise point is *left* of the line
                if obj.color != Color(YELLOW):
                    obj.set_color(YELLOW)
                    self.add_sound("assets/click.wav")

        self.add(growing_circle)

        for _ in range(30):
            p = Dot(fill_opacity=0.6)
            p.move_to([random.uniform(-6, 6), random.uniform(-4, 4), 0])
            p.add_updater(opacity_updater)
            self.add(p)

        self.play(
            growing_circle.animate.scale_to_fit_width(1.5*config.frame_width),
            run_time=5
        )
        self.play(Create(moving_line))
        self.play(moving_line.animate.shift(14*RIGHT), run_time=5)
        self.play(moving_line.animate.shift(14*LEFT), run_time=5)




class DeCasteljau(Scene):
    def construct(self):
        self.camera.background_color = '#455D3E'
        a1 = np.array([-3, -2, 0])
        h1 = np.array([-3, 0, 0])
        h2 = np.array([3, 0, 0])
        a2 = np.array([3, 2, 0])

        t = ValueTracker(0.001)
        self.add(t)

        d01 = Cross(scale_factor=0.2).move_to(a1)
        d02 = Dot(color=ORANGE).move_to(h1)
        d03 = Dot(color=ORANGE).move_to(h2)
        d04 = Cross(scale_factor=0.2).move_to(a2)

        d11 = Dot(color=GRAY).add_updater(
            lambda mob: mob.move_to(
                (1- t.get_value()) * d01.get_center() + t.get_value() * d02.get_center()
            )
        )
        d12 = Dot(color=GRAY).add_updater(
            lambda mob: mob.move_to((1- t.get_value()) * d02.get_center() + t.get_value() * d03.get_center())
        )
        d13 = Dot(color=GRAY).add_updater(
            lambda mob: mob.move_to((1- t.get_value()) * d03.get_center() + t.get_value() * d04.get_center())
        )

        d21 = Dot(color=GRAY).add_updater(
            lambda mob: mob.move_to((1- t.get_value()) * d11.get_center() + t.get_value() * d12.get_center())
        )
        d22 = Dot(color=GRAY).add_updater(
            lambda mob: mob.move_to((1- t.get_value()) * d12.get_center() + t.get_value() * d13.get_center())
        )

        d31 = Dot(color=RED).add_updater(
            lambda mob: mob.move_to((1- t.get_value()) * d21.get_center() + t.get_value() * d22.get_center())
        )

        static_lines = [
            Line(d01.get_center(), d02, color=ORANGE),
            Line(d02, d03),
            Line(d03, d04.get_center(), color=ORANGE)
        ]

        dynamic_lines = [
            always_redraw(lambda a=a, b=b: Line(a.get_center(), b.get_center(), color=LIGHT_GRAY))
            for a, b in [
                (d11, d12), (d12, d13), (d21, d22)
            ]
        ]
        self.add(*dynamic_lines, *static_lines, d01, d02, d03, d04, d11, d12, d13, d21, d22, d31)
        self.add(
            TracedPath(lambda: d31.get_center(), stroke_color=RED)
        )

        self.wait(0.5)
        self.play(t.animate(run_time=5).set_value(0.999))
        self.wait(0.5)
        self.play(FadeOut(VGroup(
            *dynamic_lines, *static_lines, d02, d03, d11, d12, d13, d21, d22
        )))
        self.wait()


