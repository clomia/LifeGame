""" 주요 게임 로직이다, UI는 simul_ui의 객체들을 사용한다."""
from ursina import *
from .origin import GameConfig
from .simul_ui import *


class IterStep(Entity):
    """
    세대를 연속으로 진행시킨다.
    정물이나 멸종에 다다르면 멈춘다.
    """

    def __init__(self, cell_controller, eye, count: int = GameConfig.IterStep_Count):
        super().__init__()
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
        self.update = self.end_check

    def end_check(self):
        if self.controller.end:
            self.seq.kill()
            self.eye_controll_on()
            destroy(self)

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


class IterController(Entity):
    """
    게임이 끝난 후 필드를 둘러볼때 실행되는 컨트롤러입니다.
    마우스 우클릭을 통해 재생,일시정지를 지원합니다.
    """

    def __init__(self, cell_controller, eye):
        super().__init__()
        self.eye = eye
        self.controller = cell_controller
        self.playing = False
        self.seq = Sequence(Func(self.controller.next), 1, loop=True)

    def start(self):
        # self.eye.position, self.eye.rotation = self.eye.fixed_positions["origin"]
        self.eye.update = lambda: None
        self.seq.start()

    def pause(self):
        self.eye.update = self.eye.controller
        self.seq.pause()

    def input(self, key):
        if key == "right mouse down" and self.controller.generation >= GameConfig.IterStep_Count:
            if not self.playing:
                self.start()
                self.playing = True
            else:
                self.pause()
                self.playing = False


class Judgment(Entity):
    """ 판정자 """

    def __init__(self, cell_controller, eye):
        super().__init__()
        self.cell_controller = cell_controller
        self.eye = eye

    def winner(self, player, info=None):
        ResultPanel(
            self.eye,
            winner=player,
            more_info=info,
            pipe_func=lambda: IterController(self.cell_controller, self.eye),
        )
        self.update = lambda: None

    def update(self):
        """ 세포가 배치되면 CellController를 주시하기 시작한다."""
        if self.cell_controller.cell_monitor():
            self.update = self.main

    def main(self):
        cc = self.cell_controller
        field_state = {
            "still_life": cc.end and cc.cell_monitor(),
            "red_empty": not cc.cell_monitor.count(REDCELL),
            "blue_empty": not cc.cell_monitor.count(BLUECELL),
        }
        if field_state["still_life"]:
            # * 정물
            self.execute(info=STILL_LIFE)
        elif field_state["red_empty"] and field_state["blue_empty"]:
            # * 멸종
            self.winner(None, info=EXTINCTION)
        elif field_state["red_empty"]:
            self.winner(BLUECELL)
        elif field_state["blue_empty"]:
            self.winner(REDCELL)

    def execute(self, info=None):
        if (counter := self.cell_controller.cell_monitor.counter)[BLUECELL] > counter[REDCELL]:
            self.winner(BLUECELL, info)
        elif counter[BLUECELL] < counter[REDCELL]:
            self.winner(REDCELL, info)
        else:
            self.winner(None, info)


def trigger(cell_controller, eye):
    """ 모든 클래스를 이어주는 편의 함수"""
    CountDown(cell_controller, count=10, pipe_func=IterStep(cell_controller, eye))
    CellMonitor(cell_controller)
    Judgment(cell_controller, eye)
