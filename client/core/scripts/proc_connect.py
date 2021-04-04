""" [!]다른(서브) 프로세스가 사용하는[!] 프로세스간 통신용 모듈입니다 """
import socket
from threading import Thread
from queue import Queue
from ast import literal_eval
from .constant import *


class BprinConnection(Thread):
    def __init__(self):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40000
        self.queue = Queue()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            fieldset = self.queue.get()
            sock.sendall(str(fieldset).encode())

    def send(self, fieldset):
        self.queue.put(fieldset)


class SimulConnection(Thread):
    def __init__(self, queue):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40001
        self.queue = queue

    def responser(self, sock):
        fieldset_list = sock.recv(1048576)
        print(f"[simul프로세스] fieldset 리스트를 수신")
        fieldset_list = literal_eval(fieldset_list.decode())
        assert isinstance(fieldset_list, list)
        self.queue.put(fieldset_list)
        time.sleep(10)
        sock.sendall("need next".encode("utf-8"))
        return fieldset_list

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            sock.sendall("Loading Complate".encode("utf-8"))
            self.responser(sock)
            while len(self.responser(sock)) >= PROPHECY_COUNT:
                pass