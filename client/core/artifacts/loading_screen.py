from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

if not __name__ == "__main__":
    from .universe import *
    from .origin import *
    from .cell_controll import *
    from .node_cube import *


class LoadScreen(FullUI):
    def __init__(self, pipe_queue, simul_loading_complate_signal):
        super().__init__()
        self.pipe_queue = pipe_queue
        self.simul_loading_complate_signal = simul_loading_complate_signal
        self.texture = load_texture("source/load_screen.jpg")
        invoke(self.main_execute, delay=1)

    def main_execute(self):
        walls = {
            "bottom": "source/wall_bottom.jpg",
            "top": "source/wall_top.jpg",
            "left": "source/wall_front.jpg",
        }
        internal = Universe(walls, "source/universe.jpg")
        Eye(limit=internal.scale)
        CellController(self.pipe_queue)
        MobiusNodeCube()
        destroy(self)
        invoke(lambda: self.simul_loading_complate_signal.put(SIGNAL), delay=2.7)


class InputHandler(Entity):
    def __init__(self):
        super().__init__()
        self.pressed = False

    def input(self, key):
        if key == "escape":
            if self.pressed:
                mouse.locked = True
                self.pressed = False
            else:
                mouse.locked = False
                self.pressed = True


class SimulLoadWaiter(FullUI):
    def __init__(self, bprin_connect, cursor):
        super().__init__()
        self.bprin_connect = bprin_connect
        self.cursor = cursor
        if LANGUAGE.now == "ko":
            self.msg_texture = load_texture("source/wait_msg_ko.png")
        elif LANGUAGE.now == "en":
            self.msg_texture = load_texture("source/wait_msg_en.png")
        self.visible = False
        self.enabled = False
        self.msg_windows = []
        self.msg_window_gen()

    def __call__(self, fieldset):
        """
        bprin_proc.offline_bprin함수에서 pipe_func로 인스턴스를 넘긴다.
        pipe_func는 callable이어야 하므로 __call__을 정의한것이다.

        트리거 시작점.
        """
        self.bprin_connect.send(fieldset)
        self.main_execute()
        InputHandler()

    def msg_window_gen(self):
        for xyz, ro in (
            ((4, 3, 70), (0, 0, 0)),
            ((4, 3, -70), (0, 180, 0)),
            ((74, 3, 0), (0, 90, 0)),
            ((-74, 3, 0), (0, -90, 0)),
        ):
            self.msg_windows.append(
                Entity(
                    model="quad",
                    texture=self.msg_texture,
                    position=xyz,
                    rotation=ro,
                    scale_x=1.3 * 30,
                    scale_y=0.5 * 30,
                    visible=False,
                )
            )

    def msg_window_visible(self):
        for msg_window in self.msg_windows:
            msg_window.visible = True

    def main_execute(self):
        """ bprin이 종료했지만 simul이 로딩중일때 생긴 대기시간동안 실행된다."""
        self.msg_window_visible()
        destroy(self.cursor)
        Sky()
        for z in range(8):
            for x in range(8):
                voxel = Voxel(position=(x, 0, z))
                voxel.eternal = True
                if x in (0, 7) or z in (0, 7):
                    Voxel(position=(x, 1, z))
        ground = Button(
            parent=scene,
            model="cube",
            position=(2.5, 985, 2.5),
            color=color.rgba(255, 255, 255, 0),
            scale_y=2000,
            scale_x=2000,
            scale_z=2000,
            double_sided=True,
        )
        # ground.model.colorize()
        Player()


class Player(FirstPersonController):
    def __init__(self):
        Entity.__init__(self)
        self.speed = 5
        self.origin_y = -0.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.cursor = Entity(parent=camera.ui, model="circle", color=color.black, scale=0.005)
        self.position = Vec3(4, 10, 4)
        self.mouse_sensitivity = Vec2(60, 60)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_duration = 0.5
        self.jumping = False
        self.air_time = 0


class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            origin_y=0.5,
            texture=load_texture("source/block_texture.png"),
            color=color.color(0, 0, random.uniform(0.7, 1.0)),
            highlight_color=color.lime,
        )

    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                voxel = Voxel(position=self.position + mouse.normal)

            if key == "right mouse down":
                destroy(self)


if __name__ == "__main__":
    app = Ursina()
    window.fullscreen = True
    window.cog_button.visible = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False

    class LANGUAGE:
        now = "en"

    SimulLoadWaiter(object, Entity()).main_execute()
    app.run()