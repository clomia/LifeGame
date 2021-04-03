import subprocess, sys, socket, time
from threading import Thread
from queue import Queue
from ast import literal_eval
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


class Operator:
    def __init__(self, propheticgrid):
        self.propheticgrid_iter = iter(propheticgrid)
        self.close = False

    def __call__(self):
        if not self.close:
            return self.iteration(PROPHECY_COUNT)
        else:
            return False  # :=에서 사용

    def iteration(self, count):
        fieldset_list = []
        try:
            for _ in range(count):
                delta, space = next(self.propheticgrid_iter)
                fieldset_list.append(delta)
        except StopIteration:
            self.close = True
        finally:
            return fieldset_list


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
            self.sock.recv(4096)

    def run(self):
        self.connect()
        fieldset = self.bprin_queue.get()
        print(f"[SimulConnect] [Get] {fieldset} ")
        init_fieldset = literal_eval(fieldset)
        assert isinstance(init_fieldset, dict)
        p_grid = PropheticGrid(init_fieldset)
        operator = Operator(p_grid)
        field_list = operator()
        field_list[0] = init_fieldset
        field_list.append({})  # 구분자
        self.sock.sendall(str(field_list).encode())
        # field_list를 미리 준비해두기 위함
        while field_list := operator():
            self.sock.recv(4096)
            self.sock.sendall(str(field_list).encode())


def execute():
    bprin_con = BprinConnect(Queue())
    simul_con = SimulConnect(Queue(), bprin_con.queue)
    bprin_con.start()
    simul_con.start()

    proc_list = []
    for arg in [[sys.executable, "core/simul_proc.py"], [sys.executable, "core/bprin_proc.py"]]:
        proc_list.append(subprocess.Popen(arg))
        time.sleep(0.6)
    # 이렇게 안하면 동기로 순차실행되더라
    for proc in proc_list:
        proc.communicate()
