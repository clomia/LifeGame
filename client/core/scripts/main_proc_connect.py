""" [!]메인 프로세스가 사용하는[!] 프로세스간 통신용 모듈입니다 """
import socket
from threading import Thread
from queue import Queue
from ast import literal_eval
from .constant import *
from .prophecy import *


class BprinConnect(Thread):
    """ 메인 프로세스가 Bprin프로세스와 가지는 연결"""

    def __init__(
        self,
        queue,
        simul_loading_complate_signal: Queue,
        bprin_kill_signal: Queue,
    ):
        """ bprin프로세스의 응답을 self.queue에 담는다"""
        super().__init__()
        self.queue = queue
        self.simul_loading_complate_signal = simul_loading_complate_signal
        self.bprin_kill_signal = bprin_kill_signal
        self.name = "[Main Process]-(bprin connection)"

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("localhost", BPRIN_PROC_PORT))
            sock.listen()
            self.sock, addr = sock.accept()  # * 서브프로세스 첫 신호받는곳 Bloking!
            fieldset = self.sock.recv(4096).decode()
            sock.close()
            del sock

        return fieldset

    def run(self):
        fieldset = self.connect()
        print("[main프로세스]-bprin프로세스로부터 fieldset을 제공받았습니다.")
        self.simul_loading_complate_signal.get()
        print("[main프로세스]-simul프로세스의 로딩 완료 signal이 들어온것을 확인하였습니다.")
        self.bprin_kill_signal.put(SIGNAL)
        self.queue.put(fieldset)
        self.queue.put(SIGNAL)
        # * core/main.ProcControll.bprin_proc_check의 if문->fieldset수신 확인때 인터셉팅 대응용


class Operator:
    """
    메인 프로세스가 수행하는 lifegame연산과 연결하는 도구
    연산 알고리즘 실행 트리거 입니다. 직접 연산하지 않습니다.
    """

    def __init__(self, propheticgrid):
        self.propheticgrid_iter = iter(propheticgrid)
        self.close = False

    def first_call(self):
        return self.iteration(FIRST_PROPHECY_COUNT)

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
    """ 메인 프로세스가 Simul프로세스와 가지는 연결"""

    def __init__(
        self, queue, bprin_queue, simul_loading_complate_signal: Queue, oper_grid=PropheticGrid
    ):
        """ 연산 그리드 클래스(ex: PropheticGrid)를 oper_grid인자로 입력받아 사용합니다 """
        super().__init__()
        self.queue = queue
        self.bprin_queue = bprin_queue
        self.simul_loading_complate_signal = simul_loading_complate_signal
        self.oper_grid = oper_grid
        self.name = "[Main Process]-(simul connection)"

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("localhost", SIMUL_PROC_PORT))
            sock.listen()
            self.sock, addr = sock.accept()
            self.sock.setblocking(True)
            signal = self.sock.recv(4096)
            return signal

    def run(self):
        self.connect()
        print("[main 프로세스]-simul프로세스의 로딩 완료 signal을 수신하였습니다.")
        self.simul_loading_complate_signal.put(SIGNAL)
        fieldset = self.bprin_queue.get()
        init_fieldset = literal_eval(fieldset)
        assert isinstance(init_fieldset, dict)
        p_grid = self.oper_grid(init_fieldset)
        operator = Operator(p_grid)
        field_list = operator.first_call()
        field_list[0] = init_fieldset
        field_list.append({})  # 구분자
        self.sock.sendall(str(field_list).encode())
        # field_list를 미리 준비해두기 위함
        while field_list := operator():
            self.sock.recv(4096)
            self.sock.sendall(str(field_list).encode())
        print("[main 프로세스]-simul 프로세스에게 연산 제공을 완료하여, 연산 채널을 종료합니다.")


class SimulSignalConnect(Thread):
    """ 메인 프로세스가 bprin 부팅 신호를 대기하는 채널"""

    def __init__(self, bprin_booting_signal: Queue):
        super().__init__()
        self.bprin_booting_signal = bprin_booting_signal
        self.name = "[Main Process]-(simul signal connection)"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("localhost", SIMUL_PROC_PORT_2))
            sock.listen()
            self.sock, addr = sock.accept()
            self.sock.setblocking(True)
            signal = self.sock.recv(4096)
            if signal == BPRIN_BOOTING_REQUEST:
                self.bprin_booting_signal.put(signal)
