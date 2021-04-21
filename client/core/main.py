import subprocess, sys, time
from queue import Queue
from threading import Thread
from contextlib import contextmanager
from .scripts import *


class ProcControll:
    """ 프로그렘 실행기"""

    def __init__(self):
        """ 멀티 프로레싱 멀티 쓰레딩의 실행 트리거 클래스. """
        self.shutdown_request = Queue()
        self.bprin_queue = Queue()
        self.simul_loading_complate_signal = Queue()
        self.bprin_kill_signal = Queue()
        self.bprin_booting_request = Queue()

    def main(self):
        """ 모든것을 실행합니다"""
        self.bprin_connect = BprinConnect(
            self.bprin_queue,
            self.simul_loading_complate_signal,
            self.bprin_kill_signal,
        )
        self.simul_connect = SimulConnect(
            Queue(),
            self.bprin_queue,
            self.simul_loading_complate_signal,
        )
        self.bprin_connect.start()
        self.simul_connect.start()
        print(self.bprin_connect)
        SimulSignalConnect(self.bprin_booting_request).start()
        self.simul_process = subprocess.Popen([sys.executable, "core/simul_proc.py"])
        time.sleep(0.1)
        self.bprin_process = subprocess.Popen([sys.executable, "core/bprin_proc.py"])
        for method in self.threading_helper():
            Thread(target=method, daemon=True).start()
        Thread(target=self.bprin_starter).start()

    def bprin_starter(self):
        """ 이 함수를 실행하는 쓰레드 자체가 문제다"""
        self.bprin_booting_request.get()
        print(
            f"simul_connect: {self.simul_connect} , bprin_connect: {self.bprin_connect} -< 현재 상태ㅇ!!"
        )

        print("커넥션 실행 이전!")
        BprinConnect(
            self.bprin_queue,
            self.simul_loading_complate_signal,
            self.bprin_kill_signal,
        ).start()
        print("커넥션 실행 완료!")
        self.bprin_process = subprocess.Popen([sys.executable, "core/bprin_proc.py", "reboot"])

        for method in [self.bprin_proc_check]:
            Thread(target=method, daemon=True).start()

    def threading_helper(self):
        yield self.simul_proc_check
        yield self.bprin_proc_check
        yield self.shutdown
        yield self.bprin_killer

    def bprin_proc_check(self):
        """ 프로세스가 죽으면 큐에 신호를 넣습니다"""
        self.bprin_process.wait()
        if self.bprin_queue.empty():
            self.shutdown_request.put(SIGNAL)

    def bprin_killer(self):
        self.bprin_kill_signal.get()
        self.bprin_process.kill()

    def simul_proc_check(self):
        """ 프로세스가 죽으면 큐에 신호를 넣습니다"""
        self.simul_process.wait()
        self.shutdown_request.put(SIGNAL)

    def shutdown(self):
        """
        큐에 신호가 들어오면 실행중인 서브 프로세스들을 모두 죽입니다
        이 함수를 직접 호출하지 마세요!

        self.shutdown_request.put(SIGNAL) 를 할 때 이 함수가 실행됩니다!
        """
        self.shutdown_request.get()
        print("[main 프로세스]-shutdown signal을 수신하였습니다. 프로세스들을 모두 죽입니다.")
        self.bprin_process.kill()
        self.simul_process.kill()

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
