""" 
각 프로세스가 input함수로 할당할때 사용한다
ex: input = react_handler(bprin_react_map)
"""
from .origin import *

default_react_map: dict = {}

bprin_react_map: dict = {
    "escape": Esc().handler,
}

simul_react_map: dict = {
    "escape": Esc(mouse_locked=True, bg_deep=True).handler,
}


# ---------------------------------------------------------
bprin_react_map = {**default_react_map, **bprin_react_map}
simul_react_map = {**default_react_map, **simul_react_map}


def react_handler(react_map):
    """
    input = react_handler(bprin_react_map)

    input = react_handler(simul_react_map)

    위와같이 사용합니다.\n
    이 함수는 함수를 반환합니다.
    """

    def func(key):
        try:
            react_map[key]()
        except KeyError:
            # print(f"[react_map]Not Mapping: {key}")
            pass

    return func


if __name__ == "__main__":
    from ursina import *

    app = Ursina()
    input = react_handler(bprin_react_map)
    app.run()
