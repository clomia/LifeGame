from ursina import *

if __name__ == "__main__":
    from undeveloped_screen import *
else:
    from .undeveloped_screen import *


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
        self.texture = load_texture("source/home_bg.jpg")


class OfflineBtn(Button):
    def __init__(self, cursor, pipe_func):
        super().__init__()
        self.pipe_func = pipe_func
        self.cursor = cursor
        self.origin_color = color.white
        self.color = self.origin_color
        self.model = "quad"
        self.texture = load_texture("source/btn1.png")
        self.scale /= 5
        self.x += 0.15
        self.text = "Offline"
        self.text_origin = -1, 0.5
        self.show_color = color.hex("697e8f")
        self.hide_color = color.rgba(255, 255, 255, 15)
        self.text_color = self.show_color

    def lazy__init__(self, *other_entities):
        self.other_entities = other_entities

    def on_mouse_enter(self):
        self.color = color.cyan
        self.cursor.rotational_speed = 8
        self.text_color = self.show_color

    def on_mouse_exit(self):
        self.color = self.origin_color
        self.cursor.rotational_speed = 1
        self.text_color = self.hide_color

    def on_click(self):
        self.cursor.rotational_speed = 1
        for entity in self.other_entities:
            destroy(entity)
        destroy(self)
        self.pipe_func()


class OnlineBtn(Button):
    def __init__(self, cursor, pipe_func=None):
        super().__init__()
        self.pipe_func = pipe_func
        self.cursor = cursor
        self.origin_color = color.white
        self.color = self.origin_color
        self.model = "quad"
        self.texture = load_texture("source/btn2.png")
        self.scale /= 5
        self.x -= 0.3
        self.y += 0.25
        self.text = "Online"
        self.text_origin = 1, -0.5
        self.show_color = color.hex("697e8f")
        self.hide_color = color.rgba(255, 255, 255, 15)
        self.text_color = self.show_color

    def lazy__init__(self, *other_entities):
        self.other_entities = other_entities

    def on_mouse_enter(self):
        self.color = color.cyan
        self.cursor.rotational_speed = 8
        self.text_color = self.show_color

    def on_mouse_exit(self):
        self.color = self.origin_color
        self.cursor.rotational_speed = 1
        self.text_color = self.hide_color

    def on_click(self):
        undeveloped_window(self.cursor)
        self.cursor.rotational_speed = 1
        # for entity in self.other_entities:
        #    destroy(entity)
        # destroy(self)
        # pipe_func()


def home_screen(cursor, offline_pipe, online_pipe=None):
    bg = BackGround()
    online_btn = OnlineBtn(cursor, online_pipe)
    offline_btn = OfflineBtn(cursor, offline_pipe)
    online_btn.lazy__init__(bg, offline_btn)
    offline_btn.lazy__init__(bg, online_btn)


__all__ = ["home_screen"]

if __name__ == "__main__":
    from origin import *

    with bprin(debug=True) as cursor:
        home_screen(cursor, lambda: print("click!"), None)
