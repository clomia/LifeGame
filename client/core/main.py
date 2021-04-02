if __name__ == "__main__":
    from artifacts import *
    from scripts import *
else:
    from .artifacts import *
    from .scripts import *

"""
def input(key):
    if key == "escape":
        esc_handler()



with artifacts():
    blueprinting = InputGrid()
    score_panel(blueprinting)
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
"""
