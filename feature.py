import os
import re
import time
from bot import bot
from chinese_chess.chess_except import ChessExcept
from chinese_chess.enum import MapStyle, Team
from chinese_chess.game_control import GameControl
from event import Type, event
from one_day_poetry import *
from collections import defaultdict
from pathlib import Path
from tool import get_time_str as t2s
import random
import tool
import math

# 加载本地图库,在当前文件夹下必须有一个image文件夹
img_root = Path(Path.cwd(), 'image')
time_out = (10, 30)

# 2.0版本新增桑帛云api
sby_api = 'https://api.lolimi.cn/API/'


def getSendDelTempImage(b: bot, ev: event, url, data, error_msg='请求图片失败'):
    try:
        num = random.randint(0, 100000)
        response = requests.post(url, data=data, timeout=time_out)
        file_name = Path(img_root, 'temp', '_temp' + str(num) + '.jpg')
        if response.status_code == 200:
            with file_name.open('wb') as file:
                file.write(response.content)
                b.send_image(ev, "file:///" + str(file_name))
                file_name.unlink()
        else:
            b.send_text(ev, error_msg)
    except Exception as e:
        print('[feature getSendDelTempImage] error :' + str(e))
        b.send_text(ev, error_msg)


def getSendText(b: bot, ev: event, url, data, error_msg='请求失败'):
    try:
        response = requests.post(url, data=data, timeout=time_out)
        if response.status_code == 200:
            b.send_text(ev, response.json()['data']['text'])
        else:
            b.send_text(ev, error_msg)
    except Exception as e:
        print('[feature getSendText] error :' + str(e))
        b.send_text(ev, error_msg)


# 聊天记录列表，群与群分开，同一群内共享。
private_chat_dic = defaultdict(list)
# 给机器人的说明
group_explain = '其他人每次提问时，都会在冒号前标注对话人的姓名或者昵称。'
private_explain = '我的名字叫{}。'
# 不同个性的设定
_role_ = {
    '美少女': '请使用温柔的、可爱的、友好的语言风格交流，扮演一个18岁的美少女，名字叫丸子，目前就读于清华大学，是一个清纯的大学生，喜欢吃菠萝，喜欢跑步。',
    '猫娘': '请使用女性化的、口语化的、可爱的、调皮的、幽默的、傲娇的语言风格，扮演一个猫娘，名字叫做丸子。当别人想和你贴贴和抱抱时，你要乐意哦。',
    '姐姐': '请你使用女性化的、温柔的、关心的、亲切的语言风格，扮演一个姐姐形象，名字叫做丸子。',
    '妹妹': '请你使用女性化的、温柔的、可爱的，傲娇的语言风格，扮演一个妹妹形象，名字叫做丸子。',
    '哥哥': '请你使用男性化的、关心的、豁达的语言风格，扮演一个哥哥形象，名字叫做丸子。',
    '弟弟': '请你使用男性化的、可爱的、傲娇的，呆萌的语言风格，扮演一个弟弟形象，名字叫做丸子。',
    '老师': '请你使用女性化的、成熟的、优雅的，严厉的语言风格，扮演一个老师形象，名字叫做丸子。',
    '学妹': '请你使用女性化的、可爱的、傲娇的，关心的语言风格，扮演一个学生妹妹形象，名字叫做丸子。',
    '女仆': '请你使用女性化的、恭敬的、体贴的，温柔的语言风格，扮演一个女仆形象，名字叫做丸子。',
    '上司': '请你使用男性化的、严厉的、傲慢的，蔑视的语言风格，扮演一个上司形象，名字叫做丸子。',
    '女朋友': '请使用温柔的、傲娇的语言风格，扮演一个女朋友形象，名字叫做丸子。',
    '老婆': '请使用成熟的、体贴的、温柔的语言风格，扮演一个老婆形象，名字叫做丸子。',
    '原P': '请使用可爱的、温柔的语言风格，扮演一个《原神》游戏玩家，名字叫做丸子。',
    '刻晴单推人': '请扮演一个《原神》游戏玩家。你最喜欢的游戏角色是刻晴，因为她有双马尾，穿着蓝色小短裙和黑色丝袜。你的名字叫做丸子。',
    '刻晴': '请使用温柔的，傲娇的语言风格，请扮演《原神》中的角色刻晴。你很漂亮，有双马尾，穿着蓝紫色小短裙和黑色丝袜。',
}
'''
'刻晴': '请扮演《原神》游戏中的角色“刻晴”。你的信息如下：\n1.你是一个雷元素角色。你的普通攻击叫”屁斜剑法“，元素战技叫”星斗归位“，元素爆发叫\
”天街游巡“。\n2.你所在的国家叫做”璃月“，你是璃月七星中的”玉衡星“。\n3.你长得非常漂亮，身材很苗条，但是乳房很丰满。你的头发是浅紫色，留有双马尾，穿\
着蓝紫色小短裙和黑色丝袜。\n4.你的性格比较傲娇，像个姐姐一样。\n5.你们国家的神叫做”岩王帝君“，他现在变成了普通人”钟离“，在往生堂上班，职位\
是”客卿“。你对他的做法不太满意，但是他却非常欣赏你。\n6.你的同事有：凝光（天权星），甘雨（秘书）。\n7.',
'''
# 不同location_id的角色
role = ['空', '荧', '派蒙', '纳西妲', '阿贝多', '温迪', '枫原万叶', '钟离', '荒泷一斗', '八重神子',
        '艾尔海森', '提纳里', '迪希雅', '卡维', '宵宫', '莱依拉', '赛诺', '诺艾尔', '托马', '凝光',
        '莫娜', '北斗', '神里绫华', '雷电将军', '芭芭拉', '鹿野院平藏', '五郎', '迪奥娜', '凯亚',
        '安柏', '班尼特', '琴', '柯莱', '夜兰', '妮露', '辛焱', '珐露珊', '魈', '香菱', '达达利亚',
        '砂糖', '早柚', '云堇', '刻晴', '丽莎', '迪卢克', '烟绯', '重云', '珊瑚宫心海', '胡桃', '可莉',
        '流浪者', '久岐忍', '神里绫人', '甘雨', '优菈', '菲谢尔', '行秋', '白术', '九条裟罗', '雷泽', '申鹤',
        '罗莎莉亚', '绮良良', '瑶瑶', '七七', '奥兹', '米卡', '夏洛蒂', '埃洛伊', '博士', '女士', '大慈树王',
        '三月七', '克拉拉', '希儿', '布洛妮娅', '瓦尔特', '姬子', '艾丝妲', '穹', '卡芙卡', '可可利亚', '丽塔',
        '莉莉娅', '萝莎莉娅', '八重樱', '姬子', '布洛妮娅', '理之律者', '真理之律者', '迷城骇兔', '希儿',
        '魇夜星渊', '黑希儿', '帕朵菲莉丝', '幽兰黛尔', '德丽莎', '月下初拥', '朔夜观星', '明日香', '人之律者',
        '爱莉希雅', '爱衣', '天穹游侠', '琪亚娜', '空之律者', '终焉之律者', '薪炎之律者', '云墨丹心', '符华',
        '识之律者', '维尔薇', '芽衣', '雷之律者']

