from queue import Queue
from artifacts import *
from scripts import *


pipe_queue = CacheManagementPipe(limit=50)
simul_loading_complate_signal = Queue(1)


connect = SimulConnection(pipe_queue, simul_loading_complate_signal)
connect.start()


with simul():
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue, simul_loading_complate_signal)
