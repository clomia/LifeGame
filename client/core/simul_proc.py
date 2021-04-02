import socket
from threading import Thread
from queue import Queue
from ast import literal_eval
from artifacts import *

pipe_queue = Queue()


class Connection(Thread):
    def __init__(self, queue):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40001
        self.queue = queue

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            sock.sendall("Loading Complate".encode("utf-8"))
            fieldset = sock.recv(4096)
            print(f"[simul프로세스] fieldset {fieldset.decode()} 을 수신")
            fieldset = literal_eval(fieldset.decode())
            assert isinstance(fieldset, dict)
            fieldset[0] = True  # 초기 fieldset이라는 구분자
            self.queue.put(fieldset)


connect = Connection(pipe_queue)
connect.start()

with simulation():
    walls = {
        "bottom": "source/wall_bottom.jpg",
        "top": "source/wall_top.jpg",
        "left": "source/wall_front.jpg",
    }
    world = Universe(walls, "source/universe.jpg")
    Eye(limit=world.scale)
    controller = CellController(pipe_queue)