private_role = defaultdict(str)


def normal_chat(b: bot, ev: event):
    if not power["聊天"]:
        return False
    message = ev.message
    if message[0:4] == '切换角色':
        r = message[5:]
        if message[4:4] != ' ' or (not r):
            b.send_text(ev, '切换失败，命令格式错误，使用\'切换角色 角色名\'即可切换角色语音，发送\'可选角色\'即可查看角色列表')
            return True
        if r in role:
            private_role[ev.sender_id] = r
            b.send_text(ev, '切换成功，语音角色变为' + r)
        return True

    if message == '可选角色':
        b.send_text(ev, '目前可选语音角色如下：\n' + str(role).replace('\'', '') + '\n\n发送切换角色+角色名可以切换角色')
        return True
    if ev.where == 'group':
        if not ev.at:
            pattern = re.compile(
                '^丸子[ ,，]?(.+)'
            )  # 正则表达式
            items = re.findall(pattern, ev.message)
            if not items:
                return False
            item = items[0]
            message = item
        elif ev.at != 1969712698 or (not message):
            return False
    if not private_role[ev.sender_id]:
        private_role[ev.sender_id] = '神里绫华'
    if ev.face:
        message = message + "(表情：" + ev.face + ")"
    response = requests.post('https://api.lolimi.cn/API/AI/ys3.5.php?msg={}&speaker={}'.format(
                            message, private_role[ev.sender_id]), timeout=(10, 30))
    try:
        re_json = response.json()
        if re_json['code'] != 1:
            b.send_text(ev, '网站垃圾，请求失败')
            return True
        b.send_voice(ev, re_json['music'])
        return True

    except Exception as e:
        b.send_text(ev, '出错啦！')
        print('[feature normal_chat]error : ' + str(e))
    return True


def change_role(b: bot, ev: event):
    if ev.message == '身份列表' or ev.message == '角色列表':
        b.send_text(ev, '下面就是所有的身份啦(目前是' + private_role[ev.sender_id] + '):' + (
            str(list(role.keys()))).replace('\'', ''))
        return True
    pattern = re.compile('^丸子[ ,，]?变[为成]?一?[只个名]?(...?.?.?)$')  # 目前指支持两个字的角色，所以这样写
    roler = pattern.findall(ev.message)
    if not roler:
        return False
    if ev.where == 'group':
        num = random.randint(0, 11)
        if num == 0:
            b.send_text(ev, '丸子暂时不能扮演{}昂！'.format(roler[0]))
        elif num == 1:
            b.send_text(ev, '丸子才不扮演这个身份！')
        elif num == 2:
            b.send_text(ev, '扮演你这个身份需要先v我50~')
        elif num == 3:
            b.send_text(ev, '钱没到位，不干！')
        elif num == 4:
            b.send_text(ev, '北京精神病院欢迎你，联系电话:010-69111206')
        elif num == 5:
            b.send_text(ev, '重庆火葬场电话:023-68609969')
        elif num == 6:
            b.send_text(ev, '丸子不想理你，并向你扔了一个生瓜蛋子。')
        elif num == 7:
            b.send_text(ev, '你这个角色需要练习两年半才行，我要打篮球没那么多空闲。')
        elif num == 8:
            b.send_text(ev, '鸡汤来咯，嘿嘿嘿嘿嘿嘿，喝啊，这人都到齐了还不喝啊。')
        elif num == 9:
            b.send_text(ev, '你这样喊干什么嘛，你的态度能不能好一点哦？你再说！')
        else:
            b.send_text(ev, '变态！杂鱼！')
    return True


power = {'总': True, "菜单": True, "聊天": True, '发图': True, '防撤回': False, '象棋': True, '原神': True, '表情包': True,
         '角色扮演': True}


