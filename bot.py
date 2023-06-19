import re
import http.client
import json
import sys

import threading
import random
import time

from event import event
import feature as f
# 写爬虫
import requests
import base64
import asyncio
import schedule

__version__ = 4.1

# 4.0添加聊天功能，取消语言学习模块，数据库不用postgresql了，改用es
# 图片传输只能png的，jpg只能手机端能看到

# 使用代理，openai需要用到代理
import os

os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7078'
os.environ["HTTPS_PROXY"] = 'http://127.0.0.1:7078'

dic_group = {}  # 到时候再考虑用这个来做什么吧
dic_private = {}
dic_m = {}

# 4 丸子来一张 5 丸子\n6 丸子 查询作者 千式部\n7 丸子 ID 8396713 10\n8 丸子 ID 8396713 all\n9 丸子 删除 千式部.zip\n10 丸子 tag 水着 热度排 前3张
# 庙檐开发，目前功能贫瘠，只有学习语言功能，第一次输入如‘字段1 & 字段2’的文字，丸子会响应并学会字段1;2.输入:十连;3.输入抽up

all_pic_d = {}

allow_id = {2655602003}  # primary使用


# lock=threading.Lock()#来个线程锁
# lock_chat=threading.Lock()#再来个线程锁
# AInum=1#临界区资源

# line=[]任务线，完全没写


# 丸子聊天说明：“丸子”后面跟参数。完整输出会把问题以及得分打印出来


