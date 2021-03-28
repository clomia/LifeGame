from ursina import *


class BackGround:
    def __init__(self, *, top=None, bottom, left=None, right=None, front=None, back=None):
        """
        6면에 사용될 이미지 경로를 입력해주세요

        """
        self.scale = 100
        self.walls = {
            "front": self.rendering((0, 0, -self.scale / 2), (0, 180, 0), front),
            "back": self.rendering((0, 0, self.scale / 2), (0, 0, 0), back),
            "right": self.rendering((self.scale / 2, 0, 0), (0, 90, 0), right),
            "left": self.rendering((-self.scale / 2, 0, 0), (0, 270, 0), left),
            "top": self.rendering((0, self.scale / 2, 0), (270, 0, 0), top),
            "bottom": self.rendering((0, -self.scale / 2, 0), (90, 0, 0), bottom),
        }

    def rendering(self, co, deg, img=None):
        if img:
            return Entity(
                parent=scene,
                model="quad",
                texture=load_texture(img),
                scale=self.scale,
                position=co,
                rotation=deg,
            )


class Universe:
    """
    거대한 정육면채를 만들고 우주로 감싼다.
    """

    def __init__(self, wall_imgs: dict, universe_img):
        self.walls = BackGround(
            top=wall_imgs.get("top", None),
            bottom=wall_imgs.get("bottom", None),
            left=wall_imgs.get("left", None),
            right=wall_imgs.get("right", None),
            front=wall_imgs.get("front", None),
            back=wall_imgs.get("back", None),
        )
        self.scale = self.walls.scale
        self.outlining = lambda co, deg: Entity(
            model=Quad(segments=0, mode="line", thickness=10),
            color=color.hex("f5f6f8"),
            position=co,
            rotation=deg,
            scale=self.scale,
        )

        self.cubic_bar()
        self.universe_img = universe_img

        self.SPACE = Entity(
            parent=scene,
            model="sphere",
            texture=load_texture(self.universe_img),
            double_sided=True,
            scale=17_000,
        )

    def cubic_bar(self):
        {
            "front": self.outlining((0, 0, -self.scale / 2), (0, 0, 0)),
            "back": self.outlining((0, 0, self.scale / 2), (0, 0, 0)),
            "right": self.outlining((self.scale / 2, 0, 0), (0, 90, 0)),
            "left": self.outlining((-self.scale / 2, 0, 0), (0, 90, 0)),
            "top": self.outlining((0, self.scale / 2, 0), (90, 0, 0)),
            "bottom": self.outlining((0, -self.scale / 2, 0), (90, 0, 0)),
        }