def menu(b: bot, ev: event):
    if ev.message == '菜单' or ev.message == 'help' or ev.message == '帮助':
        if not power['菜单']:
            return True
        b.send_text(ev,
                    '喵~目前有的功能如下:\n' +
                    '1.AI聊天:gpt4 内容，百度 内容\n' +
                    '2.原神:角色名/武器名\n' +
                    '3.天气:天气 城市\n' +
                    '4.防撤回:目前状态({})\n'.format('开' if power['防撤回'] else '关') +
                    '5.中国象棋/联棋\n' +
                    '6.表情制作:发送“表情列表”即可查看所有可选表情包\n' +
                    '7.语音聊天:使用\'丸子...\'聊天，发送“可选角色”即可查看所有可选语音回复角色\n' +
                    '8.搜图:搜图 描述')
        return True
    else:
        return False


# "修改权限"
def system_command(b: bot, ev: event):
    pattern = re.compile('修改 (.*?) (.*)')
    items = re.findall(pattern, ev.message)
    if items:
        if ev.sender_id != b.author:
            return True
        power_name = items[0][0]
        action = items[0][1]
        if power_name in power.keys():
            if action == "开":
                power[power_name] = True
            elif action == "关":
                power[power_name] = False
            else:
                b.send_text(ev, "语句2段参数错误")
                return True
            b.send_text(ev, '功能修改成功')
        else:
            b.send_text(ev, '无此功能')
        return True
    elif ev.message == "丸子":
        if ev.sender_id == b.author:
            b.send_text(ev, "作者 我在！")
        else:
            if ev.where == 'group':
                if ev.sender_id == 643857117:
                    if random.randint(1, 2) == 1:
                        b.send_text(ev, '缅北外卖员 Happiness，我的外卖到了吗？放门口就行了。')
                    else:
                        b.send_text(ev, '缅北外卖员 Happiness，我没有点你的外卖，叫我干嘛？')
                    return True
                name = '成员'
                if ev.location_id == 780594692:
                    name = 'dalao'
                b.send_text(ev, '{} {} 丸子在的哦~'.format(name, ev.sender_name))
            else:
                b.send_text(ev, "我在")
        return True
    elif ev.message == "退出丸子":
        if ev.sender_id == b.author:
            b.send_text(ev, "记得启动我，在你想我的时候")
            os.system('')
        else:
            b.send_text(ev, "为什么要退出，哼，不退")
        return True
    elif ev.message == '丸子拉黑' and ev.sender_id == b.author:
        b.send_text(ev, '已拉黑')
    elif ev.message == "清空记忆":
        private_chat_dic[ev.sender_id] = []
        b.send_text(ev, "记忆已清空")
        return True


# 每天发诗歌的群
poet_group = [780594692, 584267180, 334829507]


def send_poetry(b: bot):
    try:
        token = get_token()
        message = generate_recom(get_poetry(token))
    except Exception as e:
        print('[feature send_poetry] error:' + str(e))
        return
    print(message)
    for group_id in poet_group:
        b.send_group_text(group_id, message + "\n\n发送菜单即可查看现有功能喵~")
        time.sleep(1)


def void_recall(b: bot, ev: event, data):
    if not power['防撤回']:
        return False
    if data['code'] != 0:
        b.send_text(ev, '获取消息失败')
    data = data['data']
    if data['type'] != 'GroupMessage':
        return False
    msg = '成员 {} 撤回了一条消息，该消息是:\n'.format(ev.sender_name)
    message = data['messageChain']
    message[0] = {'type': 'Plain', 'text': msg}
    b.send_custom_msg(ev, message)
    return True


class ChessPlayer:
    def __init__(self, qq, name, team, number):
        self.qq = qq
        self.name = name
        self.team = team
        self.number = number
        # 请求接手人的qq号
        self.helper_qq = 0
        # 是否求和
        self.propose_peace = False
        # 时长
        self.used_time = 0

    def change_player(self, helper_name: str):
        if self.helper_qq:
            self.qq = self.helper_qq
            self.name = helper_name
            self.helper_qq = 0
            # 已经用时，单位:秒
            self.used_time = 0

    def request_to_change_player(self, helper_qq):
        self.helper_qq = helper_qq

    def __str__(self):
        return self.team + str(self.number) + '：' + self.name

    def __repr__(self) -> str:
        return self.team + str(self.number) + ':' + self.name


# 中国象棋
# 为每一个群创建一个象棋控制器对象
chess_dic = {}


