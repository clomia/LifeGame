""" 카운트다운, 점수판, 게임 로직등에 필요한 ui도구 모듈 | CellController클래스를 다루는 모듈이다."""
from ursina import *
from .origin import *
from .react_map import simul_react_map


class CountDown(UI):
    """ 게임 시작 후 카운트다운"""

    def __init__(
        self,
        cell_controller,
        count: int = 10,
        pipe_func=lambda: print("함수가 실행됩니다"),
        reverse=False,
    ):
        """ 카운트 다운 종료 후의 실행을 pipe_func로 전달해주세요"""
        super().__init__()
        self.cell_controller = cell_controller
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

    def text_setting(self):
        for number in self.numbers:
            text = Text(number, position=UI.Top, scale=self.text_size)
            text.y -= 0.067
            text.x -= 0.0117
            text.fade_out(duration=0)
            yield text

    def update(self):
        """ 세포가 배치되면 카운트다운을 시작하도록 폴링한다."""
        if self.cell_controller.cell_monitor():
            self.update = lambda: None
            invoke(self.run, delay=1)

    def run(self):
        self.action.start()


class CellMonitor(UI):
    def __init__(self, cell_controller):
        """ gen은 제너레이터가 아니라 제너레이션(세대)을 의미한다 """
        super().__init__()
        self.cell_controller = cell_controller
        self.scale_position = {
            "gen": (Vec2(0.3, 0.04), Vec2(UI.Top)),
            "left": (Vec2(0.15, 0.04), Vec2(UI.Top.x - 0.075, UI.Top.y - 0.04)),
            "right": (Vec2(0.15, 0.04), Vec2(UI.Top.x + 0.075, UI.Top.y - 0.04)),
        }
        gen, left, right = self.frame_gen()
        self.gen = Text("1", scale=1.1, y=gen.y + 0.011, x=gen.x - 0.007)
        self.gen.x_origin = self.gen.x
        self.red = Text("0", scale=1, y=left.y + 0.01, x=left.x - 0.007)
        self.red.x_origin = self.red.x
        self.blue = Text("0", scale=1, y=right.y + 0.01, x=right.x - 0.007)
        self.blue.x_origin = self.blue.x
        self.gen.update = self.gen_monitoring
        self.red.update = self.red_monitoring
        self.blue.update = self.blue_monitoring
        self.gen_counter = 0

    def update(self):
        self.gen_monitoring()
        self.red_monitoring()
        self.blue_monitoring()

    def gen_monitoring(self):
        self.gen.text = str(self.cell_controller.generation)
        self.position_maintain(self.gen)

    def blue_monitoring(self):
        self.blue.text = str(self.cell_controller.cell_monitor.count(BLUECELL))
        self.position_maintain(self.blue)

    def red_monitoring(self):
        self.red.text = str(self.cell_controller.cell_monitor.count(REDCELL))
        self.position_maintain(self.red)

    @staticmethod
    def position_maintain(entity: Text):
        """ Text.update로써 중앙정렬을 유지해준다"""
        length = len(entity.text)
        entity.x = entity.x_origin - (length / 156)

    def frame_gen(self):
        gen_bg = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0),
            color=color.rgba(0, 0, 0, 50),
        )
        generation_monitor = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0, mode="line"),
        )
        gen_bg.scale, gen_bg.position = self.scale_position["gen"]
        generation_monitor.scale, generation_monitor.position = self.scale_position["gen"]
        red = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0),
            color=color.rgba(255, 0, 0, 25),
        )
        left = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0, mode="line"),
            scale_x=0.15,
        )
        red.scale, red.position = self.scale_position["left"]
        left.scale, left.position = self.scale_position["left"]
        blue = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0),
            color=color.rgba(0, 0, 255, 25),
        )
        right = Entity(
            parent=self,
            model=Quad(thickness=1.3, segments=0, mode="line"),
        )
        blue.scale, blue.position = self.scale_position["right"]
        right.scale, right.position = self.scale_position["right"]

        return (
            Vec2(generation_monitor.x, generation_monitor.y),
            Vec2(left.x, left.y),
            Vec2(right.x, right.y),
        )


