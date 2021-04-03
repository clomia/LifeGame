""" 컨트롤러, Esc 핸들러,한글 적용된 Text 클래스 등 기본적인 도구 """

from itertools import cycle
from functools import wraps
from contextlib import contextmanager
from ursina import *


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

    def __init__(self, *, speed=12, position: tuple = (0, 0, 0), fav=90, limit=None):
        super().__init__()
        self.limit = limit
        self.speed = speed
        self.sensitivity = 80
        camera.parent = self
        camera.position = position
        camera.rotation = (0, 0, 0)
        camera.fov = fav
        mouse.locked = True

    def update(self):
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


def react_roop(*args):
    """
    함수들을 인자로 받아서 input에 대한 함수실행 루프를 만들어준다

    클로저 공간에서 함수들을 무한 이터레이션 하면서 매번 타겟 키가 눌렸을때마다 순서대로 하나의 함수를 실행한다.

    ---
    input함수는 타겟 키가 눌렸을때 True를 반환하도록 작성하세요
    ---
    """
    func_gen = cycle((func for func in args))

    def decorator(function):
        @wraps(function)
        def wrapper(key):
            if function(key):
                next(func_gen)()

        return wrapper

    return decorator


class Esc:
    mouse_locked = False

    def on():
        if Esc.mouse_locked:
            mouse.locked = False
        shut_down_btn = Button(text="게임 종료", color=color.gray)
        shut_down_btn.on_click = application.quit
        Esc.panel = WindowPanel(
            title="설정",
            content=(shut_down_btn,),
        )

    def off():
        if Esc.mouse_locked:
            mouse.locked = True
        destroy(Esc.panel)

    loop = (on, off)


def esc_handler(mouse_locked=False):
    """
    함수를 호출하면 설정창이 나옵니다.

    커서가 잠겨있는 상태에서 실행될때는 mouse_locked=True를 해주세요
    """
    Esc.mouse_locked = mouse_locked

    @react_roop(*Esc.loop)
    def func(key):
        return True

    func()


@contextmanager
def bprin(*, debug=False):
    """
    준비된 환경을 제공한다.

    core/artifacts 내부에서 디버깅용으로 사용시 True를 받아야 합니다
    """
    app = Ursina()
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