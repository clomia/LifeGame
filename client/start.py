import core


def rendering_processing(init):
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
    world = core.Universe(walls, "source/universe.jpg")
    cursor.visible = False
    core.Eye(limit=world.scale)
    controller = core.CellController()
    controller(init)


def input(key):
    if key == "escape":
        core.esc_handler()()


with core.artifacts() as cursor:
    blue_printing = core.InputGrid(pipe_func=rendering_processing)
    core.score_panel(blue_printing)