class MoreInfo(UI):
    def __init__(self, result_type):
        super().__init__()
        self._position = Vec2(-0.55, 0.307)
        random_number = random.randint(100_000_000, 1000_000_000)
        random_sign = random.choice(("α", "λ", "δ", "Ω", "Φ"))
        self.frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0),
            scale=(0.5, 0.15),
            position=self._position,
        )
        bottom_y = self._position.y - 0.02
        if LANGUAGE.now == "ko":
            self.top_text = Text(
                text="실험 종료",
                x=self._position.x - 0.04,
                y=self._position.y + 0.05,
                scale=0.9,
            )
            if result_type is EXTINCTION:
                self.bottom_text = Text(
                    text="두 세포 종이 모두 멸종되었습니다.",
                    x=self._position.x - 0.2,
                    y=bottom_y,
                    scale=1.1,
                )
            elif result_type is STILL_LIFE:
                self.bottom_text = Text(
                    text="생명활동이 정지되었습니다.",
                    x=self._position.x - 0.164,
                    y=bottom_y,
                    scale=1.1,
                )
        elif LANGUAGE.now == "en":
            self.top_text = Text(
                text="End Experiment",
                x=self._position.x - 0.09,
                y=self._position.y + 0.05,
                scale=0.9,
            )
            if result_type is EXTINCTION:
                self.bottom_text = Text(
                    text="Both cell species are extinct.",
                    x=self._position.x - 0.195,
                    y=bottom_y,
                    scale=1.1,
                )
            elif result_type is STILL_LIFE:
                self.bottom_text = Text(
                    text="Life phenomenon has been stopped.",
                    x=self._position.x - 0.215,
                    y=bottom_y,
                    scale=0.95,
                )
        self.code_text = Text(
            text=f"Experiment No.{random_number}°inf/{random_sign}",
            x=self._position.x - 0.13,
            y=self._position.y + 0.02,
            scale=0.65,
        )

    def destroy(self):
        destroy(self.frame)
        destroy(self.top_text)
        destroy(self.bottom_text)
        destroy(self.code_text)
        destroy(self)


class ResultPanel(UI):
    def __init__(
        self,
        eye,
        *,
        winner=None,
        more_info=None,
        pipe_func=None,
        after_iter=True,
        bprin_booting_signal_pipe=None,
    ):
        """
        필드에 남기를 선택한 경우 pipe_func를 실행합니다
        after_iter에 False를 넘기면 사후 이터레이션 기능을 제공하지 않습니다
        """
        super().__init__()
        if S_ESC.is_on:
            S_ESC.off()
        self.bprin_booting_signal_pipe = bprin_booting_signal_pipe
        self.winner = winner
        self.after_iter = after_iter
        mouse.locked = False
        self.esc_react = simul_react_map["escape"]
        simul_react_map["escape"] = lambda: None
        self.eye = eye
        self.eye.enabled = False
        self.cursor = GameCursor()
        self.scale = (0.5, 0.2)
        self.inner_color = Entity(
            parent=self,
            model="quad",
        )
        self.model = Quad(
            mode="line",
            radius=0,
            thickness=1,
        )
        if not winner:
            self.inner_color.color = color.rgba(0, 0, 0, 50)
        elif winner == BLUECELL:
            self.inner_color.color = color.rgba(0, 0, 255, 80)
        elif winner == REDCELL:
            self.inner_color.color = color.rgba(255, 0, 0, 80)
        else:
            raise Exception()

        if LANGUAGE.now == "ko":
            if self.winner:
                self.text_entity = Text(text="승리!", x=-0.052, y=0.015, scale=2)
            else:
                self.text_entity = Text(text="무승부", x=-0.073, y=0.015, scale=2)
            self.leave_text = "로비로 돌아가기"
            self.stay_text = "필드에 남기"
        elif LANGUAGE.now == "en":
            if self.winner:
                self.text_entity = Text(text="WIN!", x=-0.052, y=0.015, scale=2)
            else:
                self.text_entity = Text(text="DRAW", x=-0.073, y=0.015, scale=2)
            self.leave_text = "Back to Lobby"
            self.stay_text = "Stay in field"
        self.text_entity.resolution = 100
        self.btn_generator()
        self.more_panel = None
        if more_info:
            self.more_panel = MoreInfo(result_type=more_info)
        self.pipe_func = pipe_func

    def destroy(self):
        destroy(self.inner_color)
        destroy(self.leave_btn)
        destroy(self.stay_btn)
        destroy(self.text_entity)
        if self.more_panel:
            self.more_panel.destroy()
        destroy(self)
        if self.after_iter:
            IterControllerGuide(self.eye, self.esc_react, self.cursor)
            self.pipe_func()
        else:
            self.eye.enabled = True
            mouse.locked = True
            simul_react_map["escape"] = self.esc_react
            destroy(self.cursor)

    def btn_generator(self):
        btn_size = self.scale
        left = self.x - btn_size.x / 4
        right = -left
        y = self.y - btn_size.y / 1.32

        def _btn_gen(*, x, text, on_click):
            class Btn(Button):
                def __init__(self):
                    super().__init__()
                    self.scale = (btn_size.x / 2, btn_size.y / 2)
                    self.x = x
                    self.y = y
                    self.color = color.white
                    self.highlight_color = color.white
                    self.pressed_color = color.white33
                    self.inner_color = Entity(
                        parent=self,
                        model="quad",
                        color=color.rgba(0, 0, 0, 50),
                    )
                    self.model = Quad(mode="line", radius=0)
                    self.on_click = on_click
                    self.text = text

                def on_mouse_enter(self):
                    self.inner_color.color = color.white33

                def on_mouse_exit(self):
                    self.inner_color.color = color.rgba(0, 0, 0, 50)

            return Btn

        self.leave_btn = _btn_gen(
            x=left,
            text=self.leave_text,
            on_click=lambda: print(f"{self.bprin_booting_signal_pipe}에 신호넣기!!!"),
        )()
        self.stay_btn = _btn_gen(x=right, text=self.stay_text, on_click=self.destroy)()


