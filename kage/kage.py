from .components    import Components
from .font          import Font
from .stroke        import Stroke
from .vec2          import Vec2

from argparse       import Namespace
import csv
import numpy as np
import svgwrite

class Kage:
    def __init__(self, dump_path: str=None, ignore_component_version=False,
                 font: Font=None) -> None:
        self.components = Components(ignore_component_version)
        self.font = font

        assert dump_path != None, "Path to dump_newest_only.txt/dump_all_versions.txt must be set."
        with open(dump_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = csv.reader(lines, delimiter='|')
        for i, line in enumerate(lines):
            if i <= 1 or len(line) < 3:
                continue
            line = [i.strip() for i in line]

            self.components.push(line[0], line[2])

    @property
    def type(self):
        return self.font

    @type.setter
    def type(self, another):
        self.font = another

    def make_glyph(self, name: str) -> svgwrite.Drawing:
        assert self.font != None, "Font must be set before generating."
        data = self.components.search(name)
        canvas = svgwrite.Drawing(size=('200', '200'))
        return self.make_glyph_with_data(canvas, data)

    def make_glyph_with_name(self, canvas: svgwrite.Drawing, name: str) -> svgwrite.Drawing:
        data = self.components.search(name)
        return self.make_glyph_with_data(canvas, data)

    def make_glyph_with_data(self, canvas: svgwrite.Drawing, data: str) -> svgwrite.Drawing:
        if data != '':
            strokes_list = self.get_each_strokes(data)
            return self.font.drawer(canvas, strokes_list)

    def get_each_strokes(self, data: str) -> list[Stroke]:
        strokes_list = []
        strokes = data.split('$')
        for stroke in strokes:
            columns = stroke.split(':')
            columns += [np.nan] * (11 - len(columns))
            if columns[0] != '99':
                strokes_list.append(Stroke(columns))
            else:
                component_data = self.components.search(columns[7])
                if component_data != '':
                    strokes_list.extend(
                        self.get_each_strokes_of_component(component_data, 
                            float(columns[3]), 
                            float(columns[4]), 
                            float(columns[5]), 
                            float(columns[6]), 
                            float(columns[1]), 
                            float(columns[2]), 
                            float(columns[9]), 
                            float(columns[10])
                        )
                    )

        return strokes_list

    def get_each_strokes_of_component(self, component_data, x1, y1, x2, y2, sx, sy, sx2, sy2) -> list[Stroke]:
        strokes = self.get_each_strokes(component_data)
        box = self.get_box(strokes)
        if sx != 0 or sy != 0:
            if sx > 100:
                sx -= 200
            else:
                sx2 = 0
                sy2 = 0
        for stroke in strokes:
            if (sx != 0 or sy != 0):
                stroke.stretch(sx, sx2, sy, sy2, box.minX, box.maxX, box.minY, box.maxY)

            vec_1 = Vec2(x1, y1)
            vec_2 = Vec2(x2, y2)
            stroke.vec_1 = vec_1 + stroke.vec_1 * (vec_2 - vec_1) / 200
            stroke.vec_2 = vec_1 + stroke.vec_2 * (vec_2 - vec_1) / 200
            stroke.vec_3 = vec_1 + stroke.vec_3 * (vec_2 - vec_1) / 200
            stroke.vec_4 = vec_1 + stroke.vec_4 * (vec_2 - vec_1) / 200

        return strokes

    def get_box(self, strokes: list[Stroke]) -> Namespace:
        minX = 200
        minY = 200
        maxX = 0
        maxY = 0

        for stroke_ in strokes:
            s_box = stroke_.get_box()
            minX = np.min([minX, s_box.minX])
            maxX = np.max([maxX, s_box.maxX])
            minY = np.min([minY, s_box.minY])
            maxY = np.max([maxY, s_box.maxY])

        return Namespace(**{'minX': minX, 'maxX': maxX, 'minY': minY, 'maxY': maxY})
