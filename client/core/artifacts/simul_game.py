""" 주요 게임 로직이다, UI는 simul_ui의 객체들을 사용한다."""
from ursina import *
from .simul_ui import *


def trigger(cell_controller):
    """ 모든 클래스를 이어주는 편의 함수"""
    CellMonitor(cell_controller)
    CountDown(10, pipe_func=IterStep(cell_controller))