class IterControllerGuide(UI):
    """ ResultPanel과 연결되어 실행되는 클래스"""

    def __init__(self, eye, default_esc, cursor):
        super().__init__()
        if S_ESC.is_on:
            S_ESC.off()
        self.esc_react = default_esc
        self.cursor = cursor
        self.eye = eye
        self.eye.enabled = False
        self.frame_color = Entity(
            parent=self,
            model="quad",
            color=color.black10,
            scale=(0.5, 0.1),
        )
        self.frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0, thickness=1),
            color=color.white,
            scale=(0.5, 0.1),
        )
        self.btn = Button(
            model="quad",
            scale=0.1,
            y=self.frame.y,
            x=self.frame.x + 0.2,
            color=color.black33,
        )

        def _on_mouse_enter():
            self.btn.color = color.white33

        def _on_mouse_exit():
            self.btn.color = color.black33

        self.btn.on_mouse_enter = _on_mouse_enter
        self.btn.on_mouse_exit = _on_mouse_exit
        self.btn.on_click = self.destroy
        self.btn_frame = Entity(
            parent=self,
            model=Quad(radius=0, mode="line"),
            scale=0.1,
            position=self.btn.position,
            z=-0.1,
        )
        self.lang_setting()
        # esc버튼이 잠겨서 update로 동적 언어변경 지원할 필요 없다

    def lang_setting(self):
        if LANGUAGE.now == "ko":
            self.ko_ver()
        elif LANGUAGE.now == "en":
            self.en_ver()

    def ko_ver(self):
        self.text = Text("마우스 우클릭으로 재생/일시정지", x=self.frame.x - 0.23, y=self.frame.y + 0.01)
        self.btn.text = "확인"
        self.now_lang = "ko"

    def en_ver(self):
        self.text = Text(
            "Play/Pause with right mouse click",
            x=self.frame.x - 0.242,
            y=self.frame.y + 0.01,
            scale=0.93,
        )
        self.btn.text = "OK"
        self.now_lang = "en"

    def destroy(self):
        destroy(self.text)
        destroy(self.btn)
        destroy(self.btn_frame)
        destroy(self.frame_color)
        destroy(self.frame)
        destroy(self.cursor)
        self.eye.enabled = True
        mouse.locked = True
        simul_react_map["escape"] = self.esc_react
        destroy(self)


