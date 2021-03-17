from itertools import permutations, chain
from ursina import *

app = Ursina()
EditorCamera(zoom_speed=2)


class Cell(Entity):  # todo 코드 다시짤때는 grid를 parent로?
    def __init__(self, grid, co):
        super().__init__()
        self.grid = grid
        self.model = "sphere"
        self.model.colorize(
            down=color.magenta,
            up=color.peach,
            left=color.peach,
            right=color.magenta,
            back=color.yellow,
            forward=color.blue,
            smooth=False,
        )
        self.scale = (0.5, 0.5, 0.5)
        self.co = co
        x_coordinates, y_coordinates = co
        # * 0.5는 cell크기이다 점에서 면으로 보정하는 값은 그 절반인 0.25이다
        self.x = 0.25 + (0.5 * x_coordinates)
        self.y = 0.25 + (0.5 * y_coordinates)
        self.z = 0.375
        self.outline = Entity(
            parent=self,
            model=Quad(segments=5, mode="line", thickness=2),
            color=color.cyan,
            z=-0.75,
        )


class CellGrid(Entity):
    def __init__(self, scale: int):
        super().__init__()
        self.scale_value = scale
        self.model = Grid(scale, scale)
        self.scale = Vec2(scale // 2, scale // 2)
        self.color = color.rgba(255, 255, 255, a=15)
        self.cell_map = {}  #! 커스텀 딕셔너리로 해서 스스로 cell을 렌더링 하도록 하자
        self.negative_range = -scale // 2
        self.positive_range = (scale // 2) - 1
        grid_range = range(-scale // 2, scale // 2)
        for x in grid_range:
            for y in grid_range:
                self.cell_map[(x, y)] = False

    def co_calculation(self, co: int) -> int:
        """ grid를 벗어나는 좌표를 grid내부좌표로 변환한다"""

        def calculation(value):
            ne_threshold = self.negative_range
            po_threshold = self.positive_range
            grid_scale = self.scale_value
            if value < ne_threshold:
                value = po_threshold - (-value + po_threshold) % grid_scale
            if value > po_threshold:
                value = ne_threshold + (value + -ne_threshold) % grid_scale
            return value

        x, y = co
        return (calculation(x), calculation(y))

    def check(self, co):
        """ cell이 있으면 cell을 반환한다. 없다면 False를 반환한다"""
        co = self.co_calculation(co)
        target = self.cell_map[co]
        if (not target) and target != False:
            return True
        else:
            return target

    def screen_control(self):  # todo 롤처럼 마우스가 끝에 닿는걸로
        camera.x += held_keys["d"] * time.dt * 10
        camera.x -= held_keys["a"] * time.dt * 10
        camera.y += held_keys["w"] * time.dt * 10
        camera.y -= held_keys["s"] * time.dt * 10

    def update(self):
        self.screen_control()

    def neighbor_counter(self, *, cell=None, co=None) -> int:
        # 주변 8칸에 있는 cell 갯수를 반환한다
        x, y = cell.co if cell else co
        counter = 0
        for add_x, add_y in chain(permutations([-1, 0, 1], 2), ((1, 1), (-1, -1))):
            co = (x + add_x, y + add_y)
            if self.check(co):
                counter += 1
        return counter

    def execute_logic(self):
        state_delta = []
        for co, cell in self.cell_map.items():
            delta = self.logic(cell, co)
            if delta:
                state_delta.append(delta)

        for co, result in state_delta:
            self.cell_map[co] = result

    def logic(self, cell, co):
        if cell:
            neighbor_count = self.neighbor_counter(cell=cell)
            if not (neighbor_count == 2 or neighbor_count == 3):
                destroy(cell)
                return (cell.co, False)
        else:
            co = self.co_calculation(co)
            neighbor_count = self.neighbor_counter(co=co)
            if neighbor_count == 3:
                return (co, Cell(self, co))

    def init(self, co_list):
        for co in co_list:
            co = self.co_calculation(co)
            self.cell_map[co] = Cell(self, co)


grid = CellGrid(50)
glider = [(-1, 1), (-1, 0), (0, 1), (0, -1), (1, 1)]
infinity = [
    (0, 0),
    (1, 1),
    (2, 0),
    (2, 1),
    (3, 2),
    (4, 0),
    (4, 1),
    (4, 2),
    (0, 3),
    (0, 4),
    (1, 4),
    (2, 4),
    (4, 4),
]

grid.init(infinity)


def input(key):
    if key == "space":
        grid.execute_logic()


"""
def update():
    grid.execute_logic()
"""

app.run()