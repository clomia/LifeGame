""" 컨트롤러, Esc 핸들러,한글 적용된 Text 클래스 등 기본적인 도구 """

from itertools import cycle
from functools import wraps
from contextlib import contextmanager
from ursina import *
from .setting import *
from .tools import *


def source_path(*, unix=False):
    """ source 디렉토리 절대경로를 리턴한다 """
    root_dir = os.getcwd()
    for (root, dirs, _) in os.walk(root_dir):
        if "source" in dirs:
            if not unix:
                return f"{root}/source"
            else:
                return f"/c{root[2:]}/source"


class GameCursor(Cursor):
    """ 전용 커스텀 커서 """

    def __init__(self, png_path="source/cursor.png", rotational_speed=1):
        super().__init__(texture=load_texture(png_path))
        self.rotational_speed = rotational_speed
        self.scale = 0.025
        mouse.visible = False

    def update(self):
        super().update()
        self.rotation_z += self.rotational_speed * time.dt * 180


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
        self.origin_position = Vec3(5.438, 8.38817, -5.45506)
        self.origin_rotation = Vec3(53.9495, 676.621, 0)
        self.position = self.origin_position
        self.rotation = self.origin_rotation

    def update(self):
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
        if key == "backspace":
            self.position = self.origin_position
            self.rotation = self.origin_rotation
        # if key == "p":
        # 위치,각도 캡쳐용
        #    print(f"position={self.position}\nrotation={self.rotation}")


def react_roop(*args):
    """
    함수들을 인자로 받아서 input에 대한 함수실행 루프를 만들어준다

    ---
    예시
    ---
    @react_roop(func1,func2,func3,func4)\n
    def space_react():
        pass

    def input():
        if key=='space':
            space_react()

    위와같이 구현하세요. (func1,func2,func3,func4)들이 cycle을 돌면서 space_react를 호출할때마다 하나씩 실행됩니다.
    """
    func_gen = cycle((func for func in args))

    def decorator(function):
        @wraps(function)
        def wrapper():
            next(func_gen)()

        return wrapper

    return decorator


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

        @react_roop(self.on, self.off)  # todo 이 사이에 다른 화면 삽입 가능
        def handler():
            pass

        if LANGUAGE.now == "ko":
            self.title = "설정"
        elif LANGUAGE.now == "en":
            self.title = "Setting"

        self.handler = handler

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

    def off(self):
        if self.mouse_locked:
            mouse.locked = True
            destroy(self.cursor)
        for stuff in self.esc_stuff:
            destroy(stuff)

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
                invoke(self.on, delay=0.1)  # 다른 변경사항이 덮어쓰이지 않도록 하는 조치
                # self.on()

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


@contextmanager
def bprin(*, debug=False):
    """
    준비된 환경을 제공한다.

    core/artifacts 내부에서 디버깅용으로 사용시 True를 받아야 합니다
    """
    app = Ursina()
    application.development_mode = False
    cursor = GameCursor()
    window.title = "Clomia Life Game"
    window.fullscreen = True
    window.cog_button.visible = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False
    if debug:
        Text.default_font = "source/main_font.ttf"
    else:
        Text.default_font = "core/artifacts/source/main_font.ttf"
    try:
        yield cursor
    finally:
        app.run()


@contextmanager
def simul(*, debug=False):
    """
    3D 시뮬레이션 단계에서 사용하는 컨텍스트 구문이다

    """
    app = Ursina()
    application.development_mode = False
    window.title = "Clomia 3D Loader"
    window.fullscreen = True
    window.cog_button.visible = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False
    if debug:
        Text.default_font = "source/main_font.ttf"
    else:
        Text.default_font = "core/artifacts/source/main_font.ttf"
    try:
        yield
    finally:
        app.run()


class ColorSet:
    """
    주로 사용되는 color 인스턴스들을 정의해두는 곳

    단일 인스턴스 = Snake Case 로 표기
    colorize인자 dict = Camel Case 로 표기 (** 언패킹으로 사용하기)
    """

    redCell = {
        "down": color.magenta,
        "up": color.peach,
        "left": color.peach,
        "right": color.magenta,
        "back": color.yellow,
        "forward": color.blue,
    }
    redCell = {}

    outline = color.rgba(196, 235, 232, 30)
    background = color.rgb(45, 18, 35)
    player_1 = color.rgb(75, 70, 136)
    player_1_light = color.rgb(99, 205, 255)
    player_2 = color.rgb(148, 148, 148)
    player_2_light = color.rgb(255, 199, 224)


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