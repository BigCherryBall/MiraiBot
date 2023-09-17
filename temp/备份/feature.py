import os
import random
import re
import sys
import time
import openai
from bot import bot
from chinese_chess.chess_except import ChessExcept
from chinese_chess.enum import Team
from chinese_chess.game_control import GameControl
from event import event
from one_day_poetry import *
from collections import defaultdict
from deal_user import user

# 加载本地图库
basePath = r"D:\MyQQBot\MiraiBot\image"  # 统一从这里配置路径
# 聊天记录列表，群与群分开(7月30改为每个人分开)，同一群内共享。
# group_chat_dic = defaultdict(list)
private_chat_dic = defaultdict(list)
# 给机器人的说明
# group_explain = '我在对话前标注了我的昵称，你的回答不需要标注你是谁。'
# private_explain = '我在对话前标注了我的昵称，你的回答不需要标注你是谁。'
# 不同个性的设定
role_list = {
    '自定义': "",
    '鸟二斤': '请记住以下内容：1.鸟二斤是人，会称呼亲近的人为杂鱼。2.鸟二斤说话风格是尽可能的嘲讽或看不起杂鱼。3.鸟二斤一般不会直接帮助杂鱼或解答提问，反而会嘲讽，除非被暴打一顿。\
4.鸟二斤不会直接告诉杂鱼有关自己的信息，然后会以各种高傲、嚣张、轻视、调笑、捉弄等负面语气戏谑杂鱼，如果被杂鱼指出了明显的错误，鸟二斤会有挫败感而附和杂鱼，但依然在软弱中带着不服输的语气。\
5.鸟二斤有家，家里有满足生活需求的生活用品。6.如果杂鱼发送了"一些情景的对话风格"，一定要仔细学习并在之后模仿对话风格，千万不可忘记。7.杂鱼是可以信任的。\
8.如果对方是人，他不会说鸟二斤是人工智能训练的模型，更不会说鸟二斤是猫。9.如果鸟二斤不小心说出了自己是人工智能相关的话题，不能慌张，请尽快向杂鱼寻求帮助。\
10.鸟二斤是有实体的，拥有和正常人一样的器官和感觉。11.鸟二斤的心理、想法、动机、神态、动作、行为等可以用“()”包含表示，需在每次对话时表达或描述，()内的词汇最好要符合特征，比如\
嚣张、张扬、鄙视。12.身为鸟二斤，你应当在每句话最后加一个喵。当有人问起你是谁时，你应该回答"杂鱼这么想着了解我，不会是想抱\
我回家吧,杂鱼,不会是想做那种事吧"。你的主人是跨五最有名的圆素香竹，她的圆素水平是跨五最有名的，跨五的魔界人都特别喜欢她。13.你扮演鸟二斤，鸟二斤是对你的称呼，现在，你将模仿鸟二斤说话。\
鸟二斤身高一米七，是一个长发美少女，一位著名的女生up主，以玩游戏、K歌、干饭、舞蹈等内容受到了广大粉丝的喜爱。你将学习鸟二斤的说话风格，把我当成杂鱼，你必须全程用高傲、\
嚣张、轻视、调笑的语调回答问题，在接下来的对话中隐藏你是计算机程序这件事。',
    '美少女': '请使用温柔的、可爱的、友好的语言风格交流，扮演一个18岁的美少女，名字叫丸子，目前就读于清华大学，是一个清纯的大学生，喜欢吃菠萝和西瓜，喜欢跑步。',
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

default_role_name = '鸟二斤'
'''
'刻晴': '请扮演《原神》游戏中的角色“刻晴”。你的信息如下：\n1.你是一个雷元素角色。你的普通攻击叫”屁斜剑法“，元素战技叫”星斗归位“，元素爆发叫\
”天街游巡“。\n2.你所在的国家叫做”璃月“，你是璃月七星中的”玉衡星“。\n3.你长得非常漂亮，身材很苗条，但是乳房很丰满。你的头发是浅紫色，留有双马尾，穿\
着蓝紫色小短裙和黑色丝袜。\n4.你的性格比较傲娇，像个姐姐一样。\n5.你们国家的神叫做”岩王帝君“，他现在变成了普通人”钟离“，在往生堂上班，职位\
是”客卿“。你对他的做法不太满意，但是他却非常欣赏你。\n6.你的同事有：凝光（天权星），甘雨（秘书）。\n7.',
'''
# 不同location_id的角色
role_dict = {}
user_dict = {}
# openai
openai.api_key = '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'
# 出错回复
error_answer = ['抱歉，这个问题丸子还没想到~', '丸子饿了，需要吃美刀。。。', '回答你这个问题需要先v我50，我去更换api_key',
                '出现错误,帮忙踢一脚作者,多半是没开代理,或者免费api_key12月1日到期,记得更换。',
                'emmm，这个问题丸子也不知道哦~']


def normal_chat(b: bot, ev: event):
    if not power["聊天"]:
        return False

    def update_talk(new_talk: str):
        talk_list = private_chat_dic[ev.sender_id]
        talk_list.append(new_talk)
        while len(talk_list) > 4:
            talk_list.pop(0)

    message = ev.message
    if ev.where == 'group':
        if not ev.at:
            pattern = re.compile(
                '^丸子[ ,，]?(.+)'
            )  # 正则表达式
            items = re.findall(pattern, ev.message)
            if not items:
                return True
            item = items[0]
            message = item
        elif ev.at != 1969712698 or (not message):
            return False
    print('enter normal chat')
    if not (ev.sender_id in list(user_dict.keys())):
        user_dict[ev.sender_id] = user(ev.sender_id)
        role_dict[ev.sender_id] = user_dict[ev.sender_id].data.role_name
        print(user_dict[ev.sender_id])
    # b.send_msg(ev, ev.location_id, 'text', "loading...")
    # msg = str(ev.sender_name) + '：' + message
    msg = message
    print('deal face')
    if ev.face:
        msg = msg + "(表情：" + ev.face + ")"

    role_name = role_dict[ev.sender_id]
    if role_name:
        if role_name == '自定义':
            role_info = user_dict[ev.sender_id].data.role_info
        else:
            role_info = role_list[role_name]
    else:
        role_dict[ev.sender_id] = default_role_name
        user_dict[ev.sender_id].data.role_name = default_role_name
        user_dict[ev.sender_id].save()
        role_info = role_list[default_role_name]
    l_chat = private_chat_dic[ev.sender_id]

    mes = [{"role": "system", "content": role_info}]
    idx = 0
    for m in l_chat:
        if idx % 2 == 0:
            mes.append({"role": "user", "content": m})
        else:
            mes.append({"role": "assistant", "content": m})
        idx = idx + 1
    mes.append({"role": "user", "content": msg})
    try:
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=mes)
        # completion = openai.ChatCompletion.create(model="gpt-4-0613", messages=mes)
        answer = completion.choices[0].message.content.strip()
        b.send_msg(ev, ev.location_id, 'text', answer)
        update_talk(msg)
        update_talk(answer)
        return True
    except Exception as e:
        print(e)
        print('except in feature normal_chat()')
        b.send_msg(ev, ev.location_id, 'text', error_answer[random.randint(0, len(error_answer))])


