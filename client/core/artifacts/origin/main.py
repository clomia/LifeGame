""" 
컨트롤러, Esc 핸들러,한글 적용된 Text 클래스 등 기본적인 도구
"""
from contextlib import contextmanager
from ursina import *
from .setting import *
from .tools import *


class Eye(Entity):
    """
    공간을 둘러보기 위한 컨트롤러. player라고 봐도 무방하다.
    limit 인자로 공간 크기 단위값을 주면 그 안에 가둔다.

    ---
    생성하기 전에 커서를 보이지 않게 해주세요
    ---
    """

    def __init__(self, *, speed=4, fav=90, limit=None, **kwargs):
        super().__init__(**kwargs)
        self.limit = limit
        self.origin_speed = self.speed = speed
        self.sensitivity = 80
        camera.rotation = (0, 0, 0)
        camera.position = (0, 0, 0)
        camera.parent = self
        camera.fov = fav
        mouse.locked = True
        self.fast_speed = self.speed * 6
        self.fixed_positions = {  # x,y,z :position , rotation
            "origin": (Vec3(4.8953, 4.06675, -3.83887), Vec3(-318.219, -1852.87, 0)),
            "center": (Vec3(0, 0, 0), Vec3(0, 0, 0)),
            "center-top": (Vec3(4.15159, 9.707, -0.0154717), Vec3(70.0086, -1169.88, 0)),
            "center-bottom-center": (Vec3(8.85013, 1.31621, 0.0560277), Vec3(3.73638, -1889.11, 0)),
            "left-bottom-default": (Vec3(6.1342, 5.44779, -5.43013), Vec3(-678.071, -5447.75, 0)),
            "right-bottom-default": (Vec3(5.75278, 5.4826, 5.44936), Vec3(-317, -2652.83, 0)),
            "left-top-default": (Vec3(-5.79788, 5.54591, -5.0487), Vec3(-677.139, -5712.55, 0)),
            "right-top-default": (Vec3(-5.24484, 5.41471, 6.26402), Vec3(-677.55, -5621.68, 0)),
        }
        self.position, self.rotation = self.fixed_positions["origin"]
        self.update = self.controller

    def controller(self):
        self.y += held_keys["space"] * time.dt * self.speed
        self.y -= held_keys["alt"] * time.dt * self.speed
        self.rotation_y += mouse.velocity[0] * self.sensitivity
        self.rotation_x -= mouse.velocity[1] * self.sensitivity
        self.direction = Vec3(
            self.forward * (held_keys["w"] - held_keys["s"])
            + self.right * (held_keys["d"] - held_keys["a"])
        ).normalized()
        self.position += self.direction * self.speed * time.dt
        if self.limit:
            self.x = clamp(self.x, -self.limit / 2 + 2, self.limit / 2 - 2)
            self.y = clamp(self.y, -self.limit / 2 + 2, self.limit / 2 - 2)
            self.z = clamp(self.z, -self.limit / 2 + 2, self.limit / 2 - 2)

    def input(self, key):
        if key == "left mouse down":
            self.speed = self.fast_speed
        if key == "left mouse up":
            self.speed = self.origin_speed
        # if key == "p":
        # 위치,각도 캡쳐용
        # print(f"position={self.position}\nrotation={self.rotation}")
        if key == "backspace":
            self.position, self.rotation = self.fixed_positions["origin"]
        if key == "0":
            self.position, self.rotation = self.fixed_positions["center"]
        if key == "1":
            self.position, self.rotation = self.fixed_positions["center-top"]
        if key == "2":
            self.position, self.rotation = self.fixed_positions["center-bottom-center"]
        if key == "3":
            self.position, self.rotation = self.fixed_positions["left-bottom-default"]
        if key == "4":
            self.position, self.rotation = self.fixed_positions["right-bottom-default"]
        if key == "5":
            self.position, self.rotation = self.fixed_positions["right-top-default"]
        if key == "6":
            self.position, self.rotation = self.fixed_positions["left-top-default"]


