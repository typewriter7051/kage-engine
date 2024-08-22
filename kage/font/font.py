from ..stroke   import Stroke

from abc        import ABC, abstractmethod
import svgwrite

class Font(ABC):
    def __init__(self, size=2) -> None:
        self.kRate = 100
        if size == 1:
            self.kWidth = 3
            self.kKakato = 1.8
            self.kMage = 6
            self.kUseCurve = False
        else:
            self.kWidth = 5
            self.kKakato = 3
            self.kMage = 10
            self.kUseCurve = False
    
    @abstractmethod
    def drawer(self, canvas: svgwrite.Drawing, strokes_list: list[Stroke]):
        raise NotImplementedError()

