from queue import Queue
from artifacts import *
from scripts import *

# 한번에 200세대씩 제공받으므로 최대 1만 세대까지만 캐싱.
pipe_queue = Queue(50)
simul_loading_complate_signal = Queue(1)

connect = SimulConnection(pipe_queue, simul_loading_complate_signal)
connect.start()


with simul():
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue)
    simul_loading_complate_signal.put(True)
