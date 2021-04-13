from ursina import *

outline = lambda obj, opacity: Entity(
    parent=obj,
    model=Quad(segments=0, mode="line", thickness=2),
    color=color.rgba(196, 235, 232, opacity),
    z=-0.01,
)

SIGNAL = object()


class FullUI(Entity):
    """ 화면을 가득 채우는 UI를 만들기 위한 부모클래스"""

    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.origin = (-0.5, 0.5)
        self.model = "quad"
        x_ratio, y_ratio = window.screen_resolution
        value = 1 / y_ratio
        self.scale_x = x_ratio * value
        self.scale_y = y_ratio * value


class UI(Entity):
    """ 화면에 고정된 Entity(->UI)를 만들기 위한 부모클래스"""

    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.origin = (-0.5, 0.5)
        self.model = "quad"