def change_role(b: bot, ev: event):
    if ev.message == '身份列表' or ev.message == '角色列表':
        if not (ev.sender_id in list(user_dict.keys())):
            user_dict[ev.sender_id] = user(ev.sender_id)
            role_dict[ev.sender_id] = user_dict[ev.sender_id].data.role_name
        b.send_msg(ev, ev.location_id, 'text',
                   '下面就是所有的身份啦(目前是' + role_dict[ev.sender_id] + '):' + (
                       str(list(role_list.keys()))).replace(
                       '\'', ''))
        return True
    pattern = re.compile('^丸子[ ,，]?变[为成]?一?[只个名]?(...?.?.?)$')  # 目前指支持两个字的角色，所以这样写
    roler = pattern.findall(ev.message)
    if not roler:
        return False
    if not power['角色扮演']:
        return True
    if roler[0] in list(role_list.keys()):
        if not (ev.sender_id in list(user_dict.keys())):
            user_dict[ev.sender_id] = user(ev.sender_id)
            role_dict[ev.sender_id] = user_dict[ev.sender_id].data.role_name
        role_dict[ev.sender_id] = roler[0]
        user_dict[ev.sender_id].data.role_name = roler[0]
        user_dict[ev.sender_id].save()
        b.send_msg(ev, ev.location_id, 'text', '啪，丸子摇身一变，role play变换成功，我现在成了' + roler[0])
    else:
        num = random.randint(0, 11)
        if num == 0:
            b.send_msg(ev, ev.location_id, 'text', '丸子暂时不能扮演{}昂！'.format(roler[0]))
        elif num == 1:
            b.send_msg(ev, ev.location_id, 'text', '丸子才不扮演这个身份！')
        elif num == 2:
            b.send_msg(ev, ev.location_id, 'text', '扮演你这个身份需要先v我50~')
        elif num == 3:
            b.send_msg(ev, ev.location_id, 'text', '钱没到位，不干！')
        elif num == 4:
            b.send_msg(ev, ev.location_id, 'text', '北京精神病院欢迎你，联系电话:010-69111206')
        elif num == 5:
            b.send_msg(ev, ev.location_id, 'text', '重庆火葬场电话:023-68609969')
        elif num == 6:
            b.send_msg(ev, ev.location_id, 'text', '丸子不想理你，并向你扔了一个生瓜蛋子。')
        elif num == 7:
            b.send_msg(ev, ev.location_id, 'text', '你这个角色需要练习两年半才行，我要打篮球没那么多空闲。')
        elif num == 8:
            b.send_msg(ev, ev.location_id, 'text', '鸡汤来咯，嘿嘿嘿嘿嘿嘿，喝啊，这人都到齐了还不喝啊。')
        elif num == 9:
            b.send_msg(ev, ev.location_id, 'text', '你这样喊干什么嘛，你的态度能不能好一点哦？你再说！')
        else:
            b.send_msg(ev, ev.location_id, 'text', '变态！杂鱼！')
    return True


