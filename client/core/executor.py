""" 서브 프로세스로 실행시키는 시뮬레이션 모듈이다"""

import sys
from ast import literal_eval
from ursina import *

if __name__ == "__main__":
    from artifacts import *
    from scripts import *
else:
    from .artifacts import *
    from .scripts import *


class KeyHandler(Entity):
    def __init__(self):
        super().__init__()
        self.response_mapping = {
            "space": self.space_input,
            "escape": self.escape_input,
        }

    def input(self, key):
        if key in self.response_mapping:
            self.response_mapping[key]()

    def space_input(self):
        pass

    def escape_input(self):
        esc_handler(mouse_locked=True)


class Simulation:
    def __init__(self, init_space):
        super().__init__()
        self.name = "3D Phase Process"
        self.init_space = init_space
        self.source = {
            "walls": {
                "bottom": "source/wall_bottom.jpg",
                "top": "source/wall_top.jpg",
                "left": "source/wall_front.jpg",
            },
            "universe": "source/universe.jpg",
        }

    def run(self):
        with artifacts_3D() as cursor:
            # todo ESC 커서 처리
            KeyHandler()
            # super_field = PropheticGrid(self.init_space)
            world = Universe(self.source["walls"], self.source["universe"])
            Eye(limit=world.scale)
            controller = CellController()
            controller(self.init_space)


script, *init_space = sys.argv
Simulation({(0, 0): 1}).run()
