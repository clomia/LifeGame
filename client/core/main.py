import subprocess, sys, time
from queue import Queue
from threading import Thread, Lock
from contextlib import contextmanager
from .scripts import *


class ProcControll:
    """ 프로그렘 실행기"""

    def __init__(self):
        """ 멀티 프로레싱 멀티 쓰레딩의 실행 트리거 클래스. """
        self.shutdown_request = Queue()
        self.bprin_queue = Queue()
        self.simul_loading_complate_signal = Queue()

    def main(self):
        """ 모든것을 실행합니다"""
        bprin_con = BprinConnect(self.bprin_queue, self.simul_loading_complate_signal)
        simul_con = SimulConnect(Queue(), self.bprin_queue, self.simul_loading_complate_signal)
        bprin_con.start()
        simul_con.start()
        self.simul_proc = subprocess.Popen([sys.executable, "core/simul_proc.py"])
        time.sleep(0.1)
        self.bprin_proc = subprocess.Popen([sys.executable, "core/bprin_proc.py"])
        Thread(target=self.simul_proc_check, daemon=True).start()
        Thread(target=self.bprin_proc_check, daemon=True).start()
        Thread(target=self.shutdown, daemon=True).start()

    def bprin_proc_check(self):
        """ 프로세스가 죽으면 큐에 신호를 넣습니다"""
        self.bprin_proc.wait()
        if self.bprin_queue.empty():
            self.shutdown_request.put(True)

    def simul_proc_check(self):
        """ 프로세스가 죽으면 큐에 신호를 넣습니다"""
        self.simul_proc.wait()
        self.shutdown_request.put(True)

    def shutdown(self):
        """
        큐에 신호가 들어오면 실행중인 서브 프로세스들을 모두 죽입니다
        이 함수를 직접 호출하지 마세요!

        self.shutdown_request.put(True) 를 할 때 이 함수가 실행됩니다!
        """
        self.shutdown_request.get()
        self.bprin_proc.kill()
        self.simul_proc.kill()

    @contextmanager
    def execute(self):
        """
        사용: with ProcControll().execute():
        확실하고 안전한 종료를 보장
        """
        self.main()
        try:
            yield
        finally:
            pass
            """
            self.bprin_proc.kill()
            self.simul_proc.kill()
            sys.exit()
            finally가 바로 실행되버림
            """