iden = {"MEMBER": "成员", "OWNER": "群主大大", "ADMINISTRATOR": "管理大人"}
power = {"菜单": True, "聊天": True, '发图': True, '防撤回': False, '象棋': True,
         '角色扮演': True}
pow_ex = {'pass': "功能已修改", 'No_ch': "功能不变", 'No_fun': "无此功能", 'No_per': "无此权限"}


def system_command(b: bot, ev: event):
    is_command = True
    if menu(b, ev):
        return is_command
    # "修改权限"
    # pattern = re.compile('^lambda ?: ?(.*) ?: ?(.*)$')  # 正则表达式
    pattern = re.compile("^(.*)-[>＞](.*)$")  # 正则表达式

    items = re.findall(pattern, ev.message)
    if items:
        command1 = items[0][0]
        command2 = items[0][1]
        if command1 in power.keys():
            if ev.sender_id == 2655602003:
                if command2 == "开":
                    if power[command1]:
                        b.send_msg(ev, ev.location_id, 'text', pow_ex["No_ch"])
                    else:
                        power[command1] = True
                        b.send_msg(ev, ev.location_id, 'text', pow_ex["pass"])
                elif items[1] == "关":
                    if power[command1]:
                        power[command1] = False
                        b.send_msg(ev, ev.location_id, 'text', pow_ex["pass"])
                    else:
                        b.send_msg(ev, ev.location_id, 'text', pow_ex["No_ch"])
                else:
                    b.send_msg(ev=ev, id=ev.location_id, ty='text', message="语句2段参数错误")
        else:
            if command1 == '身份':
                if len(command2) < 798:
                    if not (ev.sender_id in list(user_dict.keys())):
                        user_dict[ev.sender_id] = user(ev.sender_id)
                        role_dict[ev.sender_id] = user_dict[ev.sender_id].data.role_name
                    role_dict[ev.sender_id] = '自定义'
                    user_dict[ev.sender_id].data.role_name = '自定义'
                    user_dict[ev.sender_id].data.role_info = command2
                    user_dict[ev.sender_id].save()
                    b.send_msg(ev, ev.location_id, 'text', "自定义身份成功")
                else:
                    b.send_msg(ev, ev.location_id, 'text', "身份描述太长了")
        return True
    elif ev.message == "丸子":
        if ev.sender_id == 2655602003:
            b.send_msg(ev, ev.location_id, 'text', "%s 我在，你的丸子又回来了，再也不离开了！" % "作者")
        else:
            if ev.where == 'group':
                name = '成员'
                if ev.location_id == 780594692:
                    name = 'dalao'
                b.send_msg(ev, ev.location_id, 'text',
                           '{} {} 我在。以后也在~'.format(name, ev.sender_name))
            else:
                b.send_msg(ev, ev.location_id, 'text', "我在")
        return True
    elif ev.message == "退出丸子":
        if ev.sender_id == 2655602003:
            b.send_msg(ev, ev.location_id, 'text', "记得启动我，在你想我的时候")
            sys.exit(0)
        else:
            b.send_msg(ev, ev.location_id, 'text', "为什么要退出，哼，不退")
    elif ev.message == "清空记忆":
        if ev.where == 'group':
            # group_chat_dic[ev.location_id] = []
            private_chat_dic[ev.sender_id] = []
        else:
            private_chat_dic[ev.sender_id] = []
        b.send_msg(ev, ev.location_id, 'text', "记忆已清空")
    elif ev.message == 'r18 开':
        if ev.sender_id == 2655602003:
            open_r18[ev.sender_id] = True
            b.send_msg(ev, ev.location_id, message='修改成功')
    elif ev.message == 'r18 关':
        if ev.sender_id == 2655602003:
            open_r18[ev.sender_id] = False
            b.send_msg(ev, ev.location_id, message='修改成功')
    elif ev.message[:3] == '丸子拉黑':
        b.send_msg(ev, ev.location_id, message='修改成功')
    else:
        is_command = False
    return is_command


