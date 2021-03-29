from queue import Queue
import core

result = Queue()


def pipe(init):
    world = core.Universe(walls, "source/universe.jpg")
    cursor.visible = False
    core.Eye(limit=world.scale)
    controller = core.CellController()
    controller(init)


with core.artifacts() as cursor:
    blue_printing = core.InputGrid(pipe_func=pipe)
    core.score_panel(blue_printing)
    input = core.esc_handler()
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
