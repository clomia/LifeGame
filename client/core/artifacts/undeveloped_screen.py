from ursina import *


class BackGround(Entity):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.origin = (-0.5, 0.5)
        self.model = "quad"
        x_ratio, y_ratio = window.screen_resolution
        value = 1 / y_ratio
        self.scale_x = x_ratio * value
        self.scale_y = y_ratio * value
        self.texture = load_texture("source/undeveloped_screen.jpg")


class GoBackBtn(Button):
    def __init__(self, cursor, bg):
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
        destroy(self.background)
        destroy(self)


def undeveloped_window(cursor):
    """ 미개발 안내창을 위 레이어에 띄운다. """
    cursor.rotational_speed = 1
    bg = BackGround()
    GoBackBtn(cursor, bg)


__all__ = ["undeveloped_window"]
if __name__ == "__main__":
    from origin import *

    with bprin(debug=True) as cursor:
        undeveloped_window(cursor)
