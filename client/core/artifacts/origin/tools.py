from ursina import *

outline = lambda obj, opacity: Entity(
    parent=obj,
    model=Quad(segments=0, mode="line", thickness=2),
    color=color.rgba(196, 235, 232, opacity),
    z=-0.01,
)

SIGNAL = object()