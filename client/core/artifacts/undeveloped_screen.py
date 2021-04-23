from ursina import *
from .origin import *


class BackGround(FullUI):
    def __init__(self):
        super().__init__()
        self.texture = load_texture("source/undeveloped_screen.jpg")


class GoBackBtn(Button):
    def __init__(self, cursor, *bg):
        super().__init__()
        self.background = bg
        self.cursor = cursor
        self.color_origin = color.white
        self.color = self.color_origin
        self.texture = load_texture("source/goback_btn.png")
        self.scale_x = 1.280 / 2.8
        self.scale_y = 0.176 / 2.8
        self.x -= 0.94
        self.y += 0.1
        self.x_origin = self.x
        self.text = "Offline"
        self.text_origin = -1, 0.5

    def showing(self, limit=-0.83):
        if self.x < limit:
            self.x += time.dt * 1

    def hiding(self):
        if self.x > self.x_origin:
            self.x -= time.dt * 1

    def on_mouse_enter(self):
        self.cursor.rotational_speed = 8
        self.update = self.showing
        self.color = color.hex("7effee")

    def on_mouse_exit(self):
        self.cursor.rotational_speed = 1
        self.update = self.hiding
        self.color = self.color_origin

    def on_click(self):
        super().on_click()
        for ele in self.background:
            destroy(ele)
        destroy(self)


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


def undeveloped_window(cursor):
    """ 미개발 안내창을 위 레이어에 띄운다. """
    cursor.rotational_speed = 1
    bg = BackGround()
    _bg = screen_gen()
    GoBackBtn(cursor, bg, _bg)


__all__ = ["undeveloped_window"]
if __name__ == "__main__":
    from origin import *

    with bprin(debug=True) as cursor:
        undeveloped_window(cursor)
