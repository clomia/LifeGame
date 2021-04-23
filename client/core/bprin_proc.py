import sys
from artifacts import *
from scripts import *

script, *option = sys.argv

shot_down_signal_pipe = Queue(1)
BprinShutdownConnection(shot_down_signal_pipe).start()
connect = BprinConnection()
connect.start()


def shut_down(arg):
    """ arg로는 버튼객체가 들어온다. 이것은 클래스 속성으로 정의한것이 원인으로 추정된다, arg를 없애면 안된다!"""
    shot_down_signal_pipe.put(SIGNAL)


with bprin() as cursor:

    ShutDownBtn.shut_down_func = shut_down

    def offline_bprin():
        blue_printer = InputGrid(pipe_func=SimulLoadWaiter(connect, cursor))
        score_panel(blue_printer)

    input = react_handler(bprin_react_map)
    if not option:
        home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None, intro=True)
    else:
        home_screen(cursor, offline_pipe=offline_bprin, online_pipe=None)
