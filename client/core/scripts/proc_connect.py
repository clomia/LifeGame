""" [!]다른(서브) 프로세스가 사용하는[!] 프로세스간 통신용 모듈입니다 """
import socket, time
from threading import Thread
from queue import Queue
from ast import literal_eval
from .constant import *


class BprinConnection(Thread):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.name = "[Sub Process]-(bprin connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", BPRIN_PROC_PORT))
            fieldset = self.queue.get()
            sock.sendall(str(fieldset).encode())

    def send(self, fieldset):
        self.queue.put(fieldset)


class SimulConnection(Thread):
    def __init__(self, queue, simul_loading_complate_signal: Queue):
        super().__init__()
        self.queue = queue
        self.name = "[Sub Process]-(simul connection)"
        self.simul_loading_complate_signal = simul_loading_complate_signal
        self.oper_counter = 0

    def responser(self, sock, first_call=False):
        fieldset_list = sock.recv(2 ** 20)  # info 104_8576byte를 넘어가면 에러 발생으로인해 연산채널이 끊긴다.
        print(f"recv는 되었다!!!! {len(fieldset_list)}")
        fieldset_list = literal_eval(fieldset_list.decode())
        assert isinstance(fieldset_list, list)
        self.queue.put(fieldset_list)
        self.oper_counter += 1
        data_scale = (self.oper_counter - 1) * PROPHECY_COUNT + FIRST_PROPHECY_COUNT
        print(
            f"[simul 프로세스]-연산을 제공받았습니다-제공받은 정보량: 총 [{data_scale if not first_call else FIRST_PROPHECY_COUNT}]세대"
        )
        if first_call:
            time.sleep(FIRST_OPERATION_SPEED)
        else:
            time.sleep(OPERATION_SPEED)
        sock.sendall(PROPHECY_REQUEST)
        return True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", SIMUL_PROC_PORT))
            self.simul_loading_complate_signal.get()
            sock.sendall("LoadingComplate".encode("utf-8"))
            print("[simul프로세스]-로딩이 완료되서 [main 프로세스]로 signal을 전송하였습니다")
            self.responser(sock, first_call=True)
            try:
                while self.responser(sock):
                    pass
            except:
                print("[simul 프로세스]-[main 프로세스]로부터 모든 연산을 제공받아서. 연산 제공 채널이 사라졌습니다.")


class SimulSignalConnection(Thread):
    """ simul 프로세스가 bprin 부팅 신호를 전송하는 채널"""

    def __init__(self, bprin_booting_signal_pipe):
        super().__init__()
        self.bprin_booting_signal_pipe = bprin_booting_signal_pipe
        self.name = "[simul Process]-(simul signal connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", SIMUL_PROC_PORT_2))
            self.bprin_booting_signal_pipe.get()
            sock.sendall(BPRIN_BOOTING_REQUEST)


class SimulShutdownConnection(Thread):
    """ simul 프로세스가 shutdown 요청 신호를 전송하는 채널"""

    def __init__(self, simul_shutdown_signal_pipe):
        super().__init__()
        self.simul_shutdown_signal_pipe = simul_shutdown_signal_pipe
        self.name = "[simul Process]-(simul shutdown connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", SIMUL_PROC_PORT_3))
            self.simul_shutdown_signal_pipe.get()
            sock.sendall(BPRIN_BOOTING_REQUEST)


class BprinShutdownConnection(Thread):
    """ bprin 프로세스가 shutdown 요청 신호를 전송하는 채널"""

    def __init__(self, bprin_shutdown_signal_pipe):
        super().__init__()
        self.bprin_shutdown_signal_pipe = bprin_shutdown_signal_pipe
        self.name = "[bprin Process]-(bprin shutdown connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", BPRIN_PROC_PORT_2))
            self.bprin_shutdown_signal_pipe.get()
            sock.sendall(BPRIN_BOOTING_REQUEST)