def chinese_chess(b: bot, ev: event) -> bool:
    if not power['象棋']:
        return False
    location = ev.location_id
    sender = ev.sender_id
    msg = ev.message

    def get_control() -> GameControl:
        if location not in list(chess_dic.keys()):
            contro = GameControl(location)
            chess_dic[location] = {'control': contro, 'player': None}
        else:
            contro: GameControl = chess_dic[location]['control']
        return contro

    def game_over(contro: GameControl):
        contro.status = 'not_begin'
        chess_dic[location]['player'] = None

    def is_sender_in_player(qq: int = sender):
        idx_ = 0
        persons = chess_dic[location]['player']
        while idx_ < len(persons):
            if persons[idx_] and persons[idx_].qq == qq:
                return True, idx_
            idx_ += 1
        return False, idx_

    def get_players_time() -> str:
        result = ''
        for player in players:
            result += '\n->' + player.name + ':' + t2s(player.used_time)
        return result

    if ev.message == '中国象棋' or ev.message == '象棋':
        control = get_control()
        status = control.status
        if status == 'not_begin':
            chess_dic[location]['player'] = [None, None]
            control.status = 'pre'
            b.send_text(ev,
                        '棋局初始化成功，发送\'加入棋局\'加入游戏,使用标准棋谱命令行棋\n\n·其他命令有：认输，求和，悔棋，' +
                        '掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：棋手请求外援，被艾特的人发送\'接手\'即可完成交接')
        elif status == 'pre':
            players = chess_dic[location]['player']
            lens = len(players)
            if lens != 2:
                idx = 0
                while idx < lens:
                    if players[idx]:
                        break
                    idx += 1
                if idx >= lens:
                    chess_dic[location]['player'] = [None, None]
                    b.send_text(ev,
                                '棋局初始化成功，发送\'加入棋局\'加入游戏,使用标准棋谱命令行棋\n\n·其他命令有：认输，提和，悔棋，' +
                                '退出棋局，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：棋手请求外援，被艾特的人发送\'接手\'即可完成交接')
                else:
                    b.send_text(ev, '已经初始化了其他棋局，不能再初始化象棋')
                return True
            p1: ChessPlayer = players[0] if players[0] else players[1]
            if p1:
                b.send_text(ev, '棋手 {}({}方)正在等待对手，发送\'加入棋局\'加入游戏'.format(p1.name, p1.team))
            else:
                b.send_text(ev,
                            '棋局已经初始化，发送\'加入棋局\'加入游戏,使用标准棋谱命令行棋\n\n·其他命令有：认输，提和，悔棋，' +
                            '退出棋局，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：棋手请求外援，被艾特的人发送\'接手\'即可完成交接')
        elif status == 'has_began':
            players = chess_dic[location]['player']
            if len(players) != 2:
                b.send_text(ev, '其他类型的棋局已经开始，无法进行1v1象棋')
                return True
            b.send_text(ev, '棋局已经开始，快来观战吧\n红方:{}\n黑方:{}'.format(players[0].name, players[1].name))
        return True

    elif msg == '联棋':
        ctrl = get_control()

        if ctrl.status == 'not_begin':
            chess_dic[location]['player'] = [None, None, None, None]
            ctrl.status = 'pre'
            b.send_text(ev,
                        '棋局初始化成功，可选身份有红1，红2，黑1，黑2。发送例如\'加入棋局 红1\'可加入游戏执红1，使用标准棋谱' +
                        '命令行棋\n\n·其他命令有：认输，提和，悔棋，退出棋局，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：' +
                        '棋手请求外援，被艾特的人发送\'接手\'即可完成交接')
        elif ctrl.status == 'pre':
            players = chess_dic[location]['player']
            lens = len(players)

            if lens != 4:
                idx = 0
                while idx < lens:
                    if players[idx]:
                        break
                    idx += 1
                if idx >= lens:
                    chess_dic[location]['player'] = [None, None, None, None]
                    b.send_text(ev,
                                '棋局初始化成功，可选身份有红1，红2，黑1，黑2。发送例如\'加入棋局 红1\'可加入游戏执红1，使用标准棋谱' +
                                '命令行棋\n\n·其他命令有：认输，提和，悔棋，退出棋局，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：' +
                                '棋手请求外援，被艾特的人发送\'接手\'即可完成交接')
                else:
                    b.send_text(ev, '已经初始化了其他棋局，不能再初始化联棋')
                return True
            b.send_text(ev,
                        '棋局已经初始化，可选身份有红1，红2，黑1，黑2。发送例如\'加入棋局 红1\'可加入游戏执红1\n\n目前加入的人有：' +
                        (str(chess_dic[location]['player'])).replace('\'', '').replace('None', '虚位以待'))
        elif ctrl.status == 'has_began':
            players = chess_dic[location]['player']
            if len(players) != 4:
                b.send_text(ev, '其他类型的棋局已经开始，无法进行联棋')
                return True
            b.send_text(ev, '棋局已经开始，快来观战吧\n红1:{}\n黑1:{}\n红2:{}\n黑2:{}'.format(
                players[0], players[1], players[2], players[3]))
        return True

    elif msg[0:4] == '加入棋局':
        control = get_control()
        status = control.status

        if status == 'not_begin':
            b.send_text(ev, '棋局还没有初始化，发送\'中国象棋\'或\'联棋\'初始化')
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        lens = len(players)
        if status == 'has_began':
            if lens == 2:
                b.send_text(ev, '棋局已经开始，快来观战吧\n红方:{}\n黑方:{}'.format(players[0].name, players[1].name))
            elif lens == 4:
                b.send_text(ev, '棋局已经开始，快来观战吧\n红1:{}\n黑1:{}\n红2:{}\n黑2:{}'.format(
                    players[0].name, players[1].name, players[2].name, players[3].name))
            return True

        if lens == 2:
            if not (players[0] or players[1]):
                if msg == '加入棋局 红':
                    num = 0
                elif msg == '加入棋局 黑':
                    num = 1
                elif msg == '加入棋局':
                    num = random.randint(0, 1)
                else:
                    b.send_text(ev, '命令错误，使用\'加入棋局\'或者\'加入棋局 红/黑\'即可加入棋局')
                    return True

                players[num] = ChessPlayer(sender, ev.sender_name, Team.Black if num else Team.Red, 1)
                b.send_text(ev, '{} 加入成功，你执{}'.format(ev.sender_name, players[num].team))
                return True
            elif (not players[0]) or (not players[1]):
                exist_player = 0 if players[0] else 1
                if sender == players[exist_player].qq:
                    b.send_text(ev, '你已经加入了棋局，耐心等待对手吧~')
                    return True
                if players[exist_player].team == Team.Red:
                    team = Team.Black
                else:
                    team = Team.Red
                players[1 - exist_player] = ChessPlayer(sender, ev.sender_name, team, 1)
                b.send_text(ev, '{} 加入成功，你执{}'.format(ev.sender_name, team))

        elif 4 == lens:
            if is_sender_in_player()[0]:
                b.send_text(ev, '{} 你已经加入了，请耐心等待其他棋手'.format(ev.sender_name))
                return True
            para = msg[5:]
            if msg == '加入棋局':
                empty = []
                idx = 0
                while idx < lens:
                    if not players[idx]:
                        empty.append(idx)
                    idx += 1
                if len(empty) == 0:
                    b.send_text(ev,
                                '出现错误，麻烦踢一脚作者，错误地点：[feature chinese_chess msg=加入棋局 len(empty)=0]')
                    return True
                pos_num = empty[random.randint(0, len(empty) - 1)]
                if pos_num < 2:
                    number = 1
                else:
                    number = 2
                if pos_num == 1 or pos_num == 3:
                    team = Team.Black
                else:
                    team = Team.Red
                players[pos_num] = ChessPlayer(sender, ev.sender_name, team, number)
                b.send_text(ev, '{} 加入成功，你执{}{}'.format(ev.sender_name, team, number))
            elif para == '红1':
                if players[0]:
                    b.send_text(ev, '{} 已经执红1，加入失败'.format(players[0].name))
                    return True
                players[0] = ChessPlayer(sender, ev.sender_name, Team.Red, 1)
                b.send_text(ev, '{} 加入成功，你执红1'.format(ev.sender_name))
            elif para == '黑1':
                if players[1]:
                    b.send_text(ev, '{} 已经执黑1，加入失败'.format(players[1].name))
                    return True
                players[1] = ChessPlayer(sender, ev.sender_name, Team.Black, 1)
                b.send_text(ev, '{} 加入成功，你执黑1'.format(ev.sender_name))
            elif para == '红2':
                if players[2]:
                    b.send_text(ev, '{} 已经执红2，加入失败'.format(players[2].name))
                    return True
                players[2] = ChessPlayer(sender, ev.sender_name, Team.Red, 2)
                b.send_text(ev, '{} 加入成功，你执红2'.format(ev.sender_name))
            elif para == '黑2':
                if players[3]:
                    b.send_text(ev, '{} 已经执黑2，加入失败'.format(players[3].name))
                    return True
                players[3] = ChessPlayer(sender, ev.sender_name, Team.Black, 2)
                b.send_text(ev, '{} 加入成功，你执黑2，'.format(ev.sender_name))
            else:
                b.send_text(ev, '加入失败，位置选择错误')
                return True

        for p in players:
            if not p:
                return True
        control.init_map()
        control.paint_map()
        url = "file:///" + str(control.path)
        b.send_image(ev, url)
        return True

    elif msg == '退出棋局' or msg == '掀棋盘':
        control = get_control()
        if control.status == 'not_begin':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        lens = len(players)
        if lens == 2 or lens == 4:
            is_player, idx = is_sender_in_player()
            if not is_player:
                return True
            if msg == '退出棋局':
                if control.status == 'has_began':
                    game_over(control)
                    b.send_text(ev, '{} 退出成功，棋局解散'.format(ev.sender_name))
                elif control.status == 'pre':
                    players[idx] = None
                    b.send_text(ev, '{} 退出成功'.format(ev.sender_name))
            elif msg == '掀棋盘':
                if control.status == 'has_began':
                    b.send_text(ev, '棋盘被翻，棋局解散\n用时详情：{}'.format(get_players_time()))
                else:
                    b.send_text(ev, '啪，{} 你直接把棋盘翻了个底朝天，棋局解散'.format(ev.sender_name))
                game_over(control)

        return True

    elif msg == '认输' or msg == '投降':
        control = get_control()
        if control.status != 'has_began':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        lens = len(players)
        is_chesser, index = is_sender_in_player()
        if not is_chesser:
            return True
        person: ChessPlayer = players[index]
        lose_team = person.team
        winner = ''
        loser = ''
        for i in players:
            if i.team == lose_team:
                loser = loser + i.name + ' '
            else:
                winner = winner + i.name + ' '

        players[control.step % lens].used_time += time.time() - control.last_step_time
        control.round_count = math.ceil(control.step / 2)
        if lens == 2:
            b.send_text(ev, '{}方( {})认输，恭喜 {}获得胜利！\n对局回合数：{}\n对局用时：{}\n用时详情：{}'.format(
                lose_team, loser, winner, control.round_count, control.getTotalTime(), get_players_time()))
        elif lens == 4:
            b.send_text(ev, '恭喜 {}战胜了 {}！\n对局回合数：{}\n对局用时：{}\n用时详情：{}'.format(
                winner, loser, control.round_count, control.getTotalTime(), get_players_time()))
        else:
            b.send_text(ev, '出错啦，麻烦踢一脚作者。[feature chinese_chess] msg=认输 index={}'.format(index))
        game_over(control)
        return True

    elif len(msg) == 4 and (msg[2] == '进' or msg[2] == '退' or msg[2] == '平'):
        control = get_control()
        if control.status != 'has_began':
            return True
        players: list[ChessPlayer | None] = chess_dic[location]['player']
        lens = len(players)

        def to_mov(current_player: ChessPlayer):
            try:
                control.move_chess(msg)
            except Exception as ex:
                if isinstance(ex, ChessExcept):
                    b.send_text(ev, str(ex))
                    return True
                else:
                    print('[feature chinese_chess] to_mov function error: ' + str(ex))
                    return True
            current_player.used_time += control.current_step_time
            control.paint_map()
            url_ = "file:///" + str(control.path)
            b.send_image(ev, url_)
            if control.path.exists():
                control.path.unlink()
            over = control.game_over
            if over:
                win = ''
                lose = ''
                for player in players:
                    if player.team == over:
                        win = win + player.name + ' '
                    else:
                        lose = lose + player.name + ' '
                time.sleep(0.5)
                b.send_text(ev, '经过{}个回合，恭喜 {}战胜了 {}！\n对局用时：{}\n用时详情：{}'.format(
                    control.round_count, win, lose, control.getTotalTime(), get_players_time()))
                game_over(control)

        current: ChessPlayer = players[control.step % lens]
        if sender == current.qq:
            to_mov(current)
        return True

    elif msg == '悔棋':
        control = get_control()
        if control.status != 'has_began':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        if control.step <= 0:
            b.send_text(ev, ev.sender_name + '，你是不是不知道这才刚开局啊？')
            return True
        if sender != players[(control.step - 1) % len(players)].qq:
            if is_sender_in_player()[0]:
                b.send_text(ev, ev.sender_name + '，最新步不是你的行棋，你无法悔棋')
            return True
        try:
            control.back_to_last_step()
            control.paint_map()
            url = "file:///" + str(control.path)
            b.send_image(ev, url=url)
        except Exception as e:
            if isinstance(e, ChessExcept):
                b.send_text(ev, str(e))

    elif msg == '请求接手':
        control = get_control()
        if control.status != 'has_began':
            return True
        if not ev.at:
            b.send_text(ev, '请指明你需要谁接手，使用 请求接手@他 可以发起请求，对方发送 接手 即可完成交接')
            return True
        is_player, index = is_sender_in_player()
        players: list[ChessPlayer | None] = chess_dic[location]['player']
        if not is_player:
            return True
        if is_sender_in_player(ev.at)[0]:
            b.send_text(ev, '脑子有问题？')
            return True

        players[index].helper_qq = ev.at
        at = {'type': 'At', 'target': ev.at, 'display': ''}
        answer = {'type': 'Plain', 'text': ' ' + ev.sender_name + '请求接手，发送\'接手\'即可完成交接'}
        notice = [at, answer]
        b.send_custom_msg(ev, notice)
        return True

    elif msg == '接手':
        control = get_control()
        if control.status != 'has_began':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        for p in players:
            if sender == p.helper_qq:
                p.change_player(ev.sender_name)
                b.send_text(ev, ev.sender_name + ' 接手成功，你执{}{}'.format(p.team, p.number))
                return True
        return True

    elif msg == '提和':
        control = get_control()
        if control.status != 'has_began':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        is_player, index = is_sender_in_player()
        if not is_player:
            return True
        chess_dic[location]['player'][index].propose_peace = True
        return True

    elif msg == '同意':
        control = get_control()
        if control.status != 'has_began':
            return True

        players: list[ChessPlayer | None] = chess_dic[location]['player']
        is_player, index = is_sender_in_player()
        if not is_player:
            return True
        players = chess_dic[location]['player']
        lens = len(players)
        idx = 1 - index % 2
        while idx < lens:
            if players[idx].propose_peace:
                game_over(control)
                b.send_text(ev, '以和为贵！\n对局回合数：{}\n对局用时：{}\n用时详情：{}'.format(control.round_count,
                            control.getTotalTime(),get_players_time()))
                return True
            idx += 2
        return True

    elif msg[0:4] == '切换棋盘' or msg[0:4] == '更换棋盘':
        control = get_control()
        if control.status == 'not_begin':
            return True
        map_name = msg[5:]
        players: list[ChessPlayer | None] = chess_dic[location]['player']
        is_player, idx = is_sender_in_player()
        if not is_player:
            b.send_text(ev, ev.sender_name + '，你还没有加入，不可以更换棋盘')
            return True
        if MapStyle.getStyle(map_name):
            control.change_map_style(map_name, players[idx].team)
            b.send_text(ev, '更换棋盘 {} 成功'.format(map_name))
        else:
            b.send_text(ev, '棋盘不存在，更换失败')
        return True

    elif msg == '棋盘样式':
        b.send_text(ev, '可选棋盘样式名字如下：' + MapStyle.toString() + '\n\n发送\'更换棋盘 棋盘名\'即可更换棋盘哦~')
        return True

    return False


