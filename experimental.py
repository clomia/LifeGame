from ursina import *

app = Ursina()

# camera.x = 10
def screen_control():
    camera.x += held_keys["d"] * time.dt * 10
    camera.x -= held_keys["a"] * time.dt * 10
    camera.y += held_keys["w"] * time.dt * 10
    camera.y -= held_keys["s"] * time.dt * 10


class CellGrid(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = Grid(1000, 1000)
        self.scale = Vec2(500, 500)
        self.color = color.rgba(255, 255, 255, a=15)

    def update(self):
        screen_control()


EditorCamera(zoom_speed=2)
CellGrid()

app.run()