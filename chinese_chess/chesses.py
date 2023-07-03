from chinese_chess.chess import Chess
from chinese_chess.chess_except import CommandExcept, MoveExcept
from chinese_chess.enum import Team
from PIL import Image

pic_root = r'D:\MyQQBot\MiraiBot\chinese_chess\my_chess' + '\\'


class Horse(Chess):  # 马
    def __init__(self, team: str, x: int, y: int):
        path = pic_root + 'red_knight.jpg'
        if team == Team.Black:
            path = pic_root + 'black_knight.jpg'
        img = Image.open(path)
        super(Horse, self).__init__(team, img, x, y, '马')

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        chess = mp[new_x][new_y]  # 判断落点是否有自家棋子
        if chess and chess.team == self.team:
            raise MoveExcept()
        target = mp[new_x][new_y]
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        forward_or_not = command[0] == '进'
        num = command[1]
        if command[0] == '平':
            raise CommandExcept()
        target_y = self.get_cow_by_num(num)
        x = self.transform.position.x
        y = self.transform.position.y
        _x = 1
        _y = target_y - y
        is_lega = True
        if abs(_y) != 1 and abs(_y) != 2:
            raise CommandExcept()
        if self.team == Team.Red:
            if abs(_y) == 1:
                if forward_or_not:
                    if mp[x - 1][y]:
                        is_lega = False
                    _x = -2
                else:
                    if mp[x + 1][y]:
                        is_lega = False
                    _x = 2
            else:
                if mp[x][y + int(_y / 2)]:
                    is_lega = False
                if forward_or_not:
                    _x = -1
        else:
            if abs(_y) == 1:
                if forward_or_not:
                    if mp[x + 1][y]:
                        is_lega = False
                    _x = 2
                else:
                    if mp[x - 1][y]:
                        is_lega = False
                    _x = -2
            else:
                if mp[x][y + int(_y / 2)]:
                    is_lega = False
                if not forward_or_not:
                    _x = -1
        if not is_lega:
            raise MoveExcept()
        return x, y, x + _x, y + _y


class Car(Chess):  # 车
    def __init__(self, team: str, x: int, y: int):
        path = pic_root + 'red_rook.jpg'
        if team == Team.Black:
            path = pic_root + 'black_rook.jpg'
        img = Image.open(path)
        super(Car, self).__init__(team, img, x, y, '车')

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        if target and target.team == self.team:
            raise MoveExcept()
        if x == new_x:
            if new_y > y:
                for j in range(y + 1, new_y):
                    if mp[x][j]:
                        raise MoveExcept()
            else:
                for j in range(new_y + 1, y):
                    if mp[x][j]:
                        raise MoveExcept()
        else:
            if new_x > x:
                for j in range(x + 1, new_x):
                    if mp[j][y]:
                        raise MoveExcept()
            else:
                for j in range(new_x + 1, x):
                    if mp[j][y]:
                        raise MoveExcept()
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        x = self.transform.position.x
        y = self.transform.position.y
        _x = 0
        _y = 0
        direction = command[0]
        distance = command[1]
        if direction == '进' or direction == '退':
            _x = self.get_dis_by_num(distance)
            if (self.team == Team.Red and direction == '进') or (self.team == Team.Black and direction == '退'):
                _x = -self.get_dis_by_num(distance)
            if x + _x > 9 or x + _x < 0:
                raise CommandExcept()
        else:
            _y = self.get_cow_by_num(distance) - y
            if _y == 0:
                return CommandExcept()
        return x, y, x + _x, y + _y


class Elephant(Chess):  # 相象
    def __init__(self, team: str, x: int, y: int):
        name = '相'
        path = pic_root + 'red_elephant.jpg'
        if team == Team.Black:
            name = '象'
            path = pic_root + 'black_elephant.jpg'
        img = Image.open(path)
        super(Elephant, self).__init__(team, img, x, y, name)

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        if target and target.team == self.team:
            raise CommandExcept()
        if mp[int((x + new_x) / 2)][int((y + new_y) / 2)]:  # 这里会不会因为float转int导致坐标出错
            raise MoveExcept()
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        forward_or_not = command[0] == '进'
        num = command[1]
        if command[0] == '平':
            raise CommandExcept()
        x = self.transform.position.x
        y = self.transform.position.y
        _x = 2
        _y = self.get_cow_by_num(num) - y
        if abs(_y) != 2:
            raise CommandExcept()
        if (self.team == Team.Red and forward_or_not) or (self.team == Team.Black and (not forward_or_not)):
            _x = -2
        target_x = x + _x
        if self.team == Team.Red:
            if target_x > 9 or target_x < 5:
                raise CommandExcept()
        else:
            if target_x < 0 or target_x > 4:
                raise CommandExcept()
        return x, y, target_x, y + _y


