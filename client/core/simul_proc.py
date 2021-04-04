from queue import Queue
from artifacts import *
from scripts import *

# 한번에 200세대씩 제공받으므로 최대 1만 세대까지만 캐싱.
pipe_queue = Queue(50)


connect = SimulConnection(pipe_queue)
connect.start()


class LoadScreen(Entity):
    def __init__(self):
        super().__init__()
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
        controller = CellController(pipe_queue)
        destroy(self)


with simul():
    LoadScreen()
