import subprocess
from multiprocessing import Process

process_list = []
process_list.append(subprocess.Popen(["python", "start.py"]))
process_list.append(subprocess.Popen(["python", "core/executor.py", "asdf"]))

for process in process_list:
    process.communicate()

"""
subprocess.run(["python", "core/executor.py", "asdf"])
subprocess.run(["python", "start.py"])
"""
