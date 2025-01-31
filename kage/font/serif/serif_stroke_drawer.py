from ..serif        import Serif
from ...stroke_info import StrokeType, SerifType
from ...util        import generate_flatten_curve
from ...vec2        import Vec2, normalize
import numpy as np
import svgwrite
import svgwrite.path

class LegacySerifStrokeDrawer:
    def __init__(self, font: Serif, canvas: svgwrite.Drawing) -> None:
        self.font = font
        self.canvas = canvas
        
    def draw_bezier(self, vec_1: Vec2, vec_s1: Vec2, vec_s2: Vec2, vec_2: Vec2,
                    a2: int, a3: int, opt1, hane_adjustment, opt3, opt4):
        self.__draw_curve_universal(
            vec_1, vec_s1, vec_s2, vec_2,
            a2, a3,
            opt1,
            hane_adjustment,
            opt3,
            opt4
        )

    def draw_curve(self, vec_1: Vec2, vec_s: Vec2, vec_2: Vec2,
                   a2: int, a3: int, opt1, hane_adjustment, opt3, opt4):
        self.__draw_curve_universal(
            vec_1, vec_s, vec_s, vec_2,
            a2, a3,
            opt1,
            hane_adjustment,
            opt3,
            opt4
        )
    
    def draw_line(self, vec_1: Vec2, vec_2: Vec2,
                  a2: int, a3: int, opt1, uroko_adjustment: int, kakato_adjustment: int):
        kMinWidthT = self.font.kMinWidthT - opt1 / 2

        if (vec_1.x == vec_2.x or vec_1.y != vec_2.y and
            (vec_1.x > vec_2.x or np.abs(vec_2.y - vec_1.y) >= np.abs(vec_2.x - vec_1.x) or
             a2 == 6 or a3 == 6)):
            # 縦, 竖, vertical storke: use y-axis
            # 角度が深い / 鈎（かぎ）の横

            cosrad, sinrad = Vec2(0, 1) if (vec_1.x == vec_2.x) else normalize(vec_2 - vec_1)

            rotation_matrix = np.array([
                [ sinrad, cosrad],
                [-cosrad, sinrad]
            ])

            poly0 = [Vec2(0, 0)] * 4

            # head
            if a2 == SerifType.free:
                poly0[0] = rotation_matrix @ Vec2(kMinWidthT, self.font.kMinWidthY / 2)
                poly0[3] = rotation_matrix @ Vec2(-kMinWidthT, -self.font.kMinWidthY / 2)
            # No idea which serif types these are they don't show up in the dump file.
            elif a2 in [1,6]:
                poly0[0] = rotation_matrix @ Vec2(kMinWidthT, 0)
                poly0[3] = rotation_matrix @ Vec2(-kMinWidthT, 0)
            elif a2 == SerifType.top_left_corner: # 箱型左上角
                poly0[0] = rotation_matrix @ Vec2(kMinWidthT, -self.font.kMinWidthY)
                poly0[3] = rotation_matrix @ Vec2(-kMinWidthT, -self.font.kMinWidthY - kMinWidthT)
            elif a2 == SerifType.top_right_corner: # 箱型右上角
                v = -1 if vec_1.x > vec_2.x else 1
                if vec_1.x == vec_2.x:
                    poly0[0] = Vec2(+ kMinWidthT, 0)
                    poly0[3] = Vec2(- kMinWidthT, 0)
                else:
                    poly0[0] = Vec2(+ (kMinWidthT + v) / sinrad, +1)
                    poly0[3] = Vec2(- kMinWidthT / sinrad, 0)
            elif a2 == 32: # ?
                if vec_1.x == vec_2.x:
                    poly0[0] = Vec2(+ kMinWidthT, - self.font.kMinWidthY)
                    poly0[3] = Vec2(- kMinWidthT, - self.font.kMinWidthY)
                else:
                    poly0[0] = Vec2(+ kMinWidthT / sinrad, 0)
                    poly0[3] = Vec2(- kMinWidthT / sinrad, 0)

            # head dots translate with vec_1
            poly0[0] += vec_1
            poly0[3] += vec_1

            # tail
            if a3 == SerifType.free:
                if a2 == 6:
                    poly0[1] = rotation_matrix @ Vec2(kMinWidthT, 0)
                    poly0[2] = rotation_matrix @ Vec2(-kMinWidthT, 0)
                else:
                    poly0[1] = rotation_matrix @ Vec2(kMinWidthT, -kMinWidthT / 2)
                    poly0[2] = rotation_matrix @ Vec2(-kMinWidthT, kMinWidthT / 2)
            elif a3 in [1,5]:
                if a3 == 5 and vec_1.x == vec_2.x:
                    pass
                else:
                    poly0[1] = rotation_matrix @ Vec2(kMinWidthT, 0)
                    poly0[2] = rotation_matrix @ Vec2(-kMinWidthT, 0)
            elif a3 == 13:
                poly0[1] = rotation_matrix @ Vec2(kMinWidthT, self.font.kAdjustKakatoL[kakato_adjustment])
                poly0[2] = rotation_matrix @ Vec2(-kMinWidthT, self.font.kAdjustKakatoL[kakato_adjustment] + kMinWidthT)
            elif a3 == 23:
                poly0[1] = rotation_matrix @ Vec2(kMinWidthT, self.font.kAdjustKakatoR[kakato_adjustment])
                poly0[2] = rotation_matrix @ Vec2(-kMinWidthT, self.font.kAdjustKakatoR[kakato_adjustment] + kMinWidthT)
            elif a3 in [SerifType.right_bottom_corner, SerifType.connect_v]:
                if vec_1.x == vec_2.x:
                    poly0[1] = Vec2(+ kMinWidthT, self.font.kMinWidthY)
                    poly0[2] = Vec2(- kMinWidthT, self.font.kMinWidthY)
                else:
                    poly0[1] = Vec2(+ kMinWidthT / sinrad, 0)
                    poly0[2] = Vec2(- kMinWidthT / sinrad, 0)
            
            # tail dots translate with vec_2
            poly0[1] += vec_2
            poly0[2] += vec_2

            # draw body
            poly0 = [str(i) for i in poly0]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(poly0)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black'
            )
            self.canvas.add(path)

            if a3 == SerifType.bottom_right_ht: # for T design
                polygon = [
                    Vec2(0, self.font.kMinWidthY),
                    Vec2(+kMinWidthT, -self.font.kMinWidthY * 3) if vec_1.x == vec_2.x
                        else Vec2(+kMinWidthT * 0.5, -self.font.kMinWidthY * 4),
                    Vec2(+kMinWidthT * 2, -self.font.kMinWidthY),
                    Vec2(+kMinWidthT * 2, +self.font.kMinWidthY)
                ]
                polygon = [str(i) for i in polygon]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_2})'
                )
                self.canvas.add(path)
            elif a3 == SerifType.bottom_left_corner:
                if kakato_adjustment == 4: # for new GTH box's left bottom corner
                    if vec_1.x == vec_2.x:
                        polygon = [
                            Vec2(-kMinWidthT, -self.font.kMinWidthY*3),
                            Vec2(-kMinWidthT * 2, 0),
                            Vec2(-self.font.kMinWidthY, +self.font.kMinWidthY * 5),
                            Vec2(+kMinWidthT, +self.font.kMinWidthY)
                        ]
                        polygon = [str(i) for i in polygon]
                        path = svgwrite.path.Path(
                            d = "M" + (" L".join(polygon)),
                            stroke = 'black',
                            stroke_width = 0,
                            fill = 'black',
                            transform = f'translate({vec_2})'
                        )
                        self.canvas.add(path)
                    else: # direction unrelated，向き関係なし
                        polygon = [
                            Vec2(0, -self.font.kMinWidthY*5),
                            Vec2(-kMinWidthT * 2, 0),
                            Vec2(-self.font.kMinWidthY, +self.font.kMinWidthY * 5),
                            Vec2(+kMinWidthT, +self.font.kMinWidthY),
                            Vec2(0,0)
                        ]
                        polygon = [str(i) for i in polygon]
                        path = svgwrite.path.Path(
                            d = "M" + (" L".join(polygon)),
                            stroke = 'black',
                            stroke_width = 0,
                            fill = 'black',
                            transform = f'translate({vec_2 + Vec2((vec_1.x - vec_2.x) / (vec_2.y - vec_1.y) * 3 if (vec_1.x > vec_2.x and vec_1.y != vec_2.y) else 0, 0)})'
                        )
                        self.canvas.add(path)

            if a2 in [22,27]: # box's right top corner
                # 四角右上鱗斜めでもまっすぐ向き
                # 箱形右上三角形装饰
                poly = [
					Vec2(-kMinWidthT, -self.font.kMinWidthY),
					Vec2(0, -self.font.kMinWidthY - self.font.kWidth),
					Vec2(+kMinWidthT + self.font.kWidth, +self.font.kMinWidthY)
                ]
                poly += [
                    Vec2(+kMinWidthT, +kMinWidthT),
                    Vec2(-kMinWidthT, 0)
                ] if vec_1.x == vec_2.x else [
                    Vec2(+kMinWidthT, +kMinWidthT - 1),
                    Vec2(0, +kMinWidthT + 2),
                    Vec2(0, 0),
                ] if a2 == SerifType.roofed_narrow else [
                    Vec2(+kMinWidthT, +kMinWidthT - 1),
                    Vec2(-kMinWidthT, +kMinWidthT + 4)
                ]
                poly = [str(i) for i in poly]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(poly)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_1})'
                )
                self.canvas.add(path)
            elif a2 == SerifType.free: # beginning of the stroke
                poly = [
					vec_1 + rotation_matrix @ Vec2(kMinWidthT, self.font.kMinWidthY * 0.5),
					vec_1 + rotation_matrix @ Vec2(kMinWidthT + kMinWidthT * 0.5, self.font.kMinWidthY * 0.5 + self.font.kMinWidthY),
					vec_1 + rotation_matrix @ Vec2(kMinWidthT - 2, self.font.kMinWidthY * 0.5 + self.font.kMinWidthY * 2 + 1),
				]
                if vec_1.x != vec_2.x:
                    poly[2] = Vec2(vec_1.x + (kMinWidthT - 2) * sinrad + (self.font.kMinWidthY * 0.5 + self.font.kMinWidthY * 2) * cosrad,
						vec_1.y + (kMinWidthT + 1) * -cosrad + (self.font.kMinWidthY * 0.5 + self.font.kMinWidthY * 2) * sinrad)
                
                poly = [str(i) for i in poly]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(poly)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black'
                )
                self.canvas.add(path)

            if (vec_1.x == vec_2.x and a3 == 1 or a2 == 6 and
                (a3 == SerifType.free or vec_1.x != vec_2.x and a3 == SerifType.hook_right)):
                # 鈎の横棒の最後の丸
                # no need only used at 1st=yoko
                poly = [
                    "M",
                    vec_2 + rotation_matrix @ Vec2(kMinWidthT, 0),
                    "Q",
                    Vec2(vec_2.x - cosrad * kMinWidthT * 0.9 + -sinrad * -kMinWidthT * 0.9, # typo? (- cosrad should be + cosrad)
					vec_2.y + sinrad * kMinWidthT * 0.9 + cosrad * -kMinWidthT * 0.9),
                    vec_2 + rotation_matrix @ Vec2(0, kMinWidthT),
                    "Q",
                    vec_2 + rotation_matrix @ Vec2(-kMinWidthT * 0.9, kMinWidthT * 0.9),
                    vec_2 + rotation_matrix @ Vec2(-kMinWidthT, 0)
                ]
                poly = [str(i) for i in poly]
                path = svgwrite.path.Path(
                    d = " ".join(poly),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black'
                )
                self.canvas.add(path)

                if (vec_1.x != vec_2.x and a2 == 6 and a3 == SerifType.hook_right):
                    # 鈎の横棒のハネ
                    hane_length = self.font.kWidth * 5
                    rv = 1 if vec_1.x < vec_2.x else -1
                    poly = [
                        Vec2(rv * (kMinWidthT - 1), 0),
                        Vec2(rv * (kMinWidthT + hane_length), 2),
                        Vec2(rv * (kMinWidthT + hane_length), 0),
                        Vec2(kMinWidthT - 1, -kMinWidthT), 
                    ]
                    poly = [str(vec_2 + rotation_matrix @ i) for i in poly]
                    path = svgwrite.path.Path(
                        d = "M" + " L".join(poly),
                        stroke = 'black',
                        stroke_width = 0,
                        fill = 'black'
                    )
                    self.canvas.add(path)

        elif (vec_1.y == vec_2.y and a2 == 6):
            # 横（よこ）, 横划, horizontal stroke: use x-axis
            # 鈎の横, 钩的横划, horizontal stroke of hook: get bold
            
            # body
            poly0 = [
                vec_1 + Vec2(0, -kMinWidthT),
                vec_2 + Vec2(0, -kMinWidthT),
                vec_2 + Vec2(0, +kMinWidthT),
                vec_1 + Vec2(0, +kMinWidthT),
            ]
            poly0 = [str(i) for i in poly0]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(poly0)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black'
            )
            self.canvas.add(path)

            if a3 in [1,0,5]:
                # 鍵の横棒に最後の丸
                degree = 180 if vec_1.x > vec_2.x else 0
                
                poly = [
                    "M",
                    Vec2(0, -kMinWidthT),
                    "Q", 
                    Vec2(+kMinWidthT * 0.9, -kMinWidthT * 0.9),
                    Vec2(+kMinWidthT, 0),
                    "Q", 
                    Vec2(+kMinWidthT * 0.9, +kMinWidthT * 0.9),
                    Vec2(0, +kMinWidthT),
                ]
                poly = [str(i) for i in poly]
                path = svgwrite.path.Path(
                    d = " ".join(poly),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_2}) rotate({degree},0,0)'
                )
                self.canvas.add(path)
                
                if a3 == SerifType.hook_right:
                    # 鈎の横棒のハネ
                    hane_length = self.font.kWidth * (4 * (1 - opt1 / self.font.kAdjustMageStep) + 1)
                    rv = 1 if vec_1.x < vec_2.x else -1
                    poly = [
                        Vec2(0, rv * -kMinWidthT),
						Vec2(2, rv * (-kMinWidthT - hane_length)),
						Vec2(0, rv * (-kMinWidthT - hane_length)),
						Vec2(-kMinWidthT, rv * -kMinWidthT)
                    ]
                    poly = [str(i) for i in poly]
                    path = svgwrite.path.Path(
                        d = "M" + " L".join(poly),
                        stroke = 'black',
                        stroke_width = 0,
                        fill = 'black',
                        transform = f'translate({vec_2}) rotate({degree},0,0)'
                    )
                    self.canvas.add(path)

        else:
            # for others, use x-axis
            # 浅い角度
            cosrad, sinrad = Vec2(1, 0) if vec_1.y == vec_2.y else normalize(vec_2 - vec_1)

            rotation_matrix = np.array([
                [cosrad, -sinrad],
                [sinrad,  cosrad]
            ])

            # body
            poly = [
                vec_1 + rotation_matrix @ Vec2(0, -self.font.kMinWidthY),
                vec_2 + rotation_matrix @ Vec2(0, -self.font.kMinWidthY),
                vec_2 + rotation_matrix @ Vec2(0, self.font.kMinWidthY),
                vec_1 + rotation_matrix @ Vec2(0, self.font.kMinWidthY),
            ]

            # draw body
            poly = [str(i) for i in poly]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(poly)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black'
            )
            self.canvas.add(path)

            # tail
            if a3 == SerifType.free: # 鱗
                uroko_scale = (self.font.kMinWidthU / self.font.kMinWidthY - 1.0) / 4.0 + 1
                poly2 = [
                    vec_2 + rotation_matrix @ Vec2(0, -self.font.kMinWidthY),
                    vec_2 + rotation_matrix @ Vec2(-self.font.kAdjustUrokoX[uroko_adjustment] * uroko_scale, 0),
                    vec_2 - (rotation_matrix[:,0] + rotation_matrix[:,1]) * uroko_scale * Vec2(0.5, 1) * Vec2(self.font.kAdjustUrokoX[uroko_adjustment], self.font.kAdjustUrokoY[uroko_adjustment])
                ]
                poly2 = [str(i) for i in poly2]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(poly2)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black'
                )
                self.canvas.add(path)
    
    def __vec_to_degree(vec: Vec2) -> float:
        return np.arctan2(vec.y, vec.x) * 180 / np.pi

    def __draw_curve_universal(self, vec_1: Vec2, vec_s1: Vec2, vec_s2: Vec2, vec_2: Vec2,
                               a2: int, a3: int, opt1, hane_adjustment, opt3, opt4) -> None:
        kMinWidthT = self.font.kMinWidthT - opt1 / 2

        if (temp := a2 % 100) in [0,7,27]:
            delta2 = -1 * self.font.kMinWidthY * 0.5
        elif temp in [1, 2, 6, 22, 32]:
            delta2 = 0
        elif temp == 12:
            delta2 = self.font.kMinWidthY
        else:
            return

        if delta2 != 0:
            vec_d = Vec2(0, delta2) if all(vec_1 == vec_s1) else normalize(vec_1 - vec_s1, delta2)
            vec_1 += vec_d

        corner_offset = 0
        if ((a2 == SerifType.top_right_corner or a2 == SerifType.roofed_narrow) and
            a3 == SerifType.narrow and kMinWidthT > 6):
            contourLength = np.hypot(*(vec_s1 - vec_1)) +
                            np.hypot(*(vec_s2 - vec_1)) +
                            np.hypot(*(vec_2 - vec_s2))
            if (contourLength < 100):
                corner_offset = (kMinWidthT - 6) * ((100 - contourLength) / 100)
                vec_1.x += corner_offset

        if (temp := a3 % 100) in [0,1,7,9,15,14,17,5]:
            delta3 = 0
        elif temp == 8:
            delta3 = -1 * kMinWidthT * 0.5
        else:
            delta3 = delta2

        if delta3 != 0:
            vec_d = Vec2(0, -delta3) if all(vec_2 == vec_s2) else normalize(vec_2 - vec_s2, delta3)
            vec_2 += vec_d

        self.__draw_curve_body(
            vec_1, vec_s1, vec_s2, vec_2,
            a2, a3,
            kMinWidthT,
            opt3,
            opt4
        )
        self.__draw_curve_head(
            vec_1, vec_s1,
            a2,
            kMinWidthT,
            vec_1.y <= vec_2.y,
            corner_offset
        ) # XXX: should check NaN or inf?
        self.__draw_curve_tail(
            vec_s2, vec_2,
            a2, a3,
            kMinWidthT,
            hane_adjustment,
            opt4,
            vec_2.y <= vec_1.y
        )

    def __draw_curve_body(self, vec_1: Vec2, vec_s1: Vec2, vec_s2: Vec2, vec_2: Vec2,
                          a2, a3, kMinWidthT, opt3, opt4) -> None:
        is_quadratic = all(vec_s1 == vec_s2)
        
        hosomi = 0.5

        if np.hypot(*(vec_2 - vec_1)) < 50:
            hosomi += 0.4 * (1 - np.hypot(*(vec_2 - vec_1)) / 50)

        def delta_d(t: float) -> float:
            if (a2 == SerifType.narrow or a2 == SerifType.roofed_narrow) and a3 == SerifType.free: # L2RD: fatten
                return t ** hosomi * self.font.kL2RDfatten
            if a2 == SerifType.narrow or a2 == SerifType.roofed_narrow:
                if is_quadratic:
                    return t ** hosomi
                else:
                    return (t ** hosomi) ** 0.7  # make fatten
            if a3 == SerifType.narrow:
                return (1 - t) ** hosomi
            if is_quadratic and (opt3 > 0 or opt4 > 0):
                return ((self.font.kMinWidthT - opt3 / 2) - (opt4 - opt3) / 2 * t) / self.font.kMinWidthT
            else:
                return 1
            
        left, right = generate_flatten_curve(
            vec_1, vec_s1, vec_s2, vec_2,
            self.font.kRate,
            lambda t: ((temp if (temp := delta_d(t)) > 0.15 else 0.15) * kMinWidthT)
        )

        # horizontal joint, 水平線に接続
        if a2 == 132 or a2 == SerifType.top_right_corner and (vec_1.y > vec_2.y) if is_quadratic else (vec_1.x > vec_s1.x):
            for index in range(len(right) - 1):
                point1 = right[index]
                point2 = right[index + 1]
                if (point1.y <= vec_1.y and vec_1.y <= point2.y):
                    new1 = Vec2(
                        point2.x + (point1.x - point2.x) * (vec_1.y - point2.y) / (point1.y - point2.y) ,
                        vec_1.y
                    )
                    point3 = left[0]
                    point4 = left[1]
                    new2 = Vec2(
                        point3.x + (point4.x - point3.x) * (vec_1.y - point3.y) / (point4.y - point3.y) \
                        if a2 == 132 else \
                        point3.x + (point4.x - point3.x + 1) * (vec_1.y - point3.y) / (point4.y - point3.y),
                        vec_1.y \
                        if a2 == 132 else \
                        vec_1.y + 1
                    )
                    for i in range(index):
                        if len(right) > 0:
                            right = right[1:]
                    right[0] = new1
                    left.insert(0, new2)
                    break
        
        right.reverse()
        dots = left + right
        dots = [str(dot) for dot in dots]
        # draw
        path = svgwrite.path.Path(
            d = "M" + (" L".join(dots)),
            stroke = 'black',
            stroke_width = 0,
            fill = 'black'
        )
        self.canvas.add(path)

    def __draw_curve_head(self, vec_1: Vec2, vec_s1: Vec2,
                          a2: int, kMinWidthT, is_up_to_bottom: bool, corner_offset) -> None:
        """
        process for head of stroke
        """
        if a2 == SerifType.top_left_corner:
            #degree = np.arctan2(vec_1.x - vec_s1.x, vec_s1.y - vec_1.y) / (np.pi * 2) * 360
            degree = self.__vec_to_degree(vec_s1 - vec_1) - 90 % 360
            polygon = [
                Vec2(-kMinWidthT, 0),
                Vec2(+kMinWidthT, 0),
                Vec2(-kMinWidthT, -kMinWidthT)
            ]
            # draw
            polygon = [str(i) for i in polygon]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(polygon)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black',
                transform = f'translate({vec_1}) rotate({degree},0,0)'
            )
            self.canvas.add(path)
        elif a2 == SerifType.free:
            if is_up_to_bottom:
                # from up to bottom
                #degree = np.arctan2(vec_1.x - vec_s1.x, vec_s1.y - vec_1.y) / (np.pi * 2) * 360
                degree = self.__vec_to_degree(vec_s1 - vec_1) - 90 % 360
                head_type = np.arctan2(np.abs(vec_1.y - vec_s1.y),
                                       np.abs(vec_1.x - vec_s1.x)) / np.pi * 2 - 0.4
                head_type *= 2 if head_type > 0 else 16
                pm = -1 if head_type < 0 else 1
                polygon = [
                    Vec2(-kMinWidthT, 1),
                    Vec2(+kMinWidthT, 0),
                    Vec2(-pm * kMinWidthT, -self.font.kMinWidthY * np.abs(head_type))
                ]
                # draw
                polygon = [str(i) for i in polygon]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_1}) rotate({degree},0,0)'
                )
                self.canvas.add(path)
                
                # beginning of the stroke
                move = - head_type * self.font.kMinWidthY if head_type < 0 else 0
                polygon2 = [vec_1] + [
                    Vec2(kMinWidthT, -move),
                    Vec2(kMinWidthT * 1.5, self.font.kMinWidthY - move),
                    Vec2(kMinWidthT - 2, self.font.kMinWidthY * 2 + 1),
                ] \
                if all(vec_1 == vec_s1) else [
                    Vec2(kMinWidthT, -move),
                    Vec2(kMinWidthT * 1.5, self.font.kMinWidthY - move * 1.2),
                    Vec2(kMinWidthT - 2, self.font.kMinWidthY * 2 - move * 0.8 + 1),
                ]
                # draw
                polygon2 = [str(i) for i in polygon2]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon2)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_1}) rotate({degree},0,0)'
                )
                self.canvas.add(path)
            else:
                # bottom to up
                #degree = np.arctan2(vec_s1.y - vec_1.y, vec_s1.x - vec_1.x) / (np.pi * 2) * 360
                degree = self.__vec_to_degree(vec_s1 - vec_1)
                polygon = [
                    Vec2(0, +kMinWidthT),
                    Vec2(0, -kMinWidthT),
                    Vec2(-self.font.kMinWidthY, -kMinWidthT)
                ]
                # draw
                polygon = [str(i) for i in polygon]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_1}) rotate({degree},0,0)'
                )
                self.canvas.add(path)

                polygon2 = [
                    Vec2(0, +kMinWidthT),
                    Vec2(+self.font.kMinWidthY, +kMinWidthT * 1.5),
                    Vec2(+self.font.kMinWidthY * 3, +kMinWidthT * 0.5)
                ]
                # draw
                polygon2 = [str(i) for i in polygon2]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon2)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_1}) rotate({degree},0,0)'
                )
                self.canvas.add(path)

        elif a2 in [22, 27]: # box's right top corner
            # 四角右上鱗斜めでもまっすぐ向き
            # 箱形右上三角形装饰
            polygon = [
                Vec2(-kMinWidthT, -self.font.kMinWidthY),
                Vec2(0, -self.font.kMinWidthY - self.font.kWidth),
                Vec2(+kMinWidthT + self.font.kWidth, +self.font.kMinWidthY),
                Vec2(+kMinWidthT, +kMinWidthT - 1)
            ]
            
            polygon += [
                Vec2(0, +kMinWidthT + 2),
                Vec2(0, 0)
            ] if a2 == Serif.roofed_narrow else [
                Vec2(-kMinWidthT, +kMinWidthT + 4)
            ]
            # draw
            polygon = [str(i) for i in polygon]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(polygon)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black',
                transform = f'translate({vec_1 - Vec2(corner_offset, 0)})'
            )
            self.canvas.add(path)


    def __draw_curve_tail(self, vec_s2: Vec2, vec_2: Vec2,
                          a2: int, a3: int, kMinWidthT, hane_adjustment, opt4, is_bottom_to_up):
        """
        process for tail of stroke
        """
        if a3 in [1,8,15]:
            #degree = np.arctan2(vec_2.y - vec_s2.y, vec_2.x - vec_s2.x) / (np.pi * 2) * 360 
            degree = self.__vec_to_degree(vec_2 - vec_s2)
            kMinWidthT2 = self.font.kMinWidthT - opt4 / 2
            path = [
                "M",
                Vec2(0, -kMinWidthT2),
                "Q",
                Vec2(+kMinWidthT2 * 0.9, -kMinWidthT2 * 0.9),
                Vec2(+kMinWidthT2, 0),
                "Q",
                Vec2(+kMinWidthT2 * 0.9, +kMinWidthT2 * 0.9),
                Vec2(0, +kMinWidthT2)
            ]
            path = [str(i) for i in path]
            path = svgwrite.path.Path(
                d = " ".join(path),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black',
                transform = f'translate({vec_2}) rotate({degree},0,0)'
            )
            self.canvas.add(path)

            if a3 == 15:
                degree = 0
                if is_bottom_to_up:
                    degree = 180
                polygon = [
					Vec2(0, -kMinWidthT + 1),
					Vec2(+2, -kMinWidthT - self.font.kWidth * 5 ),
					Vec2(0, -kMinWidthT - self.font.kWidth * 5),
					Vec2(-kMinWidthT, -kMinWidthT + 1),
				]
                polygon = [str(i) for i in polygon]
                path = svgwrite.path.Path(
                    d = "M" + (" L".join(polygon)),
                    stroke = 'black',
                    stroke_width = 0,
                    fill = 'black',
                    transform = f'translate({vec_2}) rotate({degree},0,0)'
                )
                self.canvas.add(path)

        elif a3 in [SerifType.free, 9]:
            if a3 == SerifType.free and not (a2 == SerifType.narrow or a2 == SerifType.roofed_narrow):
                return
            #degree = np.arctan2(vec_2.y - vec_s2.y, vec_2.x - vec_s2.x) / (np.pi * 2) * 360 
            degree = self.__vec_to_degree(vec_2 - vec_s2)
            tail_type = np.arctan2(np.abs(vec_2.y - vec_s2.y), np.abs(vec_2.x - vec_s2.x)) / np.pi * 2 - 0.6
            tail_type *= 8 if tail_type > 0 else 3
            pm = -1 if tail_type < 0 else 1
            polygon = [
                Vec2(0, +kMinWidthT * self.font.kL2RDfatten),
                Vec2(0, -kMinWidthT * self.font.kL2RDfatten),
                Vec2(np.abs(tail_type) * kMinWidthT * self.font.kL2RDfatten, pm * kMinWidthT * self.font.kL2RDfatten)
            ]
            polygon = [str(i) for i in polygon]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(polygon)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black',
                transform = f'translate({vec_2}) rotate({degree},0,0)'
            )
            self.canvas.add(path)
        elif a3 == 14:
            jump_factor = (6.0 / kMinWidthT) if kMinWidthT > 6 else 1.0
            hane_length = self.font.kWidth * 4 * jump_factor *
                          np.min([1 - hane_adjustment / 10, (kMinWidthT / self.font.kMinWidthT) ** 3])
            polygon = [
                Vec2(0, 0),
                Vec2(0, -kMinWidthT),
                Vec2(-hane_length, -kMinWidthT),
                Vec2(-hane_length, -kMinWidthT * 0.5),
            ]
            polygon = [str(i) for i in polygon]
            path = svgwrite.path.Path(
                d = "M" + (" L".join(polygon)),
                stroke = 'black',
                stroke_width = 0,
                fill = 'black',
                transform = f'translate({vec_2})'
            )
            self.canvas.add(path)


class BezierSerifStrokeDrawer(LegacySerifStrokeDrawer): # XXX Finish this.
    pass

