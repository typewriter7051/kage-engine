from ...vec2        import Vec2, normalize
from ..serif_font   import SerifFont
from ...stroke      import Stroke
from ..font         import Font
from ..serif_stroke import SerifStroke

from argparse       import Namespace
from math           import floor
import numpy as np
import svgwrite

class Serif(SerifFont):
    def __init__(self, size = 2) -> None:
        super().__init__(size)

    def draw_strokes(self, canvas: svgwrite.Drawing):
        from . serif_stroke_drawer import LegacySerifStrokeDrawer as SerifStrokeDrawer
        stroke_drawer = SerifStrokeDrawer(self, canvas)
        for serif_stroke in self.serif_strokes:
            stroke = serif_stroke.stroke
            if stroke.a1_100 == 0: # TODO: Transforms
                pass
            elif stroke.a1_100 == 1:
                if stroke.a3_100 == 4:
                    m = Vec2(0, self.kMage) if all(stroke.vec_1 == stroke.vec_2) else normalize(stroke.vec_1 - stroke.vec_2, self.kMage)
                    t1 = stroke.vec_2 + m
                    stroke_drawer.draw_line(stroke.vec_1, t1, stroke.a2_100 + stroke.a2_opt * 100, 1, serif_stroke.tate_adjustment, 0, 0)
                    stroke_drawer.draw_curve(t1, stroke.vec_2,
                        Vec2(stroke.vec_2.x - self.kMage * (((self.kAdjustTateStep + 4) - serif_stroke.tate_adjustment) / (self.kAdjustTateStep + 4)), stroke.vec_2.y),
                        1, 14,
                        serif_stroke.tate_adjustment % 10,
                        serif_stroke.hane_adjustment,
                        np.floor(serif_stroke.tate_adjustment / 10),
                        stroke.a3_opt_2
                    )
                else:
                    stroke_drawer.draw_line(stroke.vec_1, stroke.vec_2, stroke.a2_100 + stroke.a2_opt * 100, stroke.a3_100, serif_stroke.tate_adjustment, serif_stroke.uroko_adjustment, serif_stroke.kakato_adjustment)
            elif stroke.a1_100 == 2:
                if stroke.a3_100 == 4:
                    vec_d = Vec2(0, -self.kMage) if stroke.vec_2.x == stroke.vec_3.x else Vec2(-self.kMage, 0) if stroke.vec_2.y == stroke.vec_3.y else normalize(stroke.vec_2 - stroke.vec_3, self.kMage)
                    vec_t1 = stroke.vec_3 + vec_d
                    stroke_drawer.draw_curve(stroke.vec_1, stroke.vec_2, vec_t1, stroke.a2_100 + serif_stroke.kirikuchi_adjustment * 100, 0, stroke.a2_opt_2, 0, stroke.a2_opt_3, 0)
                    stroke_drawer.draw_curve(vec_t1, stroke.vec_3, stroke.vec_3 - Vec2(self.kMage, 0), 2, 14, stroke.a2_opt_2, serif_stroke.hane_adjustment, 0, stroke.a3_opt_2)
                else:
                    stroke_drawer.draw_curve(stroke.vec_1, stroke.vec_2, stroke.vec_3, stroke.a2_100 + serif_stroke.kirikuchi_adjustment * 100, 15 if (stroke.a3_100 == 5 and stroke.a3_opt == 0) else stroke.a3_100,
					stroke.a2_opt_2, stroke.a3_opt_1, stroke.a2_opt_3, stroke.a3_opt_2)
            elif stroke.a1_100 == 3:
                vec_d1 = Vec2(0, self.kMage) if all(stroke.vec_1 == stroke.vec_2) else normalize(stroke.vec_1 - stroke.vec_2, self.kMage)
                vec_d2 = Vec2(0, -self.kMage) if all(stroke.vec_2 == stroke.vec_3) else normalize(stroke.vec_3 - stroke.vec_2, self.kMage)
                vec_t1 = stroke.vec_2 + vec_d1
                vec_t2 = stroke.vec_2 + vec_d2
                stroke_drawer.draw_line(stroke.vec_1, vec_t1, stroke.a2_100 + stroke.a2_opt * 100, 1, serif_stroke.tate_adjustment, 0, 0)
                stroke_drawer.draw_curve(vec_t1, stroke.vec_2, vec_t2, 1, 1, 0, 0, serif_stroke.tate_adjustment, serif_stroke.mage_adjustment)

                if (not(stroke.a3_100 == 5 and stroke.a3_opt_1 == 0 and not ((stroke.vec_2.x < stroke.vec_3.x and stroke.vec_3.x - vec_t2.x > 0) or (stroke.vec_2.x > stroke.vec_3.x and vec_t2.x - stroke.vec_3.x > 0)))):
                    opt2 = 0 if (stroke.a3_100 == 5 and stroke.a3_opt_1 == 0) else stroke.a3_opt_1 + serif_stroke.mage_adjustment * 10
                    stroke_drawer.draw_line(vec_t2, stroke.vec_3, 6, stroke.a3_100, serif_stroke.mage_adjustment, opt2, opt2)
            elif stroke.a1_100 == 12:
                stroke_drawer.draw_curve(stroke.vec_1, stroke.vec_2, stroke.vec_3,
                    stroke.a2_100 + stroke.a2_opt_1 * 100, 1, stroke.a2_opt_2, 0, stroke.a2_opt_3, 0)
                stroke_drawer.draw_line(stroke.vec_3, stroke.vec_4, 6, stroke.a3_100, 0, stroke.a3_opt, stroke.a3_opt)
            elif stroke.a1_100 == 4:
                rate = np.hypot(*(stroke.vec_3 - stroke.vec_2)) / 120 * 6
                if (rate > 6):
                    rate = 6
                vec_d1 = Vec2(0, self.kMage * rate) if all(stroke.vec_1 == stroke.vec_2) else normalize(stroke.vec_1 - stroke.vec_2, self.kMage * rate)
                vec_t1 = stroke.vec_2 + vec_d1
                vec_d2 = Vec2(0, -self.kMage * rate) if all(stroke.vec_2 == stroke.vec_3) else normalize(stroke.vec_3 - stroke.vec_2, self.kMage * rate)
                vec_t2 = stroke.vec_2 + vec_d2

                stroke_drawer.draw_line(stroke.vec_1, vec_t1, stroke.a2_100 + stroke.a2_opt * 100, 1, stroke.a2_opt_2 + stroke.a2_opt_3 * 10, 0, 0)
                stroke_drawer.draw_curve(vec_t1, stroke.vec_2, vec_t2, 1, 1, 0, 0, 0, 0)

                if (not(stroke.a3_100 == 5 and stroke.a3_opt == 0 and stroke.vec_3.x -  vec_t2.x <= 0)):
                    stroke_drawer.draw_line(vec_t2, stroke.vec_3, 6, stroke.a3_100, 0, stroke.a3_opt, stroke.a3_opt)
            elif stroke.a1_100 == 6:
                if stroke.a3_100 == 4:
                    vec_d = Vec2(0, -self.kMage) if stroke.vec_3.x == stroke.vec_4.x else Vec2(-self.kMage, 0) if stroke.vec_3.y == stroke.vec_4.y else normalize(stroke.vec_3 - stroke.vec_4, self.kMage)
                    vec_t1 = stroke.vec_4 + vec_d
                    stroke_drawer.draw_bezier(stroke.vec_1, stroke.vec_2, stroke.vec_3, vec_t1, stroke.a2_100 + stroke.a2_opt * 100, 0, stroke.a2_opt_2, 0, stroke.a2_opt_3, 0)
                    stroke_drawer.draw_curve(vec_t1, stroke.vec_4, stroke.vec_4 - Vec2(self.kMage, 0), 1, 14, 0, serif_stroke.hane_adjustment, 0, stroke.a3_opt_2)
                else:
                    stroke_drawer.draw_bezier(stroke.vec_1, stroke.vec_2, stroke.vec_3, stroke.vec_4, stroke.a2_100 + stroke.a2_opt * 100, 15 if stroke.a3_100 == 5 and stroke.a3_opt == 0 else stroke.a3_100, stroke.a2_opt_2, stroke.a3_opt_1, stroke.a2_opt_3, stroke.a3_opt_2)
            elif stroke.a1_100 == 7:
                stroke_drawer.draw_line(stroke.vec_1, stroke.vec_2, stroke.a2_100 + stroke.a2_opt * 100, 1, serif_stroke.tate_adjustment, 0, 0)
                stroke_drawer.draw_curve(stroke.vec_2, stroke.vec_3, stroke.vec_4, 1, stroke.a3_100, serif_stroke.tate_adjustment % 10, stroke.a3_opt_1, np.floor(serif_stroke.tate_adjustment / 10), stroke.a3_opt_2)
            elif stroke.a1_100 == 9:
                # may not be exist ... no need
                pass

