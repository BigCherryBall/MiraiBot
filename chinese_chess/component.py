from pathlib import Path


class Vector2:
    def __init__(self, x: int = -1, y: int = -1):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))

    def __str__(self):
        return str((self.x, self.y))


class ChessConfig:
    def __init__(self, chess_dir: Path, map_dir: Path):
        self.chess_dir = chess_dir
        self.map_dir = map_dir
