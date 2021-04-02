import subprocess, sys, socket
from threading import Thread
from queue import Queue

if __name__ == "__main__":
    from artifacts import *
    from scripts import *
else:
    from .artifacts import *
    from .scripts import *


class BprinConnect(Thread):
    def __init__(self, queue):
        """ bprin프로세스의 응답을 self.queue에 담는다"""
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40000
        self.queue = queue

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.local_host, self.port))
            sock.listen()
            self.sock, addr = sock.accept()
            fieldset = self.sock.recv(4096).decode()
        return fieldset

    def run(self):
        fieldset = self.connect()
        print(f"[BprinConnect]프로세스로부터 fieldset {fieldset} 을 수신")
        self.queue.put(fieldset)


class SimulConnect(Thread):
    def __init__(self, queue, bprin_queue):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40001
        self.queue = queue
        self.bprin_queue = bprin_queue

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.local_host, self.port))
            sock.listen()
            self.sock, addr = sock.accept()
            signal = self.sock.recv(4096).decode()
        return signal

    def run(self):
        signal = self.connect()
        print(f"[SimulConnect] 프로세스로부터 signal {signal} 수신")
        fieldset = self.bprin_queue.get()
        print(f"[SimulConnect] [Get] {fieldset} ")
        # PropheticGrid(fieldset)
        self.sock.sendall(fieldset.encode())


def execute():
    bprin_con = BprinConnect(Queue())
    simul_con = SimulConnect(Queue(), bprin_con.queue)
    bprin_con.start()
    simul_con.start()

    proc_list = []
    for arg in [[sys.executable, "core/simul_proc.py"], [sys.executable, "core/bprin_proc.py"]]:
        proc_list.append(subprocess.Popen(arg))
    for proc in proc_list:
        proc.communicate()
        time.sleep(1)
