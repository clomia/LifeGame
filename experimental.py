from ursina import *

app = Ursina()

Entity(model=Grid(10, 10), scale=Vec2(7, 7))

app.run()