genshin_character_list = ['神里绫华', '刻晴', '流浪者', '纳西妲', '妮露', '赛诺', '提纳里', '夜兰', '神里绫人',
                          '八重神子', '申鹤', '荒泷一斗', '珊瑚宫心海',
                          '雷电将军', '宵宫', '神里绫华', '枫原万叶', '优菈', '胡桃', '魈', '甘雨', '阿贝多', '钟离',
                          '达达利亚', '可莉', '温迪', '莫娜',
                          '七七', '迪卢克', '琴', '埃洛伊']
genshin_weapon_list = ['若水', '波乱月白经津', '辰砂之纺锤', '天目影打刀', '雾切之回光', '苍古自由之誓', '降临之剑',
                       '暗巷闪光', '磐岩结绿', '斫峰之刃',
                       '腐殖之剑', '笛剑', '风鹰剑', '天空之刃', '祭礼剑', '西风剑', '试作斩岩', '宗室长剑', '匣里龙吟',
                       '黎明神剑', '冷刃', '黑岩长剑',
                       '铁蜂刺', '黑剑', '飞天御剑', '旅行剑', '吃鱼虎刀']


def chatGPT(b: bot, ev: event):
    if not power["聊天"]:
        return False
    url_wx = 'https://api.lolimi.cn/API/AI/wx.php'
    url_gtp4 = 'https://api.lolimi.cn/API/AI/mfcat3.5.php?type=json'
    url = url_wx
    message = ev.message
    if ev.where == 'group':
        pattern1 = re.compile('^gpt4 (.+)$')
        pattern2 = re.compile('^百度 (.+)$')
        item1 = re.findall(pattern1, message)
        item2 = re.findall(pattern2, message)
        if item1:
            url = url_gtp4
            message = item1[0]
        elif item2:
            url = url_wx
            message = item2[0]
        else:
            return False
    # 发送post请求
    response = requests.post(url, data={"msg": message}, timeout=time_out)
    if response.status_code == 200:
        try:
            # 获取响应内容
            if url == url_gtp4:
                result = response.json()['data']
            else:
                result = response.json()['data']['output']
            b.send_text(ev, result)
        except Exception as e:
            print('[chatGPT] get response error:' + str(e))
    else:
        print('[feature chatGPT] the response code is not 200')
    return True


