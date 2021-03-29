from typing import Tuple, Union
from ursina import *

Co = Union[Tuple[int, int, int], Tuple[int, int]]


class CellControllException(Exception):
    pass


class CellController(Entity):
    """ 유의: 외부에서 cell이라고 부르는 숫자를 여기서는 number라고 부른다. """

    def __init__(self, finite_space_size=101):
        super().__init__()
        self.space_size = finite_space_size
        self.cell_scale = 0.5
        self.cell_cubic_thickness = 1.15
        self.scale = finite_space_size * self.cell_scale
        self.cubic(self, color.white10, thickness=1.5, segments=0)
        self.field = {}

    def __call__(self, space_dict):
        """
        좌표,number쌍이 들어있는 delta_dict를 입력받아서 세포들을 전개시킨다.
        0=delete
        1=blue_cell
        2=red_cell
        """
        for co, number in space_dict.items():
            co = self.co_convert(co)
            if not number:
                destroy(self.field[co])
                del self.field[co]
            elif number == 1:
                self.blue_cell(co)
            elif number == 2:
                self.red_cell(co)
            else:
                CellControllException("세포값이 잘못되었습니다")

    def red_cell(self, co):
        cell = Entity(
            model="sphere",
            texture=load_texture("source/red.jpg"),
            scale=self.cell_scale,
            position=co,
        )
        self.fixed_cubic(cell, color.hex("aefff1"), self.cell_cubic_thickness)
        cell.rotation_z = -90
        cell.update = self.cell_moving(cell)
        self.field[co] = cell

    def blue_cell(self, co):
        cell = Entity(
            model="sphere",
            texture=load_texture("source/blue.jpg"),
            scale=self.cell_scale,
            position=co,
        )
        self.fixed_cubic(cell, color.hex("aef4ff"), self.cell_cubic_thickness)
        cell.rotation_z = -90
        cell.update = self.cell_moving(cell)
        self.field[co] = cell

    def cell_moving(self, cell):
        def func():
            cell.rotation_y += time.dt * 220

        return func

    def fixed_cubic(self, parent, color, thickness, segments=5):
        outline = lambda co, deg: Entity(
            parent=scene,
            model=Quad(segments=segments, mode="line", thickness=thickness),
            color=color,
            position=co,
            rotation=deg,
            scale=parent.scale,
        )
        {
            "front": outline((parent.x, parent.y, parent.z + -parent.scale.z * 0.5), (0, 0, 0)),
            "back": outline((parent.x, parent.y, parent.z + parent.scale.z * 0.5), (0, 0, 0)),
            "right": outline((parent.x + parent.scale.x * 0.5, parent.y, parent.z), (0, 90, 0)),
            "left": outline((parent.x + -parent.scale.x * 0.5, parent.y, parent.z), (0, 90, 0)),
            "top": outline((parent.x, parent.y + parent.scale.y * 0.5, parent.z), (90, 0, 0)),
            "bottom": outline((parent.x, parent.y + -parent.scale.y * 0.5, parent.z), (90, 0, 0)),
        }

    def cubic(self, parent, color, thickness, segments=5):
        outline = lambda co, deg: Entity(
            parent=parent,
            model=Quad(segments=segments, mode="line", thickness=thickness),
            color=color,
            position=co,
            rotation=deg,
        )
        {
            "front": outline((0, 0, -0.5), (0, 0, 0)),
            "back": outline((0, 0, 0.5), (0, 0, 0)),
            "right": outline((0.5, 0, 0), (0, 90, 0)),
            "left": outline((-0.5, 0, 0), (0, 90, 0)),
            "top": outline((0, 0.5, 0), (90, 0, 0)),
            "bottom": outline((0, -0.5, 0), (90, 0, 0)),
        }

    def co_convert(self, co: Co):
        """
        좌표는 입력 전에 반드시 이 함수를 거쳐야 합니다

        ---
        grid_scale(한 변의 길이)은 홀수여야 합니다
        ---
        0,0을 포함하기때문입니다

        반환값: Grid내부 좌표
        """
        grid_scale = self.space_size
        convert_yz = lambda x, y, z: tuple(map(lambda x: x * self.cell_scale, (x, z, y)))
        if len(co) == 3:
            co = convert_yz(*co)
        else:
            co = convert_yz(*co, 0)
        threshold, zero = divmod(grid_scale, 2)
        if not zero:
            raise CellControllException("grid_scale가 짝수이면 안됩니다!")

        def calculation(value):
            """ 1차원 수준에서 좌표연산입니다. """
            if value < -threshold:
                return threshold - (threshold - value) % grid_scale
            if value > threshold:
                return -threshold + (value + threshold) % grid_scale
            return value

        return tuple(calculation(co) for co in co)


if __name__ == "__main__":
    app = Ursina()
    controller = CellController()
    controller(
        {
            (1, 1): 1,
            (1, 2): 2,
            (2, 1): 1,
            (0, 0): 2,
        }
    )
    EditorCamera()
    app.run()