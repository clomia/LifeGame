from queue import Queue
from artifacts import *
from scripts import *


connect = BprinConnection()
connect.start()

with bprin() as cursor:

    def offline_bprin():
        blue_printer = InputGrid(pipe_func=SimulLoadWaiter(connect, cursor))
        score_panel(blue_printer)

    input = react_handler(bprin_react_map)
    home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None, intro=True)
