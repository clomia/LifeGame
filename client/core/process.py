from multiprocessing import Process, Queue
from threading import Thread
from ursina import *
import core

prophecy_result = Queue()


class Script(Process):
    def __init__(self, init_space, queue):
        super().__init__()
        self.name = "Script Process"
        self.init_space = init_space
        self.queue = queue

    def run(self):
        super_field = core.PropheticGrid(self.init_space)
        count = 0
        for delta, space in super_field:
            data = []
            if count < 10:
                data.append(delta)
                count += 1
            else:
                self.queue.put(data)
                data.clear()
                count = 0


class Render(Entity):
    def __init__(self, cell_controller, init_space):
        super().__init__()
        self.controller = cell_controller
        self.super_field = core.PropheticGrid(init_space)
        self.super_iter = iter(self.super_field)

    def input(self, key):
        if key == "space":
            delta, space = next(self.super_iter)
            self.controller(delta)


def rendering_processing(init):
    world = core.Universe(walls, "source/universe.jpg")
    cursor.visible = False
    core.Eye(limit=world.scale)
    controller = core.CellController()
    controller(init)
    Render(controller, init)


def input(key):
    if key == "escape":
        core.esc_handler()()


with core.artifacts() as cursor:
    blue_printing = core.InputGrid(pipe_func=rendering_processing)
    core.score_panel(blue_printing)
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
