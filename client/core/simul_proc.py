import time
from queue import Queue
from artifacts import *
from scripts import *


class CacheManagementPipe(Queue):
    def __init__(self, limit: int):
        """
        이동하는 데이터가 limit를 넘어가면 데이터 수신 간격을 대폭 늘립니다.

        메인 프로세스의 연산 쓰레드가 제공한 데이터가 통째로 이 파이프를 통과합니다.
        다음 파이프에서 데이터가 분해되며 그 다음에는 필요할때에 컨테이너로 연결됩니다.

        하단 파이프와 컨테이너에서 받는 부담을 이곳에서 관리하기 위한 클래스입니다.
        """
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


connect = SimulConnection(pipe_queue, simul_loading_complate_signal)
connect.start()


with simul():
    input = react_handler(simul_react_map)
    LoadScreen(pipe_queue, simul_loading_complate_signal)