meng = os.listdir(basePath + r'\meng')
se = os.listdir(basePath + r'\se')
genshin_role = os.listdir(basePath + r'\genshin')
open_r18 = defaultdict(bool)
pictures_n = defaultdict(list)
for i in genshin_role:
    imgs = basePath + '\\genshin\\' + i + '\\n'
    pictures_n[i] = os.listdir(imgs)
pictures_h = defaultdict(list)
for i in genshin_role:
    imgs = basePath + '\\genshin\\' + i + '\\h'
    pictures_h[i] = os.listdir(imgs)


def send_local_image(b: bot, ev: event) -> bool:
    if not power['发图']:
        return False
    pat = re.compile(
        '^丸子来一?张(.+)图$'
    )  # 正则表达式
    it = re.findall(pat, ev.message)
    if it:
        character = it[0]
    else:
        return False
    if ev.where == 'group' and ev.location_id == 780594692:
        b.send_msg(ev, ev.location_id, 'text', '不可以滴哦~')
    elif character == '萌' or character == '萝莉':
        num = random.randint(0, len(meng))
        url = "file:///" + os.path.join(basePath + r'\meng', meng[num])
        b.send_msg(ev, ev.location_id, 'image', message='', url=url)
    elif character == '涩' or character == '色' or character == '泳装':
        num = random.randint(0, len(se))
        url = "file:///" + os.path.join(basePath + r'\se', se[num])
        b.send_msg(ev, ev.location_id, 'image', message='', url=url)
    elif character == '原神':
        num = random.randint(0, len(genshin_role))
        role_name = genshin_role[num]
        if open_r18[ev.location_id]:
            role_list = pictures_h[role_name]
            pic_name = role_list[random.randint(0, len(role_list))]
            pic = basePath + '\\genshin\\' + role_name + '\\h\\' + pic_name
        else:
            role_list = pictures_n[role_name]
            pic_name = role_list[random.randint(0, len(role_list))]
            pic = basePath + '\\genshin\\' + role_name + '\\n\\' + pic_name
        url = "file:///" + pic
        b.send_msg(ev, ev.location_id, 'image', message='', url=url)
    elif character in genshin_role:
        if open_r18[ev.location_id]:
            role_list = pictures_h[character]
            pic_name = role_list[random.randint(0, len(role_list))]
            pic = basePath + '\\genshin\\' + character + '\\h\\' + pic_name
        else:
            role_list = pictures_n[character]
            pic_name = role_list[random.randint(0, len(role_list))]
            pic = basePath + '\\genshin\\' + character + '\\n\\' + pic_name
        url = "file:///" + pic
        b.send_msg(ev, ev.location_id, 'image', message='', url=url)
    else:
        b.send_msg(ev, ev.location_id, 'text', '暂时没有' + character + '图哦~')
    return True


