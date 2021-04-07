from ursina import *


class MobiusNodeCube(Entity):
    def __init__(self):
        super().__init__()
        self.scale = 3
        self.field_scale = 100
        self.vertex = 46
        self.world_z = -50
        self.world_x = 150  # 150을 넘어가면 z축이 변경되면서 튕겨나간다
        self.x += 130  # 이것도 일정 숫자를 넘어가면 튕겨나간다
        self.in_vertex = (
            lambda axis: self.vertex - self.scale.x / 2 < axis < self.vertex + self.scale.x / 2
            or -self.vertex - self.scale.x / 2 < axis < -self.vertex + self.scale.x / 2
        )

        self.POSITIVE_DIRECTION = 1
        self.NEGATIVE_DIRECTION = 0
        self.model = "cube"
        self.y = -self.field_scale / 2 + self.scale.y + 0.8
        self.rotation_z = 60
        self.rotation_x = 60
        self.texture = load_texture("source/cube.png")
        position_setting = (Func(self._position_setting), 11)  # 총 11초
        move_around = (
            Func(self._move_z_ne),
            7,
            Func(self._move_x_ne),
            7,
            Func(self._move_z_po),
            7,
            Func(self._move_x_po),
            7,
        )  # 총 28초
        up_down = (Func(self._r_up, 0.7), 5, Func(self._r_down, 0.7), 5)  # 총 10초
        furious = (
            Func(self._rotation_y, 2000),
            0.25,
            Func(self._rotation_xz, 1000),
            0.25,
            Func(self._rotation_yz, 1000),
            0.25,
            Func(self._rotation_xy, 1000),
            0.25,
        )  # 총 1초 (이것으로 인한 각도 변화율은 지금이 딱 좋다 바꾸지 말자)
        move_around_up_down = (
            Func(self._move_z_ne),
            7,
            Func(self._r_up, 0.7),
            5,
            Func(self._r_down, 0.7),
            5,
            Func(self._move_x_ne),
            7,
            Func(self._r_up, 0.7),
            5,
            Func(self._r_down, 0.7),
            5,
            Func(self._move_z_po),
            7,
            Func(self._r_up, 0.7),
            5,
            Func(self._r_down, 0.7),
            5,
            Func(self._move_x_po),
            7,
            Func(self._r_up, 0.7),
            5,
            Func(self._r_down, 0.7),
            5,
        )  # 총 68초
        self.complete_move = position_setting + move_around + up_down + furious  # 총 50초
        self.complete_move_2 = move_around + furious  # 총 28초
        self.complete_move_3 = move_around_up_down + furious
        # 이터레이터를 곱하거나 더해서 언패킹하면 작동을 안해서 단순 반복입력함.
        self.movement = Sequence(*self.complete_move)
        self.movement.loop = True
        self.movement.start()
        invoke(self.movement_resetting, args=self.complete_move_2, delay=50)
        invoke(self.movement_resetting, args=self.complete_move_3, delay=78)

    def movement_resetting(self, args):
        self.movement.kill()
        self.movement = Sequence(*args)
        self.movement.loop = True
        self.movement.start()

    def in_other_vertex(self, axis):
        if axis >= 0:
            return lambda x: -self.vertex - self.scale.x / 2 < x < -self.vertex + self.scale.x / 2
        else:
            return lambda x: self.vertex - self.scale.x / 2 < x < self.vertex + self.scale.x / 2

    def _move_z_po(self):
        """
        z축으로 모서리 끝까지 이동합니다.
        """
        in_other_vertex = self.in_other_vertex(self.z)

        def func():
            self.rotation_y += 70 * time.dt
            if not in_other_vertex(self.z):
                self.z += 15 * time.dt

        self.update = func

    def _move_z_ne(self):
        """
        z축으로 모서리 끝까지 이동합니다.
        """
        in_other_vertex = self.in_other_vertex(self.z)

        def func():
            self.rotation_y += 70 * time.dt
            if not in_other_vertex(self.z):
                self.z -= 15 * time.dt

        self.update = func

    def _move_x_po(self):
        """
        x축으로 모서리 끝까지 이동합니다.
        """
        in_other_vertex = self.in_other_vertex(self.x)

        def func():
            self.rotation_y += 70 * time.dt
            if not in_other_vertex(self.x):
                self.x += 15 * time.dt

        self.update = func

    def _move_x_ne(self):
        """
        x축으로 모서리 끝까지 이동합니다.
        """
        in_other_vertex = self.in_other_vertex(self.x)

        def func():
            self.rotation_y += 70 * time.dt
            if not in_other_vertex(self.x):
                self.x -= 15 * time.dt

        self.update = func

    def _position_setting(self):
        """
        x=0,z=0 이라고 간주하고 모서리 끝으로 이동합니다.
        대략 9.5초가 걸리며 여유롭게 11초를 필요로 합니다.
        이미 모서리 끝인 경우 회전만 합니다
        """

        def func():
            self.rotation_y += 130 * time.dt
            if not self.in_vertex(self.z):
                self.z += 10 * time.dt
            elif not self.in_vertex(self.x):
                self.x += 10 * time.dt

        self.update = func

    def _r_x(self, value=100, r_speed=70):
        def func():
            self.rotation_y += r_speed * time.dt
            self.x += value * time.dt

        self.update = func

    def _r_y(self, value=100, r_speed=70):
        def func():
            self.rotation_y += r_speed * time.dt
            self.y += value * time.dt

        self.update = func

    def _r_z(self, value=100, r_speed=70):
        def func():
            self.rotation_y += r_speed * time.dt
            self.z += value * time.dt

        self.update = func

    def _rotation_y(self, speed=100):
        def func():
            self.rotation_y += speed * time.dt

        self.update = func

    def _rotation_x(self, speed=100):
        def func():
            self.rotation_x += speed * time.dt

        self.update = func

    def _rotation_z(self, speed=100):
        def func():
            self.rotation_z += speed * time.dt

        self.update = func

    def _rotation_xy(self, speed=100):
        def func():
            self.rotation_x += speed * time.dt
            self.rotation_y += speed * time.dt

        self.update = func

    def _rotation_xz(self, speed=100):
        def func():
            self.rotation_x += speed * time.dt
            self.rotation_z += speed * time.dt

        self.update = func

    def _rotation_yz(self, speed=100):
        def func():
            self.rotation_z += speed * time.dt
            self.rotation_y += speed * time.dt

        self.update = func

    def _r_up(self, speed=100, r_speed=70):
        def func():
            self.rotation_y += r_speed * time.dt
            self.y += speed * time.dt

        self.update = func

    def _r_down(self, speed=100, r_speed=70):
        def func():
            self.rotation_y += r_speed * time.dt
            self.y -= speed * time.dt

        self.update = func


if __name__ == "__main__":
    app = Ursina()
    Entity(
        model="quad",
        scale=100,
        texture=load_texture("source/wall_bottom.jpg"),
        position=(0, -100 / 2, 0),
        rotation=(90, 0, 0),
    )

    MobiusNodeCube()

    Sky()
    eye = EditorCamera()
    eye.position = (0, -49, -10)

    app.run()
