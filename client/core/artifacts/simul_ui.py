""" 카운트다운, 점수판, 게임 로직등에 필요한 ui도구 모듈 | CellController클래스를 다루는 모듈이다."""
from ursina import *
from .origin import *


class CountDown(UI):
    """ 게임 시작 후 카운트다운"""

    def __init__(self, count: int = 10, pipe_func=lambda: print("함수가 실행됩니다"), reverse=False):
        """ 카운트 다운 종료 후의 실행을 pipe_func로 전달해주세요"""
        super().__init__()
        self.text_size = 1.5
        if not reverse:
            self.numbers = [str(count)]
            while count:
                count -= 1
                self.numbers.append(str(count))
        else:
            self.numbers = map(str, range(1, count + 1))
        self.fade_duration = 0.4
        self.action = Sequence(loop=False)
        for text in self.text_setting():
            self.action.append(Func(text.fade_in, duration=self.fade_duration))
            self.action.append(self.fade_duration)
            self.action.append(1 - 2 * self.fade_duration)
            self.action.append(Func(text.fade_out, duration=self.fade_duration))
            self.action.append(self.fade_duration)
            self.action.append(Func(destroy, text))
        self.action.append(Func(pipe_func))
        self.action.start()

    def text_setting(self):
        for number in self.numbers:
            text = Text(number, position=UI.Top, scale=self.text_size)
            text.fade_out(duration=0)
            yield text


class IterStep:
    """ 10세대를 한번에 진행시키는 게임step을 보여주면서 UI 표시"""

    def __init__(self, cell_controller, count: int = 10):
        self.controller = cell_controller
        self.seq = []
        self.count = count
        for _ in range(count):
            self.seq.append(1)
            self.seq.append(Func(self.controller.next))

    def __call__(self):
        """ main execute"""
        self.seq = Sequence(*self.seq)
        self.seq.start()


class CellMonitor(UI):
    def __init__(self, cell_controller):
        self.cells = cell_controller
        self.previous_field = {}

    def update(self):
        if self.cells.field != self.previous_field:
            pass