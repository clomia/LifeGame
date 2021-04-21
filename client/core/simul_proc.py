from queue import Queue
from artifacts import *
from scripts import *


pipe_queue = CacheManagementPipe(limit=50)
simul_loading_complate_signal = Queue(1)
bprin_booting_signal_pipe = Queue(1)

SimulConnection(pipe_queue, simul_loading_complate_signal).start()
SimulSignalConnection(bprin_booting_signal_pipe).start()


with simul():
    S_ESC.pipe_setting(bprin_booting_signal_pipe)
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue, simul_loading_complate_signal, bprin_booting_signal_pipe)
