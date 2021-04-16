""" 주요 게임 로직이다, UI는 simul_ui의 객체들을 사용한다."""
from ursina import *
from .simul_ui import *


class IterStep:
    """ 세대를 연속으로 진행시킨다."""

    def __init__(self, cell_controller, eye, count: int = 19):
        self.controller = cell_controller
        self.eye = eye
        self.init_setting()
        self.seq = [Func(self.eye_controll_off), Func(self.show_position_shortcut)]
        self.count = count
        for _ in range(count):
            self.seq.append(1)
            self.seq.append(Func(self.controller.next))
        self.seq.append(Func(self.eye_controll_on))

    def __call__(self):
        """ main execute"""
        self.seq = Sequence(*self.seq)
        self.seq.start()

    def eye_controll_off(self):
        self.eye.position, self.eye.rotation = self.eye.fixed_positions["origin"]
        self.eye.update = lambda: None

    def eye_controll_on(self):
        self.eye.update = self.eye.controller

    def show_position_shortcut(self):

        self.keys_desc.fade_in(duration=2)
        self.keys_img.fade_in(duration=2)

        def delete():
            self.keys_img.fade_out(duration=2)
            self.keys_desc.fade_out(duration=2)
            invoke(destroy, self.keys_img, delay=3)
            invoke(destroy, self.keys_desc, delay=3)

        invoke(delete, delay=10)

    def init_setting(self):
        self.keys_desc = KeyDescription.Position(position=(0.52, 0.35))
        self.keys_img = KeyDescription.PositionImage(scale=0.8, position=(0.5, 0.2))
        self.keys_desc.fade_out(duration=0)
        self.keys_img.fade_out(duration=0)


class Judgment:
    """ 판정자 """

    def __init__(self, cell_controller):
        self.cell_controller = cell_controller

    def update(self):
        if (cc := self.cell_controller).end:
            if cc.cell_monitor:
                # * 정물
                pass
            else:
                # * 멸종
                pass
        elif not cc.cell_monitor.count(1):
            # * 1번(blue) 패배
            pass
        elif not cc.cell_monitor.count(2):
            # * 2번(red) 패배
            pass

    def execute(self):
        self.cell_controller.cell_monitor


def trigger(cell_controller, eye):
    """ 모든 클래스를 이어주는 편의 함수"""
    CountDown(cell_controller, count=10, pipe_func=IterStep(cell_controller, eye))
    CellMonitor(cell_controller)