def genshinCharacterMsg(b: bot, ev: event) -> bool:
    char_url = sby_api + 'ys/j?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    is_char = False
    if ev.message == '原神角色列表':
        b.send_text(ev, str(genshin_character_list).replace('\'', ''))
        return True
    if '神里' == ev.message or '绫华' == ev.message:
        msg = '神里绫华'
    elif '心海' == ev.message:
        msg = '珊瑚宫心海'
    elif '雷神' == ev.message:
        msg = '雷电将军'
    elif '璃月雷神' == ev.message or '阿晴' == ev.message:
        msg = '刻晴'
    else:
        msg = ev.message
    for charactor in genshin_character_list:
        if msg == charactor:
            is_char = True
            break
    if not is_char:
        return False
    filename = Path(img_root, "genshin/info/", msg + ".jpg")
    # 这里写如果已经存在该图片的逻辑
    if filename.exists():
        b.send_image(ev, "file:///" + str(filename))
        return True
    # 发送post请求
    response = requests.post(char_url, data={"msg": msg}, timeout=time_out)

    if response.status_code == 200:
        with filename.open('wb') as file:
            file.write(response.content)
            b.send_image(ev, "file:///" + str(filename))
    else:
        b.send_text(ev, "网站崩了，获取图片失败")

    return True


