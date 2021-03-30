if __name__ == "__main__":
    from artifacts import *
    from scripts import *
else:
    from .artifacts import *
    from .scripts import *

with artifacts() as cursor:
    blue_printing = InputGrid()
    score_panel(blue_printing)
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
