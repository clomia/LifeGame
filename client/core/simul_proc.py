import socket
from threading import Thread
from queue import Queue
from ast import literal_eval
from artifacts import *
from scripts import *

# 한번에 200세대씩 제공받으므로 최대 1만 세대까지만 캐싱.
pipe_queue = Queue(50)


class Connection(Thread):
    def __init__(self, queue):
        super().__init__()
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.port = 40001
        self.queue = queue

    def responser(self, sock):
        fieldset_list = sock.recv(1048576)
        print(f"[simul프로세스] fieldset 리스트를 수신")
        fieldset_list = literal_eval(fieldset_list.decode())
        assert isinstance(fieldset_list, list)
        self.queue.put(fieldset_list)
        time.sleep(10)
        sock.sendall("need next".encode("utf-8"))
        return fieldset_list

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.local_host, self.port))
            sock.sendall("Loading Complate".encode("utf-8"))
            self.responser(sock)
            while len(self.responser(sock)) >= PROPHECY_COUNT:
                pass
            print("연산 수신 끝!")


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