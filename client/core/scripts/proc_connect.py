""" [!]다른(서브) 프로세스가 사용하는[!] 프로세스간 통신용 모듈입니다 """
import socket, time
from threading import Thread
from queue import Queue
from ast import literal_eval
from .constant import *


class BprinConnection(Thread):
    def __init__(self):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = BPRIN_PROC_PORT
        self.queue = Queue()
        self.daemon = True
        self.name = "[Sub Process]-(bprin connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            fieldset = self.queue.get()
            sock.sendall(str(fieldset).encode())

    def send(self, fieldset):
        self.queue.put(fieldset)


class SimulConnection(Thread):
    def __init__(self, queue, success_signal: Queue):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = SIMUL_PROC_PORT
        self.queue = queue
        self.daemon = True
        self.name = "[Sub Process]-(simul connection)"
        self.success_signal_queue = success_signal

    def responser(self, sock):
        fieldset_list = sock.recv(1048576)
        fieldset_list = literal_eval(fieldset_list.decode())
        assert isinstance(fieldset_list, list)
        self.queue.put(fieldset_list)
        time.sleep(10)
        sock.sendall("need next".encode("utf-8"))
        return fieldset_list

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            self.success_signal_queue.get()
            sock.sendall("Loading Complate".encode("utf-8"))
            self.responser(sock)
            while len(self.responser(sock)) >= PROPHECY_COUNT:
                pass