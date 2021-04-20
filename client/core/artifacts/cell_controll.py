from queue import Queue
from typing import Tuple, Union
from ursina import *
from .origin.tools import *

Co = Union[Tuple[int, int, int], Tuple[int, int]]


class CellControllException(Exception):
    pass


class CellCounter:
    """
    Field에서 세포 숫자만 모니터링 하는데 사용하는 객체입니다.
    인스턴스를 호출하면 세포 존재 여부에 따라 bool을 반환합니다.
    """

    def __init__(self):
        self.counter = {BLUECELL: 0, REDCELL: 0}
        self.__repr__ = self.__str__

    def append(self, cell: int):
        self.counter[cell] += 1

    def remove(self, cell: int):
        if not self.counter[cell]:
            raise Exception("remove할 cell이 없습니다.")
        self.counter[cell] -= 1

    def count(self, cell: int):
        return self.counter[cell]

    def __call__(self):
        return True if self.counter[BLUECELL] or self.counter[REDCELL] else False

    def __str__(self):
        return str(self.counter)


class CellController(Entity):
    """ 유의: 외부에서 cell이라고 부르는 숫자를 여기서는 number라고 부른다. """

    def __init__(self, input_queue, finite_space_size=101):
        super().__init__()
        self.space_size = finite_space_size
        self.cell_scale = 0.5
        self.cell_cubic_thickness = 1.15
        self.scale = finite_space_size * self.cell_scale
        self.cubic(self, color.white10, thickness=1.5, segments=0)
        self.field = {}
        self.cell_monitor = CellCounter()
        self.generation = 0
        self.queue = input_queue
        self.prophecy_fieldset = Queue()
        self.end = False
        self.judged = False

    def __call__(self, space_dict):
        """
        좌표,number쌍이 들어있는 delta_dict를 입력받아서 세포들을 배치한다.
        0=delete
        1=blue_cell
        2=red_cell
        """
        for co, number in space_dict.items():
            co = self.co_convert(co)
            if not number:
                cell, cubic = self.field[co]
                self.cell_monitor.remove(cell.number)
                destroy(cell)
                for outline in cubic.values():
                    destroy(outline)
                del self.field[co]
            elif number == BLUECELL:
                self.blue_cell(co)
            elif number == REDCELL:
                self.red_cell(co)
            else:
                CellControllException("세포값이 잘못되었습니다")

    def update(self):
        """ 큐에 fieldset정보들이 들어오면 다른 큐에 세팅한다"""
        if not self.queue.empty():
            fieldset_list = self.queue.get()
            if fieldset_list[-1]:
                for field in fieldset_list:
                    self.prophecy_fieldset.put(field)
            else:
                # 첫 수신의 경우 (구분자: [-1]=False)
                window.title = "Clomia Life Game 3D Simulator"
                window.center_on_screen()
                del fieldset_list[-1]
                for field in fieldset_list:
                    self.prophecy_fieldset.put(field)
                self.next()

    def next(self):
        self.generation += 1
        if not self.prophecy_fieldset.empty():
            space_dict = self.prophecy_fieldset.get()
            self(space_dict)
        else:
            # info: end처리는 즉각적이지 않기 때문에 멸종 판정에는 사용할 수 없다
            self.end = True

    def red_cell(self, co):
        cell = Entity(
            model="sphere",
            texture=load_texture("source/red.jpg"),
            scale=self.cell_scale,
            position=co,
        )
        cell.number = REDCELL
        cubic_dict = self.fixed_cubic(cell, ColorSet.Cell["Cubic-Red"], self.cell_cubic_thickness)
        cell.rotation_z = -90
        cell.update = self.cell_moving(cell, creating=True)

        def default_moving():
            cell.update = self.cell_moving(cell)

        invoke(default_moving, delay=2)
        try:
            if self.field[co][0].number != cell.number:
                self.cell_monitor.remove(BLUECELL)
                self.cell_monitor.append(cell.number)
        except KeyError:
            self.cell_monitor.append(cell.number)
        self.field[co] = (cell, cubic_dict)

    def blue_cell(self, co):
        cell = Entity(
            model="sphere",
            texture=load_texture("source/blue.jpg"),
            scale=self.cell_scale,
            position=co,
        )
        cell.number = BLUECELL
        cubic_dict = self.fixed_cubic(cell, ColorSet.Cell["Cubic-Blue"], self.cell_cubic_thickness)
        cell.rotation_z = -90
        cell.update = self.cell_moving(cell, creating=True)

        def default_moving():
            cell.update = self.cell_moving(cell)

        invoke(default_moving, delay=2)
        try:
            if self.field[co][0].number != cell.number:
                self.cell_monitor.remove(REDCELL)
                self.cell_monitor.append(cell.number)
        except KeyError:
            self.cell_monitor.append(cell.number)
        self.field[co] = (cell, cubic_dict)

    @staticmethod
    def cell_moving(cell, creating=False):
        if creating:

            def func():
                cell.rotation_y += time.dt * 3000

        else:

            def func():
                cell.rotation_y += time.dt * 220

        return func

    @staticmethod
    def fixed_cubic(parent, color, thickness, segments=5):
        outline = lambda co, deg: Entity(
            parent=scene,
            model=Quad(segments=segments, mode="line", thickness=thickness),
            color=color,
            position=co,
            rotation=deg,
            scale=parent.scale,
        )
        cubic_dict = {
            "front": outline((parent.x, parent.y, parent.z + -parent.scale.z * 0.5), (0, 0, 0)),
            "back": outline((parent.x, parent.y, parent.z + parent.scale.z * 0.5), (0, 0, 0)),
            "right": outline((parent.x + parent.scale.x * 0.5, parent.y, parent.z), (0, 90, 0)),
            "left": outline((parent.x + -parent.scale.x * 0.5, parent.y, parent.z), (0, 90, 0)),
            "top": outline((parent.x, parent.y + parent.scale.y * 0.5, parent.z), (90, 0, 0)),
            "bottom": outline((parent.x, parent.y + -parent.scale.y * 0.5, parent.z), (90, 0, 0)),
        }
        return cubic_dict

    @staticmethod
    def cubic(parent, color, thickness, segments=5):
        outline = lambda co, deg: Entity(
            parent=parent,
            model=Quad(segments=segments, mode="line", thickness=thickness),
            color=color,
            position=co,
            rotation=deg,
        )
        cubic_dict = {
            "front": outline((0, 0, -0.5), (0, 0, 0)),
            "back": outline((0, 0, 0.5), (0, 0, 0)),
            "right": outline((0.5, 0, 0), (0, 90, 0)),
            "left": outline((-0.5, 0, 0), (0, 90, 0)),
            "top": outline((0, 0.5, 0), (90, 0, 0)),
            "bottom": outline((0, -0.5, 0), (90, 0, 0)),
        }
        return cubic_dict

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
        convertor = lambda x, y, z: tuple(map(lambda n: n * self.cell_scale, (x, z, y)))
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

        finite_co = tuple(calculation(co) for co in co)
        if len(finite_co) == 3:
            return convertor(*finite_co)
        else:
            return convertor(*finite_co, 0)


if __name__ == "__main__":
    from queue import Queue

    input_queue = Queue()
    app = Ursina()
    controller = CellController(input_queue)
    controller(
        {
            (-70, 1): 1,
            (-51, 2): 2,
            (-71, 0): 1,
            (-71, 2): 2,
            (-72, 2): 1,
        }
    )
    EditorCamera()
    app.run()