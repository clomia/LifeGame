from itertools import cycle
from functools import wraps
from contextlib import contextmanager
from ursina import *


outline = lambda obj, opacity: Entity(
    parent=obj,
    model=Quad(segments=0, mode="line", thickness=2),
    color=color.rgba(196, 235, 232, opacity),
    z=-0.01,
)

SIGNAL = object()


class UI(Entity):
    """ 화면에 고정된 Entity(->UI)를 만들기 위한 부모클래스"""

    Center = Vec2(0, 0)
    Top = Vec2(0, 0.437)
    Bottom = Vec2(0, -0.437)
    Left = Vec2(-0.83, 0)
    Right = Vec2(0.795, 0)
    Top_Right = Vec2(0.795, 0.437)
    Top_Left = Vec2(-0.83, 0.437)
    Bottom_Right = Vec2(0.795, -0.437)
    Bottom_Left = Vec2(-0.83, -0.437)

    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.origin = (-0.5, 0.5)


class FullUI(UI):
    """
    화면을 가득 채우는 UI를 만들기 위한 부모클래스
    ESC패널과 연관되는 모든곳에서는 알수없는 레이어 중첩 문제로 인해 사용하지 않는다.
    """

    def __init__(self):
        super().__init__()
        self.model = "quad"
        x_ratio, y_ratio = window.screen_resolution
        value = 1 / y_ratio
        self.scale_x = x_ratio * value
        self.scale_y = y_ratio * value


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


def source_path(*, unix=False):
    """ source 디렉토리 절대경로를 리턴한다 """
    root_dir = os.getcwd()
    for (root, dirs, _) in os.walk(root_dir):
        if "source" in dirs:
            if not unix:
                return f"{root}/source"
            else:
                return f"/c{root[2:]}/source"


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