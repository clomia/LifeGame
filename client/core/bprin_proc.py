from artifacts import *
from scripts import *


connect = BprinConnection()
connect.start()


def offline_bprin():
    blue_printer = InputGrid(pipe_func=lambda x: connect.send(x))
    score_panel(blue_printer)


with bprin(lang="en") as cursor:
    input = react_handler(bprin_react_map)
    home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None, intro=True)
