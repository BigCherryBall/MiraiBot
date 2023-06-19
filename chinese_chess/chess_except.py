class CommandExcept(Exception):
    msg = '命令不合法'

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg


class MoveExcept(Exception):
    msg = '移动不合法'

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg
