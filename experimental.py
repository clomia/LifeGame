from ursina import *

app = Ursina()


# camera.x = 10


class Cell(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = Grid(10, 10)
        self.scale = Vec2(0.7, 0.7)

    def update(self):
        print(mouse.point)


Cell()

app.run()