class Soldier(Chess):  # 兵卒
    def __init__(self, team: str, x: int, y: int):
        name = '兵'
        path = pic_root + 'red_pawn.jpg'
        if team == Team.Black:
            name = '卒'
            path = pic_root + 'black_pawn.jpg'
        img = Image.open(path)
        super(Soldier, self).__init__(team, img, x, y, name)

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        direction = command[0]
        cow = command[1]
        x = self.transform.position.x
        y = self.transform.position.y
        _y = 1
        _x = 1
        if direction == '退':  # 小兵不能回退滴
            raise CommandExcept()
        if direction == '平':
            # 先判定过河没有
            if self.team == Team.Red:
                if x > 4:
                    raise CommandExcept()
            else:
                if x < 5:
                    raise CommandExcept()
            target_y = self.get_cow_by_num(cow)
            _y = target_y - y
            # 小兵每次只能平一格
            if abs(target_y - y) != 1:
                raise CommandExcept()
            _x = 0
            # 目标位置有没有己方单位
            chess = mp[x][target_y]
            if chess and chess.team == self.team:
                raise CommandExcept()
        elif direction == '进':
            if self.get_dis_by_num(cow) != 1:
                raise CommandExcept()
            if self.team == Team.Red:
                _x = -1
                _y = 0
                # 到顶格没有？
                if x - 1 < 0:
                    raise CommandExcept()
                # 目标位置有没有己方单位
                chess = mp[x - 1][y]
                if chess and chess.team == self.team:
                    raise CommandExcept()
            else:
                _x = 1
                _y = 0
                # 到顶格没有？
                if x + 1 > 9:
                    raise CommandExcept()
                # 目标位置有没有己方单位
                chess = mp[x + 1][y]
                if chess and chess.team == self.team:
                    raise CommandExcept()
        else:
            raise CommandExcept()
        return x, y, x + _x, y + _y


class Guard(Chess):  # 士
    def __init__(self, team: str, x: int, y: int):
        name = '仕'
        path = pic_root + 'red_mandarin.jpg'
        if team == Team.Black:
            name = '士'
            path = pic_root + 'black_mandarin.jpg'
        img = Image.open(path)
        super(Guard, self).__init__(team, img, x, y, name)

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        if target and target.team == self.team:
            raise CommandExcept()
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        direction = command[0]
        if direction == '平':
            raise CommandExcept()
        target_y = self.get_cow_by_num(command[1])
        x = self.transform.position.x
        y = self.transform.position.y
        if abs(target_y - y) != 1:
            raise CommandExcept()
        if target_y < 3 or target_y > 5:
            raise CommandExcept()
        _x = 1
        if self.team == Team.Red:
            if direction == '进':
                _x = -1
            if x + _x < 7 or x + _x > 9:
                raise CommandExcept()
        else:
            if direction == '退':
                _x = -1
            if x + _x < 0 or x + _x > 2:
                raise CommandExcept()
        return x, y, x + _x, target_y


