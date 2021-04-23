from queue import Queue
from artifacts import *
from scripts import *


pipe_queue = CacheManagementPipe(limit=50)
simul_loading_complate_signal = Queue(1)
bprin_booting_signal_pipe = Queue(1)
shot_down_signal_pipe = Queue(1)
SimulShutdownConnection(shot_down_signal_pipe).start()
SimulConnection(pipe_queue, simul_loading_complate_signal).start()
SimulSignalConnection(bprin_booting_signal_pipe).start()


def shut_down(arg):
    """ arg로는 버튼객체가 들어온다. 이것은 클래스 속성으로 정의한것이 원인으로 추정된다, arg를 없애면 안된다!"""
    shot_down_signal_pipe.put(SIGNAL)


with simul():
    ShutDownBtn.shut_down_func = shut_down
    S_ESC.pipe_setting(bprin_booting_signal_pipe)
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue, simul_loading_complate_signal, bprin_booting_signal_pipe)
