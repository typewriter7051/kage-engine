from .vec2      import Vec2, is_cross, is_cross_box

from argparse   import Namespace
import numpy as np

"""
a1 defines the stroke type.
a2 a3 define the start and end serifs.
vec_1 vec_2 are the start and endpoints of the stroke.
vec_3 vec_4 are optionally used as Bezier points if the stroke is curved.
"""
class Stroke:
    def __init__(self, data: list) -> None:
        self.a1_100 = int(data[0])
        self.a2_100 = int(data[1])
        self.a3_100 = int(data[2])
        self.vec_1 = Vec2(data[3], data[4])
        self.vec_2 = Vec2(data[5], data[6])
        self.vec_3 = Vec2(data[7], data[8])
        self.vec_4 = Vec2(data[9], data[10])
        self.a1_opt = np.floor(self.a1_100 / 100)
        self.a1_100 %= 100
        self.a2_opt = np.floor(self.a2_100 / 100)
        self.a2_100 %= 100
        self.a2_opt_1 = self.a2_opt % 10
        self.a2_opt_2 = np.floor(self.a2_opt / 10) % 10
        self.a2_opt_3 = np.floor(self.a2_opt / 100)
        self.a3_opt = np.floor(self.a3_100 / 100)
        self.a3_100 %= 100
        self.a3_opt_1 = self.a3_opt % 10
        self.a3_opt_2 = np.floor(self.a3_opt / 10)
        
    def get_control_segments(self):
        res = []
        a1 = self.a1_100 if self.a1_opt == 0 else 1 # XXX: ???
        if a1 in [0,8,9]:
            pass
        if a1 in [6,7]:
            res.insert(0, [self.vec_3, self.vec_4])
        if a1 in [2,12,3,4] or a1 in [6,7]:
            res.insert(0, [self.vec_2, self.vec_3])
        if a1 not in [0,8,9] or a1 in [6,7,2,12,3,4]:
            res.insert(0, [self.vec_1, self.vec_2])
        return res
    
    def is_cross(self, vec_b1: Vec2, vec_b2: Vec2):
        return any(is_cross(vec2s[0], vec2s[1], vec_b1, vec_b2) for vec2s in self.get_control_segments())

    def is_cross_box(self, vec_b1: Vec2, vec_b2: Vec2):
        return any(is_cross_box(vec2s[0], vec2s[1], vec_b1, vec_b2) for vec2s in self.get_control_segments())

    def stretch(self, sx, sx2, sy, sy2, bminX, bmaxX, bminY, bmaxY):
        self.vec_1 = Vec2(
            self.__stretch(sx, sx2, self.vec_1.x, bminX, bmaxX),
            self.__stretch(sy, sy2, self.vec_1.y, bminY, bmaxY),
        )
        self.vec_2 = Vec2(
            self.__stretch(sx, sx2, self.vec_2.x, bminX, bmaxX),
            self.__stretch(sy, sy2, self.vec_2.y, bminY, bmaxY),
        )
        if not (self.a1_100 == 99 and self.a1_opt == 0): # always true
            self.vec_3 = Vec2(
                self.__stretch(sx, sx2, self.vec_3.x, bminX, bmaxX),
                self.__stretch(sy, sy2, self.vec_3.y, bminY, bmaxY),
            )
            self.vec_4 = Vec2(
                self.__stretch(sx, sx2, self.vec_4.x, bminX, bmaxX),
                self.__stretch(sy, sy2, self.vec_4.y, bminY, bmaxY),
            )

    def get_box(self):
        minX = np.inf
        minY = np.inf
        maxX = -np.inf
        maxY = -np.inf
        a1 = self.a1_100 if self.a1_opt == 0 else 6 # XXX ?????
        if a1 not in [2,3,4,1,99,0]:
            minX = np.nanmin([minX, self.vec_4.x])
            maxX = np.nanmax([maxX, self.vec_4.x])
            minY = np.nanmin([minY, self.vec_4.y])
            maxY = np.nanmax([maxY, self.vec_4.y])
        if a1 in [2,3,4] or a1 not in [2,3,4,1,99,0]:
            minX = np.nanmin([minX, self.vec_3.x])
            maxX = np.nanmax([maxX, self.vec_3.x])
            minY = np.nanmin([minY, self.vec_3.y])
            maxY = np.nanmax([maxY, self.vec_3.y])
        if a1 in [1,99] or a1 in [2,3,4] or a1 not in [2,3,4,1,99,0]:
            minX = np.nanmin([minX, self.vec_1.x, self.vec_2.x])
            maxX = np.nanmax([maxX, self.vec_1.x, self.vec_2.x])
            minY = np.nanmin([minY, self.vec_1.y, self.vec_2.y])
            maxY = np.nanmax([maxY, self.vec_1.y, self.vec_2.y])
        if a1 == 0:
            pass
        
        return Namespace(**{'minX': minX, 'maxX': maxX, 'minY': minY, 'maxY': maxY})

    def __repr__(self) -> str:
        return f'{self.a1_100}:{self.a2_100}:{self.a3_100}:{self.vec_1.x}:{self.vec_1.y}:{self.vec_2.x}:{self.vec_2.y}:{self.vec_3.x}:{self.vec_3.y}:{self.vec_4.x}:{self.vec_4.y}'

    def _get_data(self) -> list:
        return [
            self.a1_100,
            self.a2_100,
            self.a3_100,
            self.vec_1.x,
            self.vec_1.y,
            self.vec_2.x,
            self.vec_2.y,
            self.vec_3.x,
            self.vec_3.y,
            self.vec_4.x,
            self.vec_4.y,
        ]

    def __stretch(self, dp, sp, p, min_, max_):
        if (p < sp + 100):
            p1 = min_
            p3 = min_
            p2 = sp + 100
            p4 = dp + 100
        else:
            p1 = sp + 100
            p3 = dp + 100
            p2 = max_
            p4 = max_
        return np.floor(((p - p1) / (p2 - p1)) * (p4 - p3) + p3)

