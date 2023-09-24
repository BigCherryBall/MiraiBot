class ChessExcept(Exception):
    def __init__(self):
        self.msg = ''

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg


class CommandExcept(ChessExcept):
    def __init__(self):
        self.msg = '命令不合法'


class MoveExcept(ChessExcept):
    def __init__(self):
        self.msg = '移动不合法'


class ChessNotFindExcept(CommandExcept):
    def __init__(self):
        self.msg = '目标棋子没有找到'


class BackExcept(ChessExcept):
    def __init__(self, msg='当前步不是最新步，无法悔棋'):
        self.msg = msg