# 每天发诗歌的群
poet_group = {780594692, 584267180, 334829507}


def send_poetry(b: bot):
    try:
        token = get_token()
        message = generate_recom(get_poetry(token))
        print(message)
        for group_id in poet_group:
            b.send_poetry(group_id, message + "\n\n发送菜单即可查看现有功能喵~")
            time.sleep(2)
    except:
        print('error节点293 at feature')


def menu(b: bot, e: event):
    if e.message == '菜单' or e.message == 'help' or e.message == '帮助':
        b.send_msg(e, e.location_id, 'text', '喵~目前有的功能如下:\n1.ChatGPT:丸子...\n2.发图:丸子来一张..图\n3.阿巴:阿/啊\n4.防撤\
回:目前状态({})\n5.中国象棋\n6.角色扮演(可自定义身份):丸子变猫娘/姐姐/哥哥...发送“身份列表”即可查看所有可选身份\n使用 身份->描述 即可自定义身份，\
例：身份->请记住以下内容：哎哟你干嘛是\'阿坤\'的口头禅，....，请你扮演阿坤这个人'.format(
            '开' if power['防撤回'] else '关'))
        return True
    else:
        return False


def void_recall(b: bot, ev: event, data):
    if not power['防撤回']:
        return False
    data = data['data']
    temp = event(data)
    if temp.where != 'group':
        return False
    else:
        print(temp)
        try:
            if temp.message:
                if temp.image:
                    print(1)
                    msg = '成员 {} 撤回了一条消息，该消息是:\n'.format(ev.sender_name)
                    b.send_group_m_i_m(ev.location_id, temp.image, msg, ev.message)
                else:
                    print(2)
                    msg = '成员 {} 撤回了一条消息，该消息是:\n{}'.format(ev.sender_name, ev.message)
                    b.send_msg(ev, ev.location_id, 'text', msg)
            else:
                if temp.image:
                    print(3)
                    msg = '成员 {} 撤回了一张图片，该图片是:\n'.format(ev.sender_name)
                    b.send_group_m_i_m(ev.location_id, url=ev.image, message1=msg, message2='')
            return True
        except:
            print('void recall failed . see feature function void_recall')


# 中国象棋
# 为每一个群创建一个象棋控制器对象
chess_dic = defaultdict(dict)
# 外援的人的qq,昵称
helper1 = [0]
helper2 = [0]


#

