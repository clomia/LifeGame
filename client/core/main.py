import subprocess, sys, time
from queue import Queue
from threading import Thread
from .scripts import *


class ProcControll:
    def __init__(self):
        """ 연산과 프로세스들 팬아웃 """
        self.shutdown_request = Queue()
        bprin_con = BprinConnect(Queue())
        simul_con = SimulConnect(Queue(), bprin_con.queue)
        bprin_con.start()
        simul_con.start()

        self.proc_list = []
        for arg in [[sys.executable, "core/simul_proc.py"], [sys.executable, "core/bprin_proc.py"]]:
            self.proc_list.append(subprocess.Popen(arg))
            time.sleep(0.1)
        # 이렇게 안하면 동기로 순차실행되더라
        for proc in self.proc_list:
            proc.communicate()
            Thread(target=self.shutdown_handle, args=(proc,)).start()
        Thread(target=self.shutdown).start()

    def shutdown_handle(self, proc):
        proc.wait()
        self.shutdown_request.put(True)

    def shutdown(self):
        self.shutdown_request.get()
        for proc in self.proc_list:
            proc.kill()