class EscBg(FullUI):
    def __init__(self):
        super().__init__()
        self.texture = load_texture("source/esc_bg.jpg")
        self.alpha = 249


def lang_setting(self):
    if LANGUAGE.now == "ko":
        self.ko_ver()
    elif LANGUAGE.now == "en":
        self.en_ver()


class LangBtnText(Text):
    def __init__(self):
        super().__init__()
        self.y = 0.05
        self.color = ColorSet.Esc["Text"]
        lang_setting(self)

    def ko_ver(self):
        self.text = "언어 설정"
        self.x = -0.735

    def en_ver(self):
        self.text = "Language setting"
        self.x = -0.8


class EnBtn(Button):
    def __init__(self, text_entities, panel):
        super().__init__()
        self.panel = panel
        self.text_entities = text_entities
        self.color = color.gray
        self.y = -0.02
        self.x = -0.686
        self.scale_x = 0.25
        self.scale_y = 0.05
        self.model = Quad(thickness=1.3, segments=0, mode="line")
        self.text = "English"
        self.text_color = ColorSet.Esc["Text"]
        self.highlight_color = color.white
        self.pressed_color = color.black66

    def on_click(self):
        if LANGUAGE.now != "en":
            LANGUAGE.setting("en")
            for t in self.text_entities:
                t.en_ver()
            self.panel.off()


class KoBtn(EnBtn):
    def __init__(self, text_entities, panel):
        super().__init__(text_entities, panel)
        self.y = -0.073
        self.x = -0.686
        self.text = "한국어"

    def on_click(self):
        if LANGUAGE.now != "ko":
            LANGUAGE.setting("ko")
            for t in self.text_entities:
                t.ko_ver()
            self.panel.off()


class KeyDescription:
    class Move(Text):
        def __init__(self):
            super().__init__()
            self.x = -0.8
            self.y = 0.32
            self.color = ColorSet.Esc["Text"]
            lang_setting(self)

        def ko_ver(self):
            self.text = dedent(
                """
                    [마우스 좌클릭] 가속
                    [w] 앞으로 이동
                    [a] 왼쪽으로 이동
                    [s] 뒤로 이동
                    [d] 오른쪽으로 이동
                    [alt] 하강
                    [space] 상승
                    """
            ).strip()

        def en_ver(self):
            self.text = dedent(
                """
                    [left click] Accelerate
                    [w] Move Front
                    [a] Move Left
                    [s] Move Back
                    [d] Move Right
                    [alt] Move Down
                    [space] Move Up
                    """
            ).strip()

    class Position(Text):
        def __init__(self, position=(0.47, 0.32)):
            super().__init__()
            self.position = position
            self.color = color.light_gray  # ColorSet.Esc["Text"]
            lang_setting(self)

        def ko_ver(self):
            self.text = "위치 단축키"

        def en_ver(self):
            self.text = "Position shortcut"

    class PositionImage(UI):
        def __init__(self, position=(0.45, 0.15), scale=1):
            """ text속성이 없습니다"""
            super().__init__()
            self.position = position
            self.scale = tuple(scale * i for i in (0.4, 0.375))
            self.model = "quad"
            self.texture = load_texture("source/position_key.png")


class ShutDownBtn(Button):
    def __init__(self):
        super().__init__()
        self.color = color.gray
        self.y = -0.4
        self.scale_x = 0.4
        self.scale_y = 0.05
        self.model = Quad(thickness=1.3, segments=0, mode="line")
        self.highlight_color = color.white
        self.pressed_color = color.black66
        self.on_click = application.quit
        lang_setting(self)
        self.text_color = ColorSet.Esc["Text"]
        self.text_entity.y -= 0.04

    def ko_ver(self):
        self.text = "게임 종료"

    def en_ver(self):
        self.text = "Game Exit"


