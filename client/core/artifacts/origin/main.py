""" 컨트롤러, Esc 핸들러,한글 적용된 Text 클래스 등 기본적인 도구 """
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
            self.position, self.rotation = self.fixed_positions["left-top-default"]
        if key == "6":
            self.position, self.rotation = self.fixed_positions["right-top-default"]


class EscBg(FullUI):
    def __init__(self):
        super().__init__()
        self.texture = load_texture("source/esc_bg.jpg")
        self.alpha = 249


class Esc:
    """ 커서가 잠겨있는 상태(3D환경) 에는 mouse_locked=True를 해주세요"""

    def __init__(self, mouse_locked=False):
        """
        mouse_locked = True 이면 simul , False이면 bprin으로 간주하고 작동합니다.

        invoke_time에 숫자를 입력하면 인스턴스 생성 후 해당 초 이후에 활성화됩니다.
        이것은 처음에만 적용됩니다.
        """

        self.mouse_locked = mouse_locked
        self.esc_stuff = []
        if LANGUAGE.now == "ko":
            self.title = "설정"
        elif LANGUAGE.now == "en":
            self.title = "Setting"

        self.ON = False

    def handler(self):
        if self.ON:
            self.off()
        else:
            self.on()

    @contextmanager
    def on_bg(self):
        """ursina특성상, 시각정보는 새로 만들어진 레이어가 위로,
        버튼 이벤트 핸들러는 새로 만들어진 레이어가 아레로 쌓인다
        위와 같은 레이어 반전때문에 증폭된 복잡도를 상쇄하는 함수이다."""
        self.esc_stuff.append(EscBg())
        try:
            yield
        finally:
            self.esc_stuff.append(self.screen_gen())

    def on(self):
        if self.mouse_locked:
            mouse.locked = False
            self.cursor = GameCursor()
        with self.on_bg():
            self.esc_stuff.append(self.shut_down_btn_gen())
            self.esc_stuff.append(self.key_description_gen())
            self.esc_stuff.append(self.main_gen())  # todo main_gen->아직None반환
            self.esc_stuff.extend(self.lang_btn_gen())
        self.ON = True

    def off(self):
        if self.mouse_locked:
            mouse.locked = True
            destroy(self.cursor)
        for stuff in self.esc_stuff:
            destroy(stuff)
        self.ON = False

    def main_gen(self):
        return

    @staticmethod
    def screen_gen():
        """ 다른 버튼의 클릭을 막는 투명판 , 가장 마지막에 호출되어야 한다. """
        screen = Button(
            parent=camera.ui,
            model=Quad(scale=(10, 10), thickness=3, segments=0),
            color=color.rgba(255, 255, 255, 0),
        )
        screen.highlight_color = screen.color
        screen.pressed_color = screen.color
        return screen

    @staticmethod
    def shut_down_btn_gen():
        if LANGUAGE.now == "ko":
            exit_text = "게임 종료"
        elif LANGUAGE.now == "en":
            exit_text = "Game Exit"
        btn = Button(
            text=exit_text,
            color=color.gray,
            y=-0.4,
            scale_x=0.4,
            scale_y=0.05,
            model=Quad(thickness=1.3, segments=0, mode="line"),
        )
        btn.highlight_color = color.white
        btn.pressed_color = color.black66
        btn.on_click = application.quit
        return btn

    def lang_btn_gen(self):
        if LANGUAGE.now == "ko":
            descr = "언어 설정"
            position_x = -0.735
        elif LANGUAGE.now == "en":
            descr = "Language setting"
            position_x = -0.8
        text = Text(descr, x=position_x, y=0.05)
        en_btn = Button(
            text="English",
            color=color.gray,
            y=-0.02,
            x=-0.686,  # 위치 변경 주의
            scale_x=0.25,
            scale_y=0.05,
            model=Quad(thickness=1.3, segments=0, mode="line"),
        )
        ko_btn = Button(
            text="한국어",
            color=color.gray,
            y=-0.073,
            x=-0.686,  # 위치 변경 주의
            scale_x=0.25,
            scale_y=0.05,
            model=Quad(thickness=1.3, segments=0, mode="line"),
        )

        def event(lang: str):
            if LANGUAGE.now != lang:
                LANGUAGE.setting(lang)
                self.off()

        en_btn.highlight_color = color.white
        en_btn.pressed_color = color.black66
        ko_btn.highlight_color = color.white
        ko_btn.pressed_color = color.black66
        en_btn.on_click = lambda: event("en")
        ko_btn.on_click = lambda: event("ko")
        return (text, en_btn, ko_btn)

    @staticmethod
    def key_description_gen():
        if LANGUAGE.now == "ko":
            description = dedent(
                """
                <white>[마우스 좌클릭] <light_gray>가속
                <white>[w] <light_gray>앞으로 이동
                <white>[a] <light_gray>왼쪽으로 이동
                <white>[s] <light_gray>뒤로 이동
                <white>[d] <light_gray>오른쪽으로 이동
                <white>[alt] <light_gray>하강
                <white>[space] <light_gray>상승
                """
            ).strip()
            return Text(description, x=-0.8, y=0.3)
        elif LANGUAGE.now == "en":
            description = dedent(
                """
                <white>[left click] <light_gray>Accelerate
                <white>[w] <light_gray>Move Front
                <white>[a] <light_gray>Move Left
                <white>[s] <light_gray>Move Back
                <white>[d] <light_gray>Move Right
                <white>[alt] <light_gray>Move Down
                <white>[space] <light_gray>Move Up
                """
            ).strip()
            return Text(description, x=-0.8, y=0.3)


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