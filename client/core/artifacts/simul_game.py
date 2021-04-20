""" 주요 게임 로직이다, UI는 simul_ui의 객체들을 사용한다."""
from ursina import *
from .origin import GameConfig
from .simul_ui import *


class SelectInfo:
    """ 오프라인 모드일때 두 패널의 정보를 취합-실행하는 객체"""

    def __init__(self, continue_func, execute_func):
        self.now = {
            BLUECELL: None,
            REDCELL: None,
        }
        self.continue_func = continue_func
        self.execute_func = execute_func

    def select(self, cell, value):
        """
        적용한 뒤 검사해서 실행한다.
        execute가 하나라도 있으면 집행을 실행,
        모두 continue일때만 pass.
        """
        if self.now[cell] is None:
            self.now[cell] = value
            state = list(self.now.values())
            if not None in state:
                if True in state:
                    self.execute_func()
                else:
                    self.now[BLUECELL] = None
                    self.now[REDCELL] = None
                    self.continue_func()


class ExcuteStep:
    """ self.select_info 에서 False는 continue, True는 execute를 의미합니다."""

    def __init__(self, eye, cell_controller, referee):
        self.cell_controller = cell_controller
        self.referee = referee
        self.eye = eye
        self.select_info = SelectInfo(continue_func=self._continue, execute_func=self._excute)
        ExecutionWaiter(GameConfig.Execution_Iter_Delay, self.first_panel)

    def _continue(self):
        self.cell_controller.next()

        def check():
            """ 판정객체가 cell_controller에 대해 자동 심판을 할 여유시간을 주기 위함."""
            if not self.cell_controller.judged:
                ExecutionWaiter(GameConfig.Execution_Iter_Delay, self.first_panel)

        invoke(check, delay=0.2)

    def _excute(self):
        self.cell_controller.next()
        self.referee.execute()

    def first_panel(self):
        self.eye.position, self.eye.rotation = self.eye.fixed_positions["center-top"]
        self.esc_func = simul_react_map["escape"]
        simul_react_map["escape"] = lambda: None
        ExecutionPenal(
            self.eye,
            continue_func=self.continue_handler(BLUECELL),
            execute_func=self.execution_handler(BLUECELL),
            player=BLUECELL,
            pipe_func=self.second_panel,
        )

    def second_panel(self):
        def after_clean():
            """ 화면이 흔들리기때문에 눈 위치를 다시 바로잡고, esc패널을 사용가능한 상태로 복구한다"""
            self.eye.position, self.eye.rotation = self.eye.fixed_positions["center-top"]
            simul_react_map["escape"] = self.esc_func

        ExecutionPenal(
            self.eye,
            continue_func=self.continue_handler(REDCELL),
            execute_func=self.execution_handler(REDCELL),
            player=REDCELL,
            pipe_func=after_clean,
        )

    def continue_handler(self, player):
        def func():
            self.select_info.select(player, False)

        return func

    def execution_handler(self, player):
        def func():
            self.select_info.select(player, True)

        return func


class IterStep(Entity):
    """
    세대를 연속으로 진행시킨다.
    정물이나 멸종에 다다르면 멈춘다.
    """

    def __init__(self, cell_controller, eye, referee, count: int = GameConfig.IterStep_Count):
        super().__init__()
        self.controller = cell_controller
        self.referee = referee
        self.eye = eye
        self.init_setting()
        self.seq = [Func(self.eye_controll_off), Func(self.show_position_shortcut)]
        self.count = count
        for _ in range(count):
            self.seq.append(1)
            self.seq.append(Func(self.controller.next))
        self.seq.append(Func(self.eye_controll_on))
        self.seq.append(Func(self.excute_step))

    def excute_step(self):
        if not self.controller.judged:
            ExcuteStep(self.eye, self.controller, self.referee)

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
    기본적으로 초기 이터레이션이 종료 되었을때만 작동합니다.
    absolute=True인 경우 무시하고 반드시 작동합니다.
    """

    def __init__(self, cell_controller, eye, absolute=False):
        super().__init__()
        self.eye = eye
        self.absolute = absolute
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

    def progress(self):
        if not self.playing:
            self.start()
            self.playing = True
        else:
            self.pause()
            self.playing = False

    def input(self, key):
        if not self.absolute:
            if (
                key == "right mouse down"
                and self.controller.generation >= GameConfig.IterStep_Count
            ):
                self.progress()
        else:
            if key == "right mouse down":
                self.progress()


class Judgment(Entity):
    """ 판정자 """

    def __init__(self, cell_controller, eye, bprin_booting_signal_pipe):
        super().__init__()
        self.cell_controller = cell_controller
        self.bprin_booting_signal_pipe = bprin_booting_signal_pipe
        self.eye = eye

    def pipe_func(self):
        IterController(self.cell_controller, self.eye)

    def winner(self, player, info=None, after_iter=True):
        if not self.cell_controller.judged:
            self.cell_controller.judged = True
            ResultPanel(
                self.eye,
                winner=player,
                more_info=info,
                pipe_func=self.pipe_func,
                after_iter=after_iter,
                bprin_booting_signal_pipe=self.bprin_booting_signal_pipe,
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
            self.pipe_func = lambda: IterController(self.cell_controller, self.eye, absolute=True)
            self.execute(info=STILL_LIFE)
        elif field_state["red_empty"] and field_state["blue_empty"]:
            # * 멸종
            self.winner(None, info=EXTINCTION, after_iter=False)
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


def trigger(cell_controller, eye, bprin_booting_signal_pipe):
    """ simul_game 과 simul_ui 를 묶어서 만든 실행자."""
    referee = Judgment(cell_controller, eye, bprin_booting_signal_pipe)
    CountDown(cell_controller, count=10, pipe_func=IterStep(cell_controller, eye, referee))
    CellMonitor(cell_controller)
