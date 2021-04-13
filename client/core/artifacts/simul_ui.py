""" 카운트다운, 점수판, 게임 로직등에 필요한 ui도구 모듈 | CellController클래스를 다루는 모듈이다."""
from ursina import *
from .origin import *


class BasicText(UI):
    """ 간편 텍스트 컨트롤러 (정해진 위치,모양,색)"""

    def __init__(self, string, *arg):
        super().__init__()
        Text(string)


class BasicUI:
    """ 좌상단 점수판 등등"""


class CountDown(UI):
    """ 게임 시작 후 카운트다운"""

    def __init__(self, count: int = 10, pipe_func=lambda: print("함수가 실행됩니다")):
        """ 카운트 다운 종료 후의 실행을 pipe_func로 전달해주세요"""
        super().__init__()
        self.text_size = 1.5
        self.numbers = [str(count)]
        while count:
            count -= 1
            self.numbers.append(str(count))
        self.fade_duration = 0.4
        self.action = Sequence(loop=False)
        for text in self.fade_setting():
            self.action.append(Func(text.fade_in, duration=self.fade_duration))
            self.action.append(self.fade_duration)
            self.action.append(1 - 2 * self.fade_duration)
            self.action.append(Func(text.fade_out, duration=self.fade_duration))
            self.action.append(self.fade_duration)
            self.action.append(Func(destroy, text))
        self.action.append(Func(pipe_func))
        self.action.start()

    def fade_setting(self):
        for number in self.numbers:
            text = Text(number, position=UI.Top, scale=self.text_size)
            text.fade_out(duration=0)
            yield text


class IterStep:
    """ 10세대를 한번에 진행시키는 게임step"""


def trigger(pipe_queue):
    """ 모든 클래스를 이어주는 편의 함수"""
