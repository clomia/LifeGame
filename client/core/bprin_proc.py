import sys
from artifacts import *
from scripts import *

script, *option = sys.argv
connect = BprinConnection()
connect.start()

with bprin() as cursor:

    def offline_bprin():
        blue_printer = InputGrid(pipe_func=SimulLoadWaiter(connect, cursor))
        score_panel(blue_printer)

    input = react_handler(bprin_react_map)
    if not option:
        home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None, intro=True)
    else:
        home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None)