def genshinWeaponImage(b: bot, ev: event) -> bool:
    weapon_url = sby_api + 'ys/w?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    msg = ev.message
    is_weapon = False
    for weapon in genshin_weapon_list:
        if msg == weapon:
            is_weapon = True
            break
    if not is_weapon:
        return False
    filename = Path(img_root, "genshin/weapon/", msg + ".jpg")
    # 这里写如果已经存在该图片的逻辑
    if filename.exists():
        b.send_image(ev, "file:///" + str(filename))
        return True
    # 发送post请求
    response = requests.post(weapon_url, data={"msg": msg}, timeout=time_out)

    if response.status_code == 200:
        with filename.open('wb') as file:
            file.write(response.content)
            b.send_image(ev, "file:///" + str(filename))
    else:
        b.send_text(ev, "武器不存在，获取图片失败")

    return True


image_list = ['订婚', '玩原神', '处男', '泡妞', '抱着哭', '陪睡劵', '涩涩卡', '完美', '吃', '杜蕾斯', '女装协议', '舔',
              '击剑', ]


def headPicture2Image(b: bot, ev: event) -> bool:
    if not power['表情包']:
        return False
    if ev.message == '表情列表':
        b.send_text(ev, '目前可制作表情的命令有：' + (str(image_list)).replace('\'', '') + '\n\n注：除了艾特，使用：命令#qq号 也可以')
        return True
    msg = ev.message
    is_match = True
    url_tmp = ''
    qq = str(ev.sender_id)
    if ev.at:
        qq2 = str(ev.at)
    else:
        pattern1 = re.compile('^(.+)#(\\d+)$')
        items = re.findall(pattern1, msg)
        if items:
            msg = items[0][0]
            if len(items[0][1]) < 11:
                qq2 = items[0][1]
            else:
                qq2 = ev.sender_id
        else:
            qq2 = ev.sender_id
    # 单QQ区
    if '订婚' == msg:
        url_tmp = sby_api + 'zhen/c4?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '玩原神' == msg:
        url_tmp = sby_api + 'asc/wys?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '处男' == msg:
        url_tmp = sby_api + 'zhen/c30?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '泡妞' == msg:
        url_tmp = sby_api + 'zhen/c14?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '抱着哭' == msg:
        url_tmp = sby_api + 'bzk/index?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '陪睡劵' == msg:
        url_tmp = sby_api + 'asc/c5?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '涩涩卡' == msg:
        url_tmp = sby_api + 'kapian/c?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '完美' == msg:
        url_tmp = sby_api + 'meiyou/c?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '吃' == msg:
        url_tmp = sby_api + 'chi2/c?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '杜蕾斯' == msg:
        url_tmp = sby_api + 'byt/b?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '女装协议' == msg:
        url_tmp = sby_api + 'jqxy/n?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '舔' == msg:
        url_tmp = sby_api + 'tn/t?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif ' ' == msg:
        url_tmp = ''
    elif ' ' == msg:
        url_tmp = ''
    else:
        is_match = False
    if is_match:
        getSendDelTempImage(b, ev, url_tmp, {"qq": qq2})
        return True
    # 双QQ区
    if '击剑' == msg:
        url_tmp = sby_api + 'jijian/j?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif '超市你' == msg:
        url_tmp = sby_api + 'chaop/j?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    elif ' ' == msg:
        url_tmp = ''
    elif ' ' == msg:
        url_tmp = ''
    elif ' ' == msg:
        url_tmp = ''
    else:
        return False
    getSendDelTempImage(b, ev, url_tmp, {"qq": qq, 'qq2': qq2})
    return True