class ExecutionPenal(UI):
    def __init__(self, eye, continue_func, execute_func, player=None, pipe_func=None):
        super().__init__()
        if S_ESC.is_on:
            S_ESC.off()
        self.eye = eye
        self.eye.enabled = False
        mouse.locked = False
        self.cursor = GameCursor()
        self.pipe_func = pipe_func
        self.top_frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0),
            scale=(0.6, 0.1),
            y=0.2,
        )
        self.top_color = Entity(
            parent=self,
            model="quad",
            scale=self.top_frame.scale,
            color=color.black10,
            y=0.2,
        )
        if player:
            if player == BLUECELL:
                self.top_color.color = color.rgba(0, 0, 255, 70)
            elif player == REDCELL:
                self.top_color.color = color.rgba(255, 0, 0, 70)
        self.left_frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0),
            scale=(0.3, 0.2),
            y=0.05,
            x=-0.15,
        )
        self.right_frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0),
            scale=(0.3, 0.2),
            y=0.05,
            x=0.15,
        )

        def _on_mouse_enter(btn):
            def func():
                btn.color = color.white33

            return func

        def _on_mouse_exit(btn):
            def func():
                btn.color = color.black10

            return func

        self.execute_btn = Button(parent=self.left_frame, model="quad", color=color.black10)
        self.continue_btn = Button(parent=self.right_frame, model="quad", color=color.black10)
        self.execute_btn.on_click = lambda: self.destroy() and execute_func()
        self.execute_btn.on_mouse_enter = _on_mouse_enter(self.execute_btn)
        self.execute_btn.on_mouse_exit = _on_mouse_exit(self.execute_btn)
        self.continue_btn.on_click = lambda: self.destroy() and continue_func()
        self.continue_btn.on_mouse_enter = _on_mouse_enter(self.continue_btn)
        self.continue_btn.on_mouse_exit = _on_mouse_exit(self.continue_btn)
        self.lang_setting()

    def destroy(self):
        self.eye.enabled = True
        mouse.locked = True
        destroy(self.cursor)
        destroy(self.top_frame)
        destroy(self.top_color)
        destroy(self.left_frame)
        destroy(self.right_frame)
        destroy(self.top_text)
        for desc in self.top_descs:
            destroy(desc)
        destroy(self.execute_btn)
        destroy(self.continue_btn)
        if self.pipe_func:
            self.pipe_func()
        return True

    def lang_setting(self):
        if LANGUAGE.now == "ko":
            self.ko_ver()
        elif LANGUAGE.now == "en":
            self.en_ver()

    def ko_ver(self):
        self.top_text = Text(
            "선택",
            x=self.top_frame.x - 0.033,
            y=self.top_frame.y + 0.022,
        )
        self.top_descs = [
            Text(
                "집행을 선택하면 다음턴에 세포가 더 많은 쪽이 승리합니다.",
                x=self.top_frame.x - 0.223,
                y=self.top_frame.y - 0.02,
                scale=0.7,
            )
        ]
        self.execute_btn.text = "집행"
        self.continue_btn.text = "패스"

    def en_ver(self):
        self.top_text = Text(
            "Choose",
            x=self.top_frame.x - 0.05,
            y=self.top_frame.y + 0.022,
        )
        self.top_descs = [
            Text(
                "If you choose execute,",
                x=self.top_frame.x - 0.083,
                y=self.top_frame.y - 0.014,
                scale=0.6,
            ),
            Text(
                "on next turn win by the player with more cells.",
                x=self.top_frame.x - 0.176,
                y=self.top_frame.y - 0.028,
                scale=0.6,
            ),
        ]
        self.execute_btn.text = "Execute"
        self.continue_btn.text = "Pass"


class ExecutionWaiter(UI):
    def __init__(self, sec, func):
        """ sec 초 이후 func를 실행합니다"""
        super().__init__()
        self._position = Vec2(UI.Right.x - 0.2, UI.Top.y - 0.2)
        self.frame = Entity(
            parent=self,
            model=Quad(mode="line", radius=0),
            scale=(0.3, 0.1),
            position=self._position,
        )
        self.background_color = Entity(
            parent=self,
            model="quad",
            scale=self.frame.scale,
            color=color.black10,
            position=self._position,
        )
        self.lang_setting()
        self.seq = Sequence()
        for s in range(sec, 0, -1):
            self.seq.append(Func(self.sec_text, s))
            self.seq.append(1)
        self.seq.append(Func(self.sec_text, 0))
        self.seq.append(0.5)
        self.seq.append(Func(self.destroy))
        self.seq.append(Func(func))
        self.seq.start()

    def destroy(self):
        destroy(self.frame)
        destroy(self.background_color)
        destroy(self.desc)
        destroy(self.sec)
        destroy(self)

    def lang_setting(self):
        if LANGUAGE.now == "ko":
            self.desc = Text(
                "선택까지 남은 시간",
                position=(self._position.x - 0.073, self._position.y + 0.03),
                scale=0.7,
            )
            self.sec = Text(
                y=self._position.y - 0.007,
                scale=1,
            )
            self.now_lang = "ko"
        elif LANGUAGE.now == "en":
            self.desc = Text(
                "Time left until select",
                position=(self._position.x - 0.088, self._position.y + 0.03),
                scale=0.7,
            )
            self.sec = Text(
                y=self._position.y - 0.007,
                scale=1,
            )
            self.now_lang = "en"

    def sec_text(self, sec):
        sec_x = self._position.x - 0.03
        if self.now_lang == "ko":
            sec_x += 0.007
            self.sec.text = f"{sec}초"
        elif self.now_lang == "en":
            self.sec.text = f"{sec}sec"
        if len(str(sec)) == 2:
            self.sec.x = sec_x - 0.0025
        else:
            self.sec.x = sec_x
