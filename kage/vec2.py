import numpy as np

class Vec2(np.ndarray):
    def __new__(cls, x, y):
        return super(Vec2, cls).__new__(
            cls, shape=(2,), dtype=np.float64, 
            buffer=np.array([x,y], dtype=np.float64)
        )

    def __str__(self) -> str:
        return f"{self.x},{self.y}"

    x = property(
        lambda self : self.data.__getitem__(0),
        lambda self, new_x : self.data.__setitem__(0, new_x)
    )

    y = property(
        lambda self : self.data.__getitem__(1),
        lambda self, new_y : self.data.__setitem__(1, new_y)
    )

    def cross_product(self, another) -> 'Vec2':
        return self.x * another.y - another.x * self.y


"""
Calculates a new vector with the same angle and a new magnitude.
"""
def normalize(vec: Vec2, magnitude = 1) -> Vec2:
    norm = np.sqrt(vec.x * vec.x + vec.y * vec.y);
    assert norm != 0
    return vec * magnitude / norm


"""
Returns true if two line segments (vec11, vec12), (vec21, vec22) intersect.
"""
def is_cross(vec11: Vec2, vec12: Vec2, vec21: Vec2, vec22: Vec2) -> bool:
    cross_1112_2122 = (vec12 - vec11).cross_product(vec21 - vec22)
    if np.isnan(cross_1112_2122):
        return True # for backward compatibility...
    if cross_1112_2122 == 0:
        # parallel
        return False # XXX should check if segments overlap?
    cross_1112_1121 = (vec11 - vec12).cross_product(vec11 - vec21)
    cross_1112_1122 = (vec11 - vec12).cross_product(vec11 - vec22)
    cross_2122_2111 = (vec21 - vec22).cross_product(vec21 - vec11)
    cross_2122_2112 = (vec21 - vec22).cross_product(vec21 - vec12)
    return cross_1112_1121 * cross_1112_1122 <= 0 and cross_2122_2111 * cross_2122_2112 <= 0 # XXX round


"""
Returns true if the line segment (vec_1, vec_2) intersect with the bounding
box formed by vec_b1, vec_b2.
"""
def is_cross_box(vec_1: Vec2, vec_2: Vec2, vec_b1: Vec2, vec_b2: Vec2) -> bool:
    if is_cross(vec_1, vec_2, vec_b1, Vec2(vec_b2.x, vec_b1.y)):
        return True
    elif is_cross(vec_1, vec_2, Vec2(vec_b2.x, vec_b1.y), vec_b2):
        return True
    elif is_cross(vec_1, vec_2, Vec2(vec_b1.x, vec_b2.y), vec_b2):
        return True
    elif is_cross(vec_1, vec_2, vec_b1, Vec2(vec_b1.x, vec_b2.y)):
        return True
    else:
        return False