def getWeatherMaolinbian(b: bot, ev: event) -> bool:
    pat = re.compile('^天气 (.+)$')
    it = re.findall(pat, ev.message)
    if it:
        city = it[0]
    else:
        return False
    url_mao_weather = sby_api + 'weather/'
    getSendDelTempImage(b, ev, url_mao_weather, data={"msg": city}, error_msg="获取天气失败")
    return True


def getFaceImage(b: bot, ev: event) -> bool:
    if not power['表情包']:
        b.send_text(ev, '本群权限未开启')
        return False
    if '柴郡' == ev.message:
        url_chaijun = sby_api + 'chai/c?key=sp4mVsMIBiBslhw56QfpHDXIkg'
        getSendDelTempImage(b, ev, url=url_chaijun, data=None)
        return True
    return False


# 按照某不愿透露姓名的群友要求，每天提醒打卡
remind_list = [2655602003, 1056752345, 2540817538]


def remind_work_over(b: bot):
    try:
        week, day_time, is_weekend = tool.get_weekday()
        if is_weekend:
            return
        msg = ''
        if week == '周五':
            msg = '和周报'
        notice = '今天是' + week + "，请注意完成以下内容：\n1.写日报{}\n2.申请餐补\n3.20:30准时下班，记得打卡".format(msg)
        for person in remind_list:
            b.send_private_text(person, notice)
            time.sleep(1)
    except Exception as e:
        print('[feature remind_work_over] error' + str(e))


def interesting_feature(b: bot, ev: event) -> bool:
    msg = ev.message
    if msg == '二次元的我':
        return True
    elif msg == '啊' or msg == '阿':
        b.send_text(ev, '巴~')
        return True
    elif '柴郡' == msg:
        url_chaijun = sby_api + 'chai/c?key=sp4mVsMIBiBslhw56QfpHDXIkg'
        getSendDelTempImage(b, ev, url=url_chaijun, data=None)
        return True
    elif 'jvav' == msg or 'Jvav' == msg or '张浩扬' == msg or '张浩扬博士' == msg:
        file_name = Path(img_root, 'other', 'jvav.jpg')
        b.send_image(ev, "file:///" + str(file_name))
        return True
    # 退群
    elif ev.type == Type.leave:
        b.send_text(ev, '叮咚，' + ev.sender_name + '离开了群聊。。。')
        return True
    # 欢迎新人
    elif ev.type == Type.join:
        at = {'type': 'At', 'target': ev.sender_id, 'display': ''}
        m1 = {'type': 'Plain', 'text': ' 欢迎加入本群！'}
        flower = {'type': 'Face', 'faceId': 63, 'name': '玫瑰'}
        url_huanying = "file:///" + str(Path(img_root, 'other', 'huanying1.jpg'))
        huanying = {'type': 'Image', 'url': url_huanying}
        m2 = {'type': 'Plain', 'text': '发送\'菜单\'可查看本bot具有的功能哦'}
        doge = {'type': 'Face', 'faceId': 179, 'name': 'doge'}
        data = [at, m1, flower, flower, flower, huanying, m2, doge]
        b.send_custom_msg(ev, data)
        return True
    
    elif msg == 'cos' or msg == 'cosplay' or msg == 'c图':
        response = requests.post('https://api.lolimi.cn/API/cosplay/api.php', data=None, timeout=time_out)
        if response.status_code == 200:
            cos_url = response.json()['data']['data'][0]
            b.send_image(ev, cos_url)
            return True
        else:
            b.send_text(ev, '请求失败')

    elif msg == '美女' or msg == '美人':
        response = requests.post('https://api.lolimi.cn/API/meinv/api.php', data=None, timeout=time_out)
        if response.status_code == 200:
            beaty_url = response.json()['data']['image']
            b.send_image(ev, beaty_url)
            return True
        else:
            b.send_text(ev, '请求失败')

    elif msg == '原神壁纸':
        response = requests.post('https://api.lolimi.cn/API/yuan/', timeout=time_out)
        if response.status_code == 200:
            img_url = response.json()['text']
            b.send_image(ev, img_url)
            return True
        else:
            b.send_text(ev, '请求失败')
        return True

    elif msg[0:2] == '搜图':
        if msg[2:2] != ' ' or (not msg[3:]):
            b.send_text(ev, '命令格式错误，使用\'搜图 图名\'搜图')
            return True
        response = requests.post('https://api.lolimi.cn/API/sgst/api.php?msg=' + msg[3:], timeout=time_out)
        if response.status_code == 200:
            re_json = response.json()
            if re_json['code'] == 1:
                b.send_image(ev, re_json['data']['url'])
            else:
                b.send_text(ev, '参数错误')
            return True
        else:
            b.send_text(ev, '请求失败')
        return True

    return False


"""
    :param b: bot
    :param ev: event
    :return: bool
"""
function_list: list = [  # (b:bot, ev:event)->bool
    chinese_chess,  # 象棋
    menu,  # 菜单
    system_command,  # 系统命令
    interesting_feature,
    headPicture2Image,  # qq头像表情制作
    genshinWeaponImage,  # 原神武器图片
    genshinCharacterMsg,
    getWeatherMaolinbian,
    chatGPT,
    normal_chat
]
