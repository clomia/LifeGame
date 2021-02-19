from ursina import *

app = Ursina()

Button(parent=scene, text="a")


def update():
    print(mouse.position, mouse.point)


Cursor()
mouse.visible = False
app.run()