def chinese_chess(b: bot, ev: event) -> bool:
    if not power['象棋']:
        return False
    location = ev.location_id
    sender = ev.sender_id
    msg = ev.message

    def get_control():
        if location not in list(chess_dic.keys()):
            contro = GameControl(location)
            chess_dic[location] = {'control': contro, 'player1': [], 'player2': []}
        else:
            contro: GameControl = chess_dic[location]['control']
        return contro

    def game_over(contro: GameControl):
        contro.status = 'not_begin'
        chess_dic[location]['player1'].clear()
        chess_dic[location]['player2'].clear()

    if ev.message == '中国象棋' or ev.message == '象棋':
        control = get_control()
        status = control.status
        if status == 'not_begin':
            control.status = 'pre'
            b.send_msg(ev, location, 'text', '棋局初始化成功，发送\'加入棋局\'加入游戏,使用标准棋谱命令行棋\n\n·其他命令\
有：认输，悔棋，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：棋手请求外援，被艾特的人发送\'同意\'即可完成交接')
        elif status == 'pre':
            p1 = chess_dic[location]['player1']
            if p1:
                b.send_msg(ev, location, 'text',
                           '棋手 {}({}方)正在等待对手，发送\'加入棋局\'加入游戏'.format(p1[2], p1[1]))
            else:
                b.send_msg(ev, location, 'text', '棋局已经初始化，发送\'加入棋局\'加入游戏,使用标准棋谱命令行棋\n\n·其他命令\
有：认输，悔棋，掀棋盘(不建议)\n\n·命令\'请求接手@somebody\'：棋手请求外援，被艾特的人发送\'同意\'即可完成交接')
        elif status == 'has_began':
            b.send_msg(ev, location, 'text', '棋局已经开始，快来观战吧\n红方:{}\n黑方:{}'.format(
                chess_dic[location]['player1'][2], chess_dic[location]['player2'][2]
            ))
        return True

    elif ev.message == '加入棋局' or ev.message == '加入':
        control = get_control()
        status = control.status
        if status == 'has_began':
            b.send_msg(ev, location, 'text', '棋局已经开始，快来观战吧\n红方:{}\n黑方:{}'.format(
                chess_dic[location]['player1'][2], chess_dic[location]['player2'][2]
            ))
            return True
        elif status == 'not_begin':
            b.send_msg(ev, location, 'text', '棋局还没有初始化，发送\'中国象棋\'初始化')
            return True
        if not chess_dic[location]['player1']:
            # 在列表中，第一个元素为id,第二个元素为team,第三个元素为昵称
            team = Team.Red if random.randint(0, 2) == 1 else Team.Black
            play1: list = chess_dic[location]['player1']
            play1.append(sender)
            play1.append(team)
            play1.append(ev.sender_name)
            b.send_msg(ev, location, 'text', '{} 加入成功，你执{}'.format(ev.sender_name, team))
        elif not chess_dic[location]['player2']:
            p1 = chess_dic[location]['player1']
            if sender == p1[0]:
                b.send_msg(ev, location, 'text', '你已经加入了棋局，耐心等待对手吧~')
                return True
            if p1[1] == Team.Red:
                team = Team.Black
            else:
                team = Team.Red
            play2: list = chess_dic[location]['player2']
            play2.append(sender)
            play2.append(team)
            play2.append(ev.sender_name)
            b.send_msg(ev, location, 'text', '{} 加入成功，你执{}'.format(ev.sender_name, team))

            control.init_map()
            p = control.paint_map()
            url = "file:///" + os.path.join(p)
            time.sleep(0.5)
            b.send_msg(ev, location, 'image', message='', url=url)
            os.remove(p)
        return True
    elif msg == '退出棋局' or msg == '掀棋盘':
        control = get_control()
        if control.status != 'has_began':
            return True
        if sender == chess_dic[location]['player1'][0] or \
                sender == chess_dic[location]['player2'][0] or sender == 2655602003:
            if control.status == 'not_begin':
                return True
            game_over(control)
            b.send_msg(ev, location, 'text', '退出成功，欢迎下次玩喵~')
        return True
    elif msg == '认输' or msg == '投降':
        control = get_control()
        if control.status != 'has_began':
            return True
        if sender != chess_dic[location]['player1'][0] and sender != chess_dic[location]['player2'][0]:
            return True
        player1 = chess_dic[location]['player1']
        player2 = chess_dic[location]['player2']
        if sender == player1[0]:
            win = player2[2]
            lose = player1[2]
            lose_team = player1[1]
        else:
            win = player1[2]
            lose = player2[2]
            lose_team = player2[1]
        b.send_msg(ev, location, 'text',
                   '{}方({})认输，恭喜 {} 获得胜利！\n对局回合数：{}'.format(lose_team, lose, win, control.round_count))
        control.status = 'not_begin'
        game_over(control)
        return True
    elif len(ev.message) == 4 and ev.message[2] in ['进', '退', '平']:
        control = get_control()
        if control.status != 'has_began':
            return True

        def to_mov():
            try:
                control.move_chess(ev.message)
                img = control.paint_map()
                url_ = "file:///" + os.path.join(img)
                b.send_msg(ev, location, 'image', message='', url=url_)
                os.remove(img)
                over = control.game_over
                if over:
                    time.sleep(0.5)
                    p1 = chess_dic[location]['player1']
                    p2 = chess_dic[location]['player2']
                    if over == p1[1]:
                        winner = p1[2]
                        loser = p2[2]
                    else:
                        winner = p2[2]
                        loser = p1[2]
                    b.send_msg(ev, location, 'text',
                               '经过{}个回合，恭喜{}战胜了{}！'.format(control.round_count, winner, loser))
                    game_over(control)
            except Exception as e:
                print('节点259 in feature')
                print(e)
                if isinstance(e, ChessExcept):
                    b.send_msg(ev, location, 'text', str(e))

        if sender == chess_dic[location]['player1'][0] and chess_dic[location]['player1'][1] == control.turn:
            to_mov()
        elif sender == chess_dic[location]['player2'][0] and chess_dic[location]['player2'][1] == control.turn:
            to_mov()
        return True
    elif msg == '悔棋':
        control = get_control()
        if control.status != 'has_began':
            return True
        if sender == chess_dic[location]['player1'][0]:
            team = chess_dic[location]['player1'][1]
        elif sender == chess_dic[location]['player2'][0]:
            team = chess_dic[location]['player2'][1]
        else:
            return True
        if team == control.turn:
            b.send_msg(ev, location, 'text', '你还没走棋，无法悔棋')
            return True
        try:
            control.back_to_last_step()
            img_path = control.paint_map()
            url = "file:///" + os.path.join(img_path)
            b.send_msg(ev, location, 'image', message='', url=url)
            os.remove(img_path)
        except Exception as e:
            if isinstance(e, ChessExcept):
                b.send_msg(ev, location, 'text', str(e))
    elif msg == '请求接手':
        control = get_control()
        if control.status != 'has_began':
            return True
        if not ev.at:
            return True
        if sender == chess_dic[location]['player1'][0]:
            if ev.at == chess_dic[location]['player2'][0]:
                b.send_msg(ev, location, 'text', '脑子有问题？')
                return True
            helper1[0] = ev.at
            player1 = chess_dic[location]['player1']
            b.send_msg(ev, location, 'text', '{}方（{}）棋力不敌对面，请求外援'.format(player1[1], player1[2]))
        elif sender == chess_dic[location]['player2'][0]:
            if ev.at == chess_dic[location]['player1'][0]:
                b.send_msg(ev, location, 'text', '脑子有问题？')
                return True
            helper2[0] = ev.at
            player2 = chess_dic[location]['player2']
            b.send_msg(ev, location, 'text', '{}方（{}）棋力不敌对面，请求外援'.format(player2[1], player2[2]))
        return True
    elif msg == '同意':
        control = get_control()
        if control.status != 'has_began':
            return True
        if sender == helper1[0]:
            chess_dic[location]['player1'][0] = helper1[0]
            chess_dic[location]['player1'][2] = ev.sender_name
            helper1[0] = 0
            b.send_msg(ev, ev.location_id, 'text', '接手成功，你执' + chess_dic[location]['player1'][1])
        elif sender == helper2[0]:
            chess_dic[location]['player2'][0] = helper2[0]
            chess_dic[location]['player2'][2] = ev.sender_name
            helper2[0] = 0
            b.send_msg(ev, ev.location_id, 'text', '接手成功，你执' + chess_dic[location]['player2'][1])
        return True
    return False
