""" [!]다른(서브) 프로세스가 사용하는[!] 프로세스간 통신용 모듈입니다 """
import socket, time
from threading import Thread
from queue import Queue
from ast import literal_eval
from .constant import *


class BprinConnection(Thread):
    def __init__(self):
        super().__init__()
        self.port = BPRIN_PROC_PORT
        self.queue = Queue()
        self.daemon = True
        self.name = "[Sub Process]-(bprin connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", self.port))
            fieldset = self.queue.get()
            sock.sendall(str(fieldset).encode())

    def send(self, fieldset):
        self.queue.put(fieldset)


class SimulConnection(Thread):
    def __init__(self, queue, simul_loading_complate_signal: Queue):
        super().__init__()
        self.port = SIMUL_PROC_PORT
        self.queue = queue
        self.daemon = True
        self.name = "[Sub Process]-(simul connection)"
        self.simul_loading_complate_signal = simul_loading_complate_signal
        self.oper_counter = 0

    def responser(self, sock):
        fieldset_list = sock.recv(1048576)
        fieldset_list = literal_eval(fieldset_list.decode())
        assert isinstance(fieldset_list, list)
        self.queue.put(fieldset_list)
        self.oper_counter += 1
        print(f"[simul프로세스]-연산을 제공받았습니다-제공받은 정보량: 총 [{self.oper_counter*PROPHECY_COUNT}]세대")
        time.sleep(OPERATION_SPEED)
        sock.sendall("need next".encode("utf-8"))
        return fieldset_list

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", self.port))
            self.simul_loading_complate_signal.get()
            sock.sendall("Loading Complate".encode("utf-8"))
            print("[simul프로세스]-로딩이 완료되서 메인 프로세스로 signal을 전송하였습니다")
            self.responser(sock)
            while len(self.responser(sock)) >= PROPHECY_COUNT:
                pass