class bot():
    def __init__(self, address, port=5700, authKey="INITKEY61xgs0xw"):
        self.conn = http.client.HTTPConnection(address, port)
        self.authKey = authKey
        self.sessionKey = self.bind()

    def bind(self):
        auth = json.dumps({"verifyKey": self.authKey})
        # print(str)
        # headers = {}
        conn = self.conn
        conn.request('POST', '/verify', auth)
        response = conn.getresponse()
        # print(response.status, response.reason)
        session = response.read().decode('utf-8')
        print(session)
        sessionKey = json.loads(session)['session']
        bind = json.dumps({"sessionKey": sessionKey, "qq": 1969712698})
        conn.request('POST', '/bind', bind)
        response = conn.getresponse()
        # print(response.status, response.reason)
        data = response.read().decode('utf-8')
        print(data)
        return sessionKey

    def send_msg(self, ev: event, id=0, ty='text', message='', url=''):
        conn = self.conn

        def send_text(_id, text):
            # print('节点106')
            sessionKey = self.sessionKey
            js = json_deal.build_text_json(sessionKey, _id, text)
            # print(js)
            if ev.type == 'primary':
                print('send primary msg')
                conn.request('POST', '/sendFriendMessage', js)
            else:
                print('send group msg')
                conn.request('POST', '/sendGroupMessage', js)

            response = conn.getresponse()
            data = response.read().decode('utf-8')
            print('成功发送data节点119', data)

        def send_image(_id, url, message):
            sessionKey = self.sessionKey
            js = json_deal.build_image_json(sessionKey, _id, url, message)
            if ev.type == 'primary':
                conn.request('POST', '/sendFriendMessage', js)
            else:
                conn.request('POST', '/sendGroupMessage', js)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            print(data)

        if ty == 'text':
            send_text(id, message)
        elif ty == 'image':
            send_image(id, url, message)

    def send_group_m_i_m(self, group_id, url, message1, message2):
        sessionKey = self.sessionKey
        messageChain = [
            json.loads(json_deal.build_dic_for_json(ty='text', text=message1)),
            json.loads(json_deal.build_dic_for_json(ty='image', url=url)),
            json.loads(json_deal.build_dic_for_json(ty='text', text=message2))
        ]
        js = json_deal.build_mix_json(sessionKey, group_id, messageChain=messageChain)
        self.conn.request('POST', '/sendGroupMessage', js)
        response = self.conn.getresponse()
        data = response.read().decode('utf-8')
        print(data)

    def send_poetry(self, group_id, poetry: str):
        sessionKey = self.sessionKey
        js = json_deal.build_text_json(sessionKey, group_id, poetry)
        self.conn.request('POST', '/sendGroupMessage', js)
        response = self.conn.getresponse()
        data = response.read().decode('utf-8')
        print(data)

    def get_msg_by_id(self, location_id, msg_id):
        print('节点154')
        requ = {}
        requ['sessionKey'] = self.sessionKey
        requ['messageId'] = msg_id
        requ['target'] = location_id
        js = json.dumps(requ)
        self.conn.request('GET', '/messageFromId?sessionKey={}&messageId={}&target={}'
                          .format(self.sessionKey, msg_id, location_id), js)
        print('节点162')
        response = self.conn.getresponse()
        data = response.read().decode('utf-8')
        data = json.loads(data)
        return data

    def deal_data(self, data):
        # 这里是处理消息的代码，解析消息并进行回复
        for i in data:
            try:
                ev = event(i)
                # 先判定是不是支持类型的事件
                if not ev.type:
                    continue
                print(ev.type, ' : ', end='')
                ev.message = str(ev.message).replace('\n', '')
                # 中国象棋
                if f.chinese_chess(self, ev):
                    continue
                # 撤回消息
                if i['type'] == 'GroupRecallEvent':
                    data = self.get_msg_by_id(ev.location_id, ev.msg_id)
                    f.void_recall(self, ev, data)
                    continue
                # 阿巴阿巴
                if len(ev.message) == 1:
                    if ev.message in ["啊", "阿"]:
                        self.send_msg(ev=ev, id=ev.location_id, message="巴~")
                    continue
                # 角色扮演
                if f.change_role(self, ev, ev.message):
                    continue
                # 系统命令
                if f.system_command(self, ev):
                    continue
                # print('\n标记1\n')
                if ev.type == 'primary':
                    print(ev.location_id, '->', ev.message)
                    if '来' in ev.message and '张' in ev.message:
                        pat = re.compile(
                            '^.*(来一?张.+)$'
                        )  # 正则表达式
                        it = re.findall(pat, ev.message)
                        if it:
                            f.send_local_image(self, ev, it[0])
                            continue
                    else:
                        f.normal_chat(self, ev, ev.message)
                elif ev.type == 'group':
                    print(ev.location_id, '->', ev.message)
                    pattern = re.compile(
                        '^丸子[ ,，]?(.+)'
                    )  # 正则表达式
                    items = re.findall(pattern, ev.message)
                    if not items:
                        continue
                    item = items[0]
                    # 发图
                    if f.send_local_image(self, ev, item):
                        continue
                    print('节点198')
                    f.normal_chat(self, ev, item)
            except Exception as e:
                print('except节点202')
                print(e)

    def call_help(self, ev: event):
        self.send_msg(ev, ev.location_id, 'text', dic_m["菜单"])

    async def fetch_message(self):
        conn = self.conn
        sessionKey = self.sessionKey
        while True:
            try:
                conn.request('GET', '/fetchLatestMessage?sessionKey=' + sessionKey + '&count=10')
                response = conn.getresponse()
                data = response.read().decode('utf-8')
                j = json.loads(data)
                data = j["data"]
                if data:
                    threading.Thread(target=self.deal_data, args=(data,)).start()  # 多线程启动
            except Exception as e:
                print('except210')
                print(e)
            await asyncio.sleep(1)

    async def run(self):
        schedule.every().day.at('21:00').do(f.send_poetry, self)
        schedule.every().day.at('09:00').do(f.send_poetry, self)  # 设计任务日程表

        async def check_schedule():
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)  # 每分钟检查是否满足条件

        tasks = [asyncio.create_task(self.fetch_message()), asyncio.create_task(check_schedule())]
        # 在这里运行协程
        await asyncio.gather(*tasks)


class json_deal():
    def build_dic_for_json(ty='text', text='', url=''):
        out = {}
        if ty == 'text':
            out["type"] = "Plain"
            out["text"] = text
        elif ty == 'image':
            out["type"] = "Image"
            out["url"] = url
        js = json.dumps(out)
        return js

    def build_text_json(sessionKey, target, message=''):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": [json.loads(json_deal.build_dic_for_json(ty='text', text=message))]
        }
        js = json.dumps(dic)
        return js

    def build_image_json(sessionKey, target, url='', message=''):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": [
                json.loads(json_deal.build_dic_for_json(ty='image', url=url)),
                json.loads(json_deal.build_dic_for_json(ty='text', text=message))
            ]
        }
        js = json.dumps(dic)
        return js

    def build_mix_json(sessionKey, target, messageChain=[]):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": messageChain
        }
        js = json.dumps(dic)
        return js


if __name__ == '__main__':
    print('begin')
    b = bot("127.0.0.1", 5700)
    r = asyncio.run(b.run())
    sys.exit(r)
