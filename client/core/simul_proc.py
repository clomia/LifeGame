import time
from queue import Queue
from artifacts import *
from scripts import *

# 이 pipe_queue로 들어온건 소비자 pipe로 분해되서 바로 들어간다
class CacheManagementPipe(Queue):
    def __init__(self, limit: int):
        """ pipe를 통과하는 데이터들을 모니터링 하면서 정보량을 관리"""
        super().__init__()
        self.limit = limit
        self.cache_full = lambda: self.cache_counter >= limit
        self.cache_counter = 0

    def put(self, item):
        if self.cache_full():
            print(
                f"[simul 프로세스][CacheManagementPipe]데이터 과부화(연산 프로세스의 데이터 제공) 방지중...\n",
                f"------데이터 수신량:{self.cache_counter} X {PROPHECY_COUNT}\n",
                f"------limit: {self.limit}\n",
                f"------(프로세스 채널링 관리)감소된 연산 간격: {OPERATION_SPEED} + {SLOW_OPERATION_SPEED}초",
            )
            time.sleep(SLOW_OPERATION_SPEED)
        super().put(item)
        self.cache_counter += 1


pipe_queue = CacheManagementPipe(limit=50)
simul_loading_complate_signal = Queue(1)

# 생산자
connect = SimulConnection(pipe_queue, simul_loading_complate_signal)
connect.start()


with simul():
    input = react_handler(simul_react_map)
    # 소비자
    LoadScreen(pipe_queue, simul_loading_complate_signal)
