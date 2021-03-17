from itertools import permutations, chain
from ursina import *

app = Ursina()
EditorCamera(zoom_speed=2)


class Cell(Entity):
    def __init__(self, co):
        super().__init__()
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
        self.model = Grid(scale, scale)
        self.scale = Vec2(scale // 2, scale // 2)
        self.color = color.rgba(255, 255, 255, a=15)
        self.cell_map = {}
        self.negative_range = -scale // 2
        self.positive_range = (scale // 2) - 1
        grid_range = range(-scale // 2, scale // 2)
        for x in grid_range:
            for y in grid_range:
                self.cell_map[(x, y)] = False

    def check(self, co):
        """ cell이 있으면 cell을 반환한다. 없다면 False를 반환한다"""
        x, y = co
        if (
            x < self.negative_range
            or x > self.positive_range
            or y < self.negative_range
            or y > self.positive_range
        ):
            return False
        target = self.cell_map[co]
        if (not target) and target != False:
            return True
        else:
            return target

    def screen_control(self):
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
            neighbor_count = self.neighbor_counter(co=co)
            if neighbor_count == 3:
                return (co, Cell(co))

    def init(self, co_list):
        for co in co_list:
            self.cell_map[co] = Cell(co)


grid = CellGrid(50)
grid.init([(-1, 1), (-1, 0), (0, 1), (0, -1), (1, 1)])


def input(key):
    if key == "left mouse down":
        grid.execute_logic()


app.run()