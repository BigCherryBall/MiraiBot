import math
import random
import re
import time
from tool import get_time_str
from chinese_chess.chess_except import ChessNotFindExcept, BackExcept
from chinese_chess.chesses import *
from chinese_chess.enum import Team, Turn


class GameControl:
    def __init__(self, seed: int = random.randint(0, 10000)):
        # 空棋盘
        # 实时棋盘，是一个二维的列表，列表里面是棋子对象的引用，没有棋子的地方是None。通过str(棋子对象的引用)获取其中的名字，格式为红/黑+棋子名字（注意红黑方的部分棋子名称不同）
        # 绘制棋盘也是读取这个二维列表的数据，通过棋子对象的引用.transform.position访问棋子坐标，如 引用.transform.position.x可以访问x坐标（坐标从0开始）
        self.map = [[None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None]]

        # 棋子对象池,所有棋盘共享,类的内部可访问，外部无法访问。只读不改。
        self.__chess_list = [
            # -------------黑方初始化------------------
            Car(Team.Black, 0, 0),
            Horse(Team.Black, 0, 1),
            Elephant(Team.Black, 0, 2),
            Guard(Team.Black, 0, 3),
            Commander(Team.Black, 0, 4),
            Guard(Team.Black, 0, 5),
            Elephant(Team.Black, 0, 6),
            Horse(Team.Black, 0, 7),
            Car(Team.Black, 0, 8),
            Artillery(Team.Black, 2, 1),
            Artillery(Team.Black, 2, 7),
            Soldier(Team.Black, 3, 0),
            Soldier(Team.Black, 3, 2),
            Soldier(Team.Black, 3, 4),
            Soldier(Team.Black, 3, 6),
            Soldier(Team.Black, 3, 8),
            # -------------红方初始化------------------
            Car(Team.Red, 9, 0),
            Horse(Team.Red, 9, 1),
            Elephant(Team.Red, 9, 2),
            Guard(Team.Red, 9, 3),
            Commander(Team.Red, 9, 4),
            Guard(Team.Red, 9, 5),
            Elephant(Team.Red, 9, 6),
            Horse(Team.Red, 9, 7),
            Car(Team.Red, 9, 8),
            Artillery(Team.Red, 7, 1),
            Artillery(Team.Red, 7, 7),
            Soldier(Team.Red, 6, 0),
            Soldier(Team.Red, 6, 2),
            Soldier(Team.Red, 6, 4),
            Soldier(Team.Red, 6, 6),
            Soldier(Team.Red, 6, 8)
        ]
        # 该谁走棋了
        self.turn = Turn.Red
        # 是否结束，没有为None，结束了就为胜利方
        self.game_over = None
        # 对弈状态:not_begin,has_began,pre
        self.status = 'not_begin'
        # 记录每次行棋的开始位置和目标位置,以便提示和悔棋
        self.__x = -1
        self.__y = -1
        self.__new_x = -1
        self.__new_y = -1
        # 每次行棋的目标位置的棋子记录:
        self.be_eat_chess = None
        # 悔棋合法
        self.back_is_legal = False
        # 回合计数
        self.round_count = 0
        # 随机数种子,用于区分不同的群
        self.seed = str(seed)
        # 开始和结束时间
        self.start_time = 0
        self.end_time = 0
        # 步数统计
        self.step = 0
        # 上一步行棋时间，用于单步计时
        self.last_step_time = 0
        # 当前步用时
        self.current_step_time = 0

    # 将空棋盘变为初始化棋盘
    def init_map(self):
        for i in range(0, 10):
            for j in range(0, 9):
                self.map[i][j] = None
        # 该谁走棋了
        self.turn = Turn.Red
        # 是否结束，没有为None，结束了就为胜利方
        self.game_over = None
        # 对弈状态:not_begin,has_began,pre
        self.status = 'has_began'
        # 记录每次行棋的开始位置和目标位置,以便提示和悔棋
        self.__x = -1
        self.__y = -1
        self.__new_x = -1
        self.__new_y = -1
        # 每次行棋的目标位置的棋子记录:
        self.be_eat_chess = None
        # 悔棋合法
        self.back_is_legal = False
        # 回合计数
        self.round_count = 0
        # 开始时间
        self.start_time = time.time()
        # 步数统计
        self.step = 0
        # 上一步行棋时刻，用于单步计时
        self.last_step_time = self.start_time
        # 当前步用时
        self.current_step_time = 0
        # -------------从棋子对象池里面读取数据------------------
        for chess in self.__chess_list:
            chess.back_to_init_pos()
            self.map[chess.init_pos.x][chess.init_pos.y] = chess

    # 从机器人那里接受到的走棋命令后，调用这个函数
    def move_chess(self, command: str):  # 命令的长度为4
        pattern1 = re.compile('^[车马炮象相仕士将帅兵卒][1-9一二三四五六七八九][进退平][1-9一二三四五六七八九]$')
        right1 = pattern1.match(command)  # 是否匹配形式1
        pattern2 = re.compile('^[前后][车马炮象相仕士兵卒][进退平][1-9一二三四五六七八九]$')
        right2 = pattern2.match(command)  # 是否匹配形式2
        if not (right1 or right2):
            raise CommandExcept()  # 如果命令都不匹配，抛出命令不匹配异常
        chess = self.get_chess(command[:2], right1, right2)  # 命令的前两个字确定棋子
        if not chess:
            raise CommandExcept()
        self.__x, self.__y, self.__new_x, self.__new_y, *be_eat_chess = chess.move(command[2:], self.map)  # 命令的后两个字移动棋子
        if be_eat_chess and be_eat_chess[0]:
            self.be_eat_chess = be_eat_chess[0]
            if be_eat_chess[0].name == '将' or be_eat_chess[0] == '帅':
                self.set_over(self.turn)
                self.round_count = math.ceil(self.step / 2)
                self.end_time = int(time.time())
                self.current_step_time = self.end_time - self.last_step_time
        else:
            self.be_eat_chess = None
        # 更新变量
        self.back_is_legal = True
        self.step += 1
        current_time = time.time()
        self.current_step_time = current_time - self.last_step_time
        self.last_step_time = current_time
        if self.turn == Turn.Red:
            self.turn = Turn.Black
        else:
            self.turn = Turn.Red

    def get_chess(self, command: str, right1, right2) -> Chess:
        if right1:
            chess_name = command[0]
            cow = self.get_cow_by_num(command[1])
            chess: Chess = None
            for i in range(0, 10):
                ches = self.map[i][cow]
                if ches and ches.name == chess_name and ches.team == self.turn:
                    chess = ches
                    break
            if chess:
                return chess
            else:
                raise ChessNotFindExcept()
        if right2:
            chess1 = None
            chess2 = None
            forward_or_behind = command[0]
            chess_name = command[1]
            chess1_r = 0
            cow = 0
            for i in range(0, 10):
                for j in range(0, 9):
                    ches = self.map[i][j]
                    if ches and ches.name == chess_name and ches.team == self.turn:
                        chess1 = ches
                        cow = j
                        chess1_r = i
                if chess1:
                    break
            for i in range(chess1_r + 1, 10):
                ches = self.map[i][cow]
                if ches and ches.name == chess_name and ches.team == self.turn:
                    chess2 = ches
                    break

            if not (chess1 and chess2):
                raise ChessNotFindExcept()
            if self.turn == Turn.Red:
                if forward_or_behind == '前':
                    return chess1
                else:
                    return chess2
            else:
                if forward_or_behind == '前':
                    return chess2
                else:
                    return chess1

    def get_cow_by_num(self, num):
        if num == '1' or num == '一':
            if self.turn == Turn.Red:
                return 8
            else:
                return 0
        elif num == '2' or num == '二':
            if self.turn == Turn.Red:
                return 7
            else:
                return 1
        elif num == '3' or num == '三':
            if self.turn == Turn.Red:
                return 6
            else:
                return 2
        elif num == '4' or num == '四':
            if self.turn == Turn.Red:
                return 5
            else:
                return 3
        elif num == '5' or num == '五':
            if self.turn == Turn.Red:
                return 4
            else:
                return 4
        elif num == '6' or num == '六':
            if self.turn == Turn.Red:
                return 3
            else:
                return 5
        elif num == '7' or num == '七':
            if self.turn == Turn.Red:
                return 2
            else:
                return 6
        elif num == '8' or num == '八':
            if self.turn == Turn.Red:
                return 1
            else:
                return 7
        elif num == '9' or num == '九':
            if self.turn == Turn.Red:
                return 0
            else:
                return 8

    def paint_map(self):
        m = Image.open(pic_root + 'map.jpg')
        # 先画位置提示:
        if self.turn == Turn.Red:
            begin = Image.open(pic_root + 'black_begin.jpg')
            end = Image.open(pic_root + 'black_end.jpg')
        else:
            begin = Image.open(pic_root + 'red_begin.jpg')
            end = Image.open(pic_root + 'red_end.jpg')
        m.paste(begin, (8 + self.__y * 80, 18 + self.__x * 80))
        m.paste(end, (4 + self.__new_y * 80, 14 + self.__new_x * 80))
        # 再画棋子
        for i in range(0, 10):
            for j in range(0, 9):
                chess = self.map[i][j]
                if chess:  # 如果不为None
                    m.paste(chess.image, (8 + j * 80, 18 + i * 80))
        path = pic_root + self.seed + '.jpg'
        m.save(path)
        return path

    def set_over(self, winner: str):
        if winner:
            if winner == Team.Black:
                self.game_over = Team.Black
            else:
                self.game_over = Team.Red
        else:
            self.game_over = None

    def back_to_last_step(self) -> None:
        if not self.back_is_legal:
            raise BackExcept()
        # 改变轮次
        if self.turn == Turn.Red:
            self.turn = Turn.Black
        else:
            self.turn = Turn.Red
        # 替换棋子
        self.map[self.__x][self.__y] = self.map[self.__new_x][self.__new_y]
        self.map[self.__x][self.__y].update_position(self.__x, self.__y)
        self.map[self.__new_x][self.__new_y] = self.be_eat_chess
        # 更新坐标
        x = self.__x
        y = self.__y
        self.__x = self.__new_x
        self.__y = self.__new_y
        self.__new_x = x
        self.__new_y = y
        # 被吃的棋子
        self.be_eat_chess = None
        # 不能连续悔棋
        self.back_is_legal = False
        # 步数
        self.step -= 1

    def getTotalTime(self) -> str:
        total_second = int(time.time() - self.start_time)
        return get_time_str(total_second)


if __name__ == '__main__':
    m = GameControl().paint_map()
    print(m.filename, m.mode)
