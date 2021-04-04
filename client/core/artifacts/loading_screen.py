from ursina import *
from .universe import *
from .origin import *
from .cell_controll import *


class LoadScreen(Entity):
    def __init__(self, pipe_queue):
        super().__init__()
        self.pipe_queue = pipe_queue
        self.parent = camera.ui
        self.origin = (-0.5, 0.5)
        self.model = "quad"
        x_ratio, y_ratio = window.screen_resolution
        value = 1 / y_ratio
        self.scale_x = x_ratio * value
        self.scale_y = y_ratio * value
        self.texture = load_texture("source/load_screen.jpg")
        invoke(self.main_execute, delay=1)

    def main_execute(self):
        walls = {
            "bottom": "source/wall_bottom.jpg",
            "top": "source/wall_top.jpg",
            "left": "source/wall_front.jpg",
        }
        world = Universe(walls, "source/universe.jpg")
        Eye(limit=world.scale)
        CellController(self.pipe_queue)
        destroy(self)