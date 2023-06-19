class Vector2:
    x: int = -1
    y: int = -1

    def __init__(self, x: int = -1, y: int = -1):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))

    def __str__(self):
        return str((self.x, self.y))


class Transform:
    def __init__(self, owner, x: int, y: int):
        self.position: Vector2 = Vector2(x, y)
        self.scale: Vector2 = Vector2(1, 1)  # 图片缩放
        self.rotation: float = 0  # 图片旋转角，-180到180之间
        self.__chess = owner

