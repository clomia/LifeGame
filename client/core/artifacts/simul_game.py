""" 주요 게임 로직이다, UI는 simul_ui의 객체들을 사용한다."""
from ursina import *
from .simul_ui import *


class Judgment:
    """ 판정자 """

    def __init__(self, cell_controller):
        pass


def trigger(cell_controller, eye):
    """ 모든 클래스를 이어주는 편의 함수"""
    CountDown(cell_controller, count=10, pipe_func=IterStep(cell_controller, eye))
    CellMonitor(cell_controller)