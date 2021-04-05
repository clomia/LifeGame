from queue import Queue
from artifacts import *
from scripts import *

# 한번에 200세대씩 제공받으므로 최대 1만 세대까지만 캐싱.
pipe_queue = Queue(50)
success_signal = Queue(1)

connect = SimulConnection(pipe_queue, success_signal)
connect.start()


with simul():
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue)
    # todo simul success signal의 시작부분인 여기서 너무 빨리 신호를 보내는것이 문제다 다른데는 문제 없더라
    # * 생각해보니까 로딩창을 먼저 띄우기 때문에 app.run()사이의 간격은 거의 없다.
    success_signal.put(True)
