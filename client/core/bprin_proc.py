import socket
from threading import Thread
from queue import Queue
from artifacts import *


class Connection(Thread):
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


connect = Connection()
connect.start()

with blue_printing() as cursor:
    blue_printing = InputGrid(pipe_func=lambda x: connect.send(x))
    score_panel(blue_printing)