from manim import *
config.frame_width = 9; config.frame_height = 16
config.pixel_width = 1080; config.pixel_height = 1920; config.frame_rate = 30
config.background_color = "#0b1020"
class T(Scene):
    def construct(self):
        c = Circle(radius=2, color="#4cc9f0", stroke_width=10)
        sq = Square(3, color="#f72585", stroke_width=10)
        self.play(Create(c), run_time=1)
        self.play(Transform(c, sq), run_time=1)
        self.play(Rotate(c, PI/2), run_time=1)
