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
        entity.x = entity.x_origin - (length / 156 - 1 / 156)

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


class ResultPanel(UI):
    def __init__(self, eye, *, winner=None):
        super().__init__()
        self.winner = winner
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
            self.inner_color.color = color.white10
        elif winner == BLUECELL:
            self.inner_color.color = color.rgba(0, 0, 255, 80)
        elif winner == REDCELL:
            self.inner_color.color = color.rgba(255, 0, 0, 80)
        else:
            raise Exception()

        if LANGUAGE.now == "ko":
            self.text_entity = Text(text="승리!", x=-0.052, y=0.015, scale=2)
            self.leave_text = "로비로 돌아가기"
            self.stay_text = "필드에 남기"
        elif LANGUAGE.now == "en":
            self.text_entity = Text(text="WIN!", x=-0.058, y=0.015, scale=2)
            self.leave_text = "Back to Lobby"
            self.stay_text = "Stay in field"
        self.text_entity.resolution = 100
        self.btn_generator()

    def destroy(self):
        destroy(self.inner_color)
        destroy(self.leave_btn)
        destroy(self.stay_btn)
        destroy(self.text_entity)
        destroy(self.cursor)
        mouse.locked = True
        self.eye.enabled = True
        simul_react_map["escape"] = self.esc_react
        destroy(self)

    def btn_generator(self):
        btn_size = Vec2(self.scale_x, self.scale_y)
        left = self.x - btn_size.x / 4
        right = -left
        y = self.y - btn_size.y / 1.32

        def _btn_gen(*, x, text, on_click):
            class Btn(Button):
                def __init__(self):
                    super().__init__()
                    self.model = Quad(mode="line", radius=0)
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
                    self.on_click = on_click
                    self.text = text

                def on_mouse_enter(self):
                    self.inner_color.color = color.white33

                def on_mouse_exit(self):
                    self.inner_color.color = color.rgba(0, 0, 0, 50)

            return Btn

        self.leave_btn = _btn_gen(x=left, text=self.leave_text, on_click=print)()
        self.stay_btn = _btn_gen(x=right, text=self.stay_text, on_click=self.destroy)()