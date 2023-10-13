import math
import random
import re
import time
from tool import get_time_str, work_dir
from chinese_chess.chess_except import ChessNotFindExcept, BackExcept
from chinese_chess.chesses import *
from chinese_chess.enum import *
from pathlib import Path
from PIL import Image


class Status:
    not_begin = 'not_begin'
    pre = 'pre'
    has_began = 'has_began'


class GameControl:
    def __init__(self, seed: int = random.randint(0, 10000)):
        # 空棋盘
        # 实时棋盘，是一个二维的列表，列表里面是棋子对象的引用，没有棋子的地方是None。通过str(棋子对象的引用)获取其中的名字，格式为红/黑+棋子名字（注意红黑方的部分棋子名称不同）
        # 绘制棋盘也是读取这个二维列表的数据，通过棋子对象的引用.pos访问棋子坐标，如 引用.pos.x可以访问x坐标（坐标从0开始）
        self.map: list[list[Chess | None]] = [[None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None],
                                              [None, None, None, None, None, None, None, None, None]]

        # 棋盘风格
        self.red_map_style = MapStyle.default
        self.black_map_style = MapStyle.default
        # 棋子风格
        self.red_chess_style = ChessStyle.default
        self.black_chess_style = ChessStyle.default
        # 棋盘路径
        self.map_dir = Path(work_dir, 'chinese_chess', 'image', 'map')
        # 棋子路径
        self.chess_dir = Path(work_dir, 'chinese_chess', 'image', 'chess')
        # 提示路径
        self.reminder_dir = Path(work_dir, 'chinese_chess', 'image', 'move_remind')
        # 是否盲棋
        self.blind_chess: bool = False
        # 棋子对象池,所有棋盘共享,类的内部可访问，外部无法访问。只读不改。
        self.__chess_list = [
            # -------------黑方初始化------------------
            Car(Team.Black, 0, 0, Path(self.chess_dir, self.black_chess_style, 'black_rook.png')),
            Horse(Team.Black, 0, 1, Path(self.chess_dir, self.black_chess_style, 'black_knight.png')),
            Elephant(Team.Black, 0, 2, Path(self.chess_dir, self.black_chess_style, 'black_elephant.png')),
            Guard(Team.Black, 0, 3, Path(self.chess_dir, self.black_chess_style, 'black_mandarin.png')),
            Commander(Team.Black, 0, 4, Path(self.chess_dir, self.black_chess_style, 'black_king.png')),
            Guard(Team.Black, 0, 5, Path(self.chess_dir, self.black_chess_style, 'black_mandarin.png')),
            Elephant(Team.Black, 0, 6, Path(self.chess_dir, self.black_chess_style, 'black_elephant.png')),
            Horse(Team.Black, 0, 7, Path(self.chess_dir, self.black_chess_style, 'black_knight.png')),
            Car(Team.Black, 0, 8, Path(self.chess_dir, self.black_chess_style, 'black_rook.png')),
            Artillery(Team.Black, 2, 1, Path(self.chess_dir, self.black_chess_style, 'black_cannon.png')),
            Artillery(Team.Black, 2, 7, Path(self.chess_dir, self.black_chess_style, 'black_cannon.png')),
            Soldier(Team.Black, 3, 0, Path(self.chess_dir, self.black_chess_style, 'black_pawn.png')),
            Soldier(Team.Black, 3, 2, Path(self.chess_dir, self.black_chess_style, 'black_pawn.png')),
            Soldier(Team.Black, 3, 4, Path(self.chess_dir, self.black_chess_style, 'black_pawn.png')),
            Soldier(Team.Black, 3, 6, Path(self.chess_dir, self.black_chess_style, 'black_pawn.png')),
            Soldier(Team.Black, 3, 8, Path(self.chess_dir, self.black_chess_style, 'black_pawn.png')),
            # -------------红方初始化------------------
            Car(Team.Red, 9, 0, Path(self.chess_dir, self.black_chess_style, 'red_rook.png')),
            Horse(Team.Red, 9, 1, Path(self.chess_dir, self.black_chess_style, 'red_knight.png')),
            Elephant(Team.Red, 9, 2, Path(self.chess_dir, self.black_chess_style, 'red_elephant.png')),
            Guard(Team.Red, 9, 3, Path(self.chess_dir, self.black_chess_style, 'red_mandarin.png')),
            Commander(Team.Red, 9, 4, Path(self.chess_dir, self.black_chess_style, 'red_king.png')),
            Guard(Team.Red, 9, 5, Path(self.chess_dir, self.black_chess_style, 'red_mandarin.png')),
            Elephant(Team.Red, 9, 6, Path(self.chess_dir, self.black_chess_style, 'red_elephant.png')),
            Horse(Team.Red, 9, 7, Path(self.chess_dir, self.black_chess_style, 'red_knight.png')),
            Car(Team.Red, 9, 8, Path(self.chess_dir, self.black_chess_style, 'red_rook.png')),
            Artillery(Team.Red, 7, 1, Path(self.chess_dir, self.black_chess_style, 'red_cannon.png')),
            Artillery(Team.Red, 7, 7, Path(self.chess_dir, self.black_chess_style, 'red_cannon.png')),
            Soldier(Team.Red, 6, 0, Path(self.chess_dir, self.black_chess_style, 'red_pawn.png')),
            Soldier(Team.Red, 6, 2, Path(self.chess_dir, self.black_chess_style, 'red_pawn.png')),
            Soldier(Team.Red, 6, 4, Path(self.chess_dir, self.black_chess_style, 'red_pawn.png')),
            Soldier(Team.Red, 6, 6, Path(self.chess_dir, self.black_chess_style, 'red_pawn.png')),
            Soldier(Team.Red, 6, 8, Path(self.chess_dir, self.black_chess_style, 'red_pawn.png'))
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
        # 图片保存地址
        self.path = Path(work_dir, 'chinese_chess', 'image', 'temp', self.seed + '.jpg')
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
        for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            for j in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
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
        def chess_name_transform(name) -> str:
            chess_name_right = name
            # 棋子红黑转化
            if name == '相' and self.turn == Turn.Black:
                chess_name_right = '象'
            elif name == '象' and self.turn == Turn.Red:
                chess_name_right = '相'
            if name == '兵' and self.turn == Turn.Black:
                chess_name_right = '卒'
            elif name == '卒' and self.turn == Turn.Red:
                chess_name_right = '兵'
            if name == '仕' and self.turn == Turn.Black:
                chess_name_right = '士'
            elif name == '士' and self.turn == Turn.Red:
                chess_name_right = '仕'
            return chess_name_right

        if right1:
            chess_name = chess_name_transform(command[0])
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
            chess_name = chess_name_transform(command[1])
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
        # 棋盘
        if self.turn == Turn.Red:
            pic = Image.open(Path(self.map_dir, self.red_map_style, 'map_red.jpg')).convert('RGB')
        else:
            pic = Image.open(Path(self.map_dir, self.black_map_style, 'map_black.jpg')).convert('RGB')
        # 先画位置提示:
        if self.turn == Turn.Red:
            begin = Image.open(Path(self.reminder_dir, 'default', 'black_begin.png'))
            end = Image.open(Path(self.reminder_dir, 'default', 'black_end.png'))
            pic.paste(begin, (8 + self.__y * 80, 18 + self.__x * 80), begin)
            pic.paste(end, (4 + self.__new_y * 80, 14 + self.__new_x * 80), end)
        else:
            begin = Image.open(Path(self.reminder_dir, 'default', 'red_begin.png'))
            end = Image.open(Path(self.reminder_dir, 'default', 'red_end.png'))
            pic.paste(begin, (8 + (8 - self.__y) * 80, 18 + (9 - self.__x) * 80), begin)
            pic.paste(end, (4 + (8 - self.__new_y) * 80, 14 + (9 - self.__new_x) * 80), end)
        # 再画棋子
        for row in self.map:
            for chess in row:
                if chess:  # 如果不为None
                    img = chess.image
                    if self.turn == Turn.Black:
                        y = 8 - chess.pos.y
                        x = 9 - chess.pos.x
                        pic.paste(img, (8 + y * 80, 18 + x * 80), img)
                    else:
                        pic.paste(img, (8 + chess.pos.y * 80, 18 + chess.pos.x * 80), img)
        pic.save(self.path)

    def set_over(self, winner: str):
        self.round_count = math.ceil(self.step / 2)
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

    def change_map_style(self, style: str, team: str):
        if team == Team.Red:
            self.red_map_style = style
        else:
            self.black_map_style = style

        print('set map',team, style)

    def change_chess_style(style: ChessStyle, team: Team):
        pass

