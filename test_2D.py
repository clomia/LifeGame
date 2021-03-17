from ursina import *


zone = Entity(parent=camera.ui)
zone.set_scissor(Vec3(-0.5, -0.25, 0), Vec3(0.5, 0.25, 0))

button_parent = Button(
    parent=zone, model="quad", scale=(0.4, 0.8), collider="box", visible_self=False
)

for i in range(8):
    Button(
        parent=button_parent,
        scale_y=0.05,
        text=f"giopwjoigjwr{i}",
        origin_y=0.5,
        y=0.5 - (i * 0.051),
    )

button_parent.add_script(Scrollable(min=-0.15, max=0.125))
