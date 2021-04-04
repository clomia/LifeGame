import subprocess, sys, time
from queue import Queue
from .scripts import *


def execute():
    """ 연산과 프로세스들 팬아웃 """
    bprin_con = BprinConnect(Queue())
    simul_con = SimulConnect(Queue(), bprin_con.queue)
    bprin_con.start()
    simul_con.start()

    proc_list = []
    for arg in [[sys.executable, "core/simul_proc.py"], [sys.executable, "core/bprin_proc.py"]]:
        proc_list.append(subprocess.Popen(arg))
        time.sleep(0.1)
    # 이렇게 안하면 동기로 순차실행되더라
    for proc in proc_list:
        proc.communicate()