class LeaveBtn(ShutDownBtn):
    def __init__(self):
        super().__init__()
        self.y = -0.33
        self.on_click = application.quit

    def ko_ver(self):
        self.text = "로비로 돌아가기"

    def en_ver(self):
        self.text = "Return to the lobby"


class Esc:
    """
    커서가 잠겨있는 상태(3D환경) 에는 simul=True를 해주세요

    ---
    Esc패널 리펙토링 시 주의사항
    ---
    모든 요소는 클래스로 정의된것을 사용해야 한다.

    동적 언어 설정을 위해서 text속성을 사용하는 모든 entity는 ko_ver,en_ver 함수를 가지고 있어야 하며
    이 함수가 실행되면 언어에 맞게 객체가 변경되어야 한다.

    또한 Text.text에 태그를 사용하면 레이어 버그가 발생하므로 사용하지 않도록 한다.
    """

    def __init__(self, simul=False):
        """
        simul = True 이면 simul , False이면 bprin으로 간주하고 작동합니다.
        """
        self.mouse_locked = simul
        self.ele_lst = [EscBg, KeyDescription.PositionImage]  # 동적 번역이 불필요한 객체들입니다.
        self.other_trans_lst = []  # 상속,변경시 동적 번역이 필요한 객체를 여기에 추가하세요
        if simul:
            self.other_trans_lst.append(LeaveBtn)
        self.first_call = True
        self.is_on = False

    def create(self):
        """ 모든 객체를 생성,준비시킨다."""

        def disabled(class_or_ins):
            if isinstance(class_or_ins, type):
                entity = class_or_ins()
            else:
                entity = class_or_ins
            entity.disable()
            return entity

        need_trans_lst = [
            LangBtnText(),
            KeyDescription.Move(),
            ShutDownBtn(),
            KeyDescription.Position(),
            *[cls() for cls in self.other_trans_lst],
        ]
        self.ele_lst.extend(
            (
                *(disabled(entity) for entity in self.ele_lst),
                *(disabled(entity) for entity in need_trans_lst),
                *(EnBtn(need_trans_lst, self), KoBtn(need_trans_lst, self)),
            )
        )

    @contextmanager
    def on_setting(self):
        if self.mouse_locked:
            mouse.locked = False
            self.cursor = GameCursor()
        if self.first_call:
            self.create()
            self.first_call = False
        try:
            yield
        finally:
            self.bg = self.screen_gen()
            self.is_on = True

    @contextmanager
    def off_setting(self):
        if self.mouse_locked:
            mouse.locked = True
            destroy(self.cursor)
        try:
            yield
        finally:
            destroy(self.bg)
            self.is_on = False

    @staticmethod
    def screen_gen():
        """
        다른 버튼의 클릭을 막는 투명판 , 가장 마지막에 호출되어야 한다.
        이것은 클래스를 호출하는것으로 생성한뒤 할당해야 의도대로 위치하게 된다.
        또한 가장 나중에 만들어져야지 가장 밑에 깔려서 의도대로 작동하게 된다.
        """
        screen = Button(
            parent=camera.ui,
            model=Quad(scale=(10, 10), thickness=3, segments=0),
            color=color.rgba(255, 255, 255, 0),
        )
        screen.highlight_color = screen.color
        screen.pressed_color = screen.color
        return screen

    def handler(self):
        """ escape키 입력에 반응하는 함수"""
        if self.is_on:
            self.off()
        else:
            self.on()

    def on(self):
        with self.on_setting():
            for entity in self.ele_lst:
                entity.enabled = True

    def off(self):
        with self.off_setting():
            for entity in self.ele_lst:
                entity.enabled = False


if __name__ == "__main__":
    from ursina import *

    app = Ursina()

    @react_roop(lambda: print("1하나"), lambda: print("2둘!!"))
    def func():
        pass

    def input(key):
        if key == "escape":
            func()

    app.run()