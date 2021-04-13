""" 카운트다운, 점수판, 게임 로직등에 필요한 ui도구 모듈 | CellController클래스를 다루는 모듈이다."""
from ursina import *


class BasicText:
    """ 간편 텍스트 컨트롤러 (정해진 위치,모양,색)"""


class BasicUI:
    """ 좌상단 점수판 등등"""


class CountDown:
    """ 게임 시작 후 카운트다운"""


class IterStep:
    """ 10세대를 한번에 진행시키는 게임step"""


def trigger(pipe_queue):
    """ 모든 클래스를 이어주는 편의 함수"""


if __name__ == "__main__":
    from origin import *

    with simul():
        BasicText("안녕")
        trigger()