class Artillery(Chess):  # 炮，这个好难。。
    def __init__(self, team: str, x: int, y: int):
        path = pic_root + 'red_cannon.jpg'
        if team == Team.Black:
            path = pic_root + 'black_cannon.jpg'
        img = Image.open(path)
        super(Artillery, self).__init__(team, img, x, y, '炮')

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        x = self.transform.position.x
        y = self.transform.position.y
        _x = 0
        _y = 0
        distance = 0
        cow = y
        direction = command[0]
        if direction == '进' or direction == '退':
            distance = self.get_dis_by_num(command[1])
        else:
            cow = self.get_cow_by_num(command[1])
        if distance != 0:
            _x = distance
            if (self.team == Team.Red and direction == '进') or (self.team == Team.Black and direction == '退'):
                _x = -distance
            # 落点是否出界
            if x + _x < 0 or x + _x > 9:
                raise CommandExcept()
            # 有没有翻山
            count = 0
            if _x > 0:
                for i in range(x + 1, x + _x):
                    if mp[i][y]:
                        count = count + 1
            else:
                for i in range(x + _x + 1, x):
                    if mp[i][y]:
                        count = count + 1
            # 只能翻一座山
            if count > 1:
                raise CommandExcept()
            # 翻山后必须打牛
            elif count == 1:
                chess = mp[x + _x][y]
                if (chess is None) or (chess.team == self.team):
                    raise CommandExcept()
            # 没有翻山终点不能有棋子
            else:
                if mp[x + _x][y]:
                    raise CommandExcept()
        else:
            _y = cow - y
            if cow == y:
                raise CommandExcept()
            # 有没有翻山
            count = 0
            if cow > y:
                for i in range(y + 1, cow):
                    if mp[x][i]:
                        count = count + 1
            else:
                for i in range(cow + 1, y):
                    if mp[x][i]:
                        count = count + 1
            # 只能翻一座山
            if count > 1:
                raise CommandExcept()
            # 翻山后必须打牛
            elif count == 1:
                chess = mp[x][cow]
                if (chess is None) or (chess.team == self.team):
                    raise CommandExcept()
            # 没有翻山终点不能有棋子
            else:
                if mp[x][cow]:
                    raise CommandExcept()
        return x, y, x + _x, y + _y


class Commander(Chess):  # 将帅
    def __init__(self, team: str, x: int, y: int):
        name = '帅'
        path = pic_root + 'red_king.jpg'
        if team == Team.Black:
            name = '将'
            path = pic_root + 'black_king.jpg'
        img = Image.open(path)
        super(Commander, self).__init__(team, img, x, y, name)

    def move(self, command: str, mp):
        x, y, new_x, new_y = self.is_king_to_king(command, mp)
        if x == -1:
            x, y, new_x, new_y = self.is_legal(command, mp)
        target = mp[new_x][new_y]
        if target and target.team == self.team:
            raise CommandExcept()
        mp[new_x][new_y] = mp[x][y]
        mp[x][y] = None
        self.update_position(new_x, new_y)
        return x, y, new_x, new_y, target

    def is_legal(self, command: str, mp):
        direction = command[0]
        cow = 0
        distance = 1
        x = self.transform.position.x
        y = self.transform.position.y
        _y = 0
        _x = 0
        if direction == '平':
            distance = 0
            cow = self.get_cow_by_num(command[1])
            if cow < 3 or cow > 5:
                raise CommandExcept()
            if abs(cow - y) != 1:
                raise CommandExcept()
            _y = cow - y
        else:
            if self.get_dis_by_num(command[1]) != 1:
                raise CommandExcept()
        if distance != 0:
            _x = 1
            if (self.team == Team.Red and direction == '进') or (self.team == Team.Black and direction == '退'):
                _x = -1
            if self.team == Team.Red:
                if x + _x < 7 or x + _x > 9:
                    raise CommandExcept()
            else:
                if x + _x < 0 or x + _x > 2:
                    raise CommandExcept()
        return x, y, x + _x, y + _y

    def is_king_to_king(self, command: str, mp):
        direction = command[0]
        distance = self.get_dis_by_num(command[1])
        if direction == '进' and (4 < distance < 10):
            y = self.transform.position.y
            x = self.transform.position.x
            _x = distance
            count = 0
            if self.team == Team.Red:
                _x = -distance
                for i in range(x - distance + 1, x):
                    if mp[i][y]:
                        count = count + 1
            else:
                for i in range(x + 1, x + distance):
                    if mp[i][y]:
                        count = count + 1
            if count != 0:
                return -1, -1, -1, -1
            king = mp[x + _x][y]
            if king and (king.name == '将' or king.name == '帅'):
                return x, y, x + _x, y
        return -1, -1, -1, -1
