""" 설계 단계에서 사용하는 모듈이다 """

from math import inf, isinf
from itertools import chain
from ursina import *

if __name__ == "__main__":
    from origin import *
else:
    from .origin import *


class InputGrid(Entity):
    """
    설계 단계를 구현한다

    입력이 모두 완료되면 pipe_func에게 값을 전달한다
    """

    def __init__(
        self,
        size: int = 15,
        bg_image: str = f"source/blueprint_bg.jpg",
        pipe_func=lambda x: print(x),
        final_input_count=3,
    ):
        """
        size는 홀수여야 한다
        """
        self.final_input = final_input_count
        super().__init__()
        self.is_complete = False
        self.need_decision = False
        self.pipe_func = pipe_func
        self.bg_image = bg_image
        self.size = size
        self.btn_color = color.rgba(0, 0, 0, 0)
        self.outline = tools.outline
        axis = lambda: chain(range(-(size // 2), 0), range(size // 2 + 1))
        self.grid = {(x, y): self.btn((x, y)) for y in axis() for x in axis()}
        self.scale = 0.4
        self.player_1 = {
            "cell": 1,
            "color": color.rgb(75, 70, 136),
            "color_rgb": (75, 70, 136),
            "hover_color": color.rgb(99, 205, 255),
            "hover_rgb": (99, 205, 255),
        }
        self.player_2 = {
            "cell": 2,
            "color": color.rgb(148, 148, 148),
            "color_rgb": (148, 148, 148),
            "hover_color": color.rgb(255, 199, 224),
            "hover_rgb": (255, 199, 224),
        }
        self.player = self.player_1
        self.info = {}
        self.other_player = lambda: self.player_2 if self.player == self.player_1 else self.player_1
        self.nowlang = None
        if LANGUAGE.now == "ko":
            self.execution_btn, self.continue_btn = self.decision_btn("ko")
        if LANGUAGE.now == "en":
            self.execution_btn, self.continue_btn = self.decision_btn("en")

        self.background()
        self.click_counter = -inf

    def btn(self, co):
        button = Button(parent=self, position=co, scale=1)
        button.color = self.btn_color
        button.is_clicked = False
        self.outline(button, 20)

        def mouse_hover():
            if not button.is_clicked:
                button.color = self.player["hover_color"]

        def mouse_exit():
            if not button.is_clicked:
                button.color = self.btn_color

        def click():
            def progress():
                button.color = self.player["color"]
                button.is_clicked = True
                self.info[co] = self.player["cell"]

            if not button.is_clicked:
                if not self.need_decision:
                    if isinf(self.click_counter):
                        self.need_decision = True
                        progress()
                        player_color = color.rgba(*self.player["hover_rgb"], 40)
                        self.continue_btn.color = player_color
                        self.execution_btn.color = player_color
                        self.player = self.other_player()
                    elif self.click_counter >= self.final_input - 1:
                        progress()
                        destroy(self.bg)
                        destroy(self)
                        self.is_complete = True
                        self.pipe_func(self.info)
                        return
                    else:
                        progress()
                        self.click_counter += 1
                else:
                    player_color = color.rgba(*self.other_player()["hover_rgb"], 80)
                    self.continue_btn.color = player_color
                    self.execution_btn.color = player_color

        button.on_mouse_enter = mouse_hover
        button.on_mouse_exit = mouse_exit
        button.on_click = click
        return button

    def decision_btn(self, lang):
        def mouse_hover(btn):
            def func():
                btn.color = color.rgba(196, 235, 232, 30)

            return func

        def mouse_exit(btn):
            def func():
                btn.color = self.btn_color

            return func

        def submit():
            if self.need_decision:
                destroy(self.execution_btn.text_entity)
                destroy(self.continue_btn.text_entity)
                destroy(self.execution_btn)
                destroy(self.continue_btn)
                self.need_decision = False
                self.click_counter = 0

        def continue_henble():
            if self.need_decision:
                self.execution_btn.color = self.btn_color
                self.continue_btn.color = self.btn_color
                self.need_decision = False

        continue_btn = Button(parent=self, z=-0.01, model="quad")
        execution_btn = Button(parent=self, z=-0.01, model="quad")
        continue_btn.x = self.x + self.size // 4 + 0.75
        continue_btn.y = self.y - self.size // 2 - 1.25
        continue_btn.scale_x = self.size // 2 + 0.5
        continue_btn.scale_y = 1.5
        execution_btn.x = self.x - self.size // 4 - 0.75
        execution_btn.y = self.y - self.size // 2 - 1.25
        execution_btn.scale_x = self.size // 2 + 0.5
        execution_btn.scale_y = 1.5

        def lang_conf(lang=lang):
            if lang == "ko" and self.nowlang != "ko":
                destroy(continue_btn.text_entity)
                destroy(execution_btn.text_entity)
                continue_text_origin = (-self.size / 5.5, self.size / 1.29)
                execution_text_origin = (self.size / 5.5, self.size / 1.29)
                continue_btn.text_entity = Text(
                    text="창조",
                    size=0.035,
                    origin=continue_text_origin,
                    alpha=150,
                )
                execution_btn.text_entity = Text(
                    text="계속",
                    size=0.035,
                    origin=execution_text_origin,
                    alpha=150,
                )
                self.nowlang = "ko"
            elif lang == "en" and self.nowlang != "en":
                destroy(continue_btn.text_entity)
                destroy(execution_btn.text_entity)
                continue_text_origin = (-self.size / 12, self.size / 1.29)
                execution_text_origin = (self.size / 9, self.size / 1.29)
                continue_btn.text_entity = Text(
                    text="continue",
                    size=0.035,
                    origin=continue_text_origin,
                    alpha=150,
                )
                execution_btn.text_entity = Text(
                    text="create",
                    size=0.035,
                    origin=execution_text_origin,
                    alpha=150,
                )
                self.nowlang = "en"

        lang_conf()
        continue_btn.color = self.btn_color
        continue_btn.on_mouse_enter = mouse_hover(continue_btn)
        continue_btn.on_mouse_exit = mouse_exit(continue_btn)
        continue_btn.on_click = continue_henble
        continue_btn.update = lambda: lang_conf(LANGUAGE.now)
        self.outline(continue_btn, 60)

        execution_btn.color = self.btn_color
        execution_btn.on_mouse_enter = mouse_hover(execution_btn)
        execution_btn.on_mouse_exit = mouse_exit(execution_btn)
        execution_btn.on_click = submit
        execution_btn.update = lambda: lang_conf(LANGUAGE.now)
        self.outline(execution_btn, 60)
        return execution_btn, continue_btn

    def background(self):
        self.bg = Entity(
            parent=scene,
            scale_x=3.84 * 5,
            scale_y=2.40 * 5,
            model="quad",
            texture=load_texture(self.bg_image),
        )


class InfoPanel(Entity):
    def __init__(self, xy=(-6.5, 3.5)):
        """
        패널 골격입니다

        아레의 속성으로 위치,투명도를 설정할 수 있습니다.
        self.x
        self.y
        self.outline_opacity
        """
        super().__init__()
        # self.parent = camera.ui
        self.text_opacity = 170
        self.outline_opacity = 60
        self.x, self.y = xy
        self.outline = lambda obj, opacity: Entity(
            parent=obj,
            model=Quad(segments=0, mode="line", thickness=2),
            color=color.rgba(196, 235, 232, opacity),
            z=-0.01,
        )
        self.player_1 = Entity(
            x=self.x,
            y=self.y,
            model="quad",
            scale=0.4,
            color=color.rgb(75, 70, 136),
        )
        self.player_1_number_screen = Entity(
            model="quad",
            scale=(self.player_1.scale_x * 5, self.player_1.scale_y),
            color=color.rgba(0, 0, 0, 0),
            x=self.player_1.x + self.player_1.scale_x * 3,
            y=self.player_1.y,
        )

        self.player_2 = Entity(
            model="quad",
            scale=0.4,
            color=color.rgb(148, 148, 148),
            x=self.player_1.x,
            y=self.player_1.y - self.player_1.scale_y,
        )
        self.player_2_number_screen = Entity(
            model="quad",
            scale=(self.player_2.scale_x * 5, self.player_2.scale_y),
            color=color.rgba(0, 0, 0, 0),
            x=self.player_2.x + self.player_2.scale_x * 3,
            y=self.player_2.y,
        )

        tools.outline(self.player_1, self.outline_opacity)
        tools.outline(self.player_1_number_screen, self.outline_opacity)
        tools.outline(self.player_2, self.outline_opacity)
        tools.outline(self.player_2_number_screen, self.outline_opacity)


class Score(Entity):
    def __init__(self, panel, provider):
        """
        provider.info = { (x,y):cell } 이어야 합니다
        """
        super().__init__()
        self.provider = provider
        self.panel = panel
        self.cell_count = {1: 0, 2: 0}
        self.x_origin = (panel.player_1.x + panel.player_1.scale_x / 3) / 9.67
        self.player = {
            1: Text(
                text="0",
                x=self.x_origin,
                y=panel.player_1.y / 8,
                alpha=panel.text_opacity,
            ),
            2: Text(
                text="0",
                x=self.x_origin,
                y=panel.player_1.y / 9,
                alpha=panel.text_opacity,
            ),
        }

    def number_updater(self, player: int, number: int):
        """ numder을 업데이트하면서 텍스트 정렬을 위해서 x좌표를 수정합니다"""
        number = str(number)
        self.player[player].text = number
        self.player[player].x = self.x_origin - (len(number) / 156 - 1 / 156)

    def update(self):
        self.cell_counter()
        self.number_updater(1, self.cell_count[1])
        self.number_updater(2, self.cell_count[2])
        if self.provider.is_complete:
            destroy(self.player[1])
            destroy(self.player[2])
            destroy(self.panel.player_1)
            destroy(self.panel.player_1_number_screen)
            destroy(self.panel.player_2)
            destroy(self.panel.player_2_number_screen)

    def cell_counter(self):
        cells = list(self.provider.info.values())
        self.cell_count[1] = cells.count(1)
        self.cell_count[2] = cells.count(2)


def score_panel(provider):
    """
    provider는 is_complete 속성을 가지고 있어야 합니다
    기본 is_complete = False 이며 True가 되면 destroy(score number)를 수행합니다
    """
    Score(InfoPanel(), provider)


if __name__ == "__main__":
    from origin.main import artifacts, esc_handler

    with artifacts(debug=True):
        blue_printing = InputGrid()
        score_panel(blue_printing)
        input = esc_handler()