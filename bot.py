import re
import http.client
import json
import sys
import threading
from event import event
import feature as f
import asyncio
import schedule
import os

# 使用代理，openai需要用到代理
os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7078'
os.environ["HTTPS_PROXY"] = 'http://127.0.0.1:7078'


# 庙檐开发，樱桃大丸子修改，目前功能有ChatGPT,防撤回，发本地图，中国象棋，角色扮演

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

    #  防撤回功能需要
    def get_msg_by_id(self, location_id, msg_id):
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
                if f.change_role(self, ev):
                    continue
                # 系统命令
                if f.system_command(self, ev):
                    continue
                # -----以上功能不需要分群聊还是私聊，接下来的功能需要分群聊还是私聊----
                if ev.type == 'primary':
                    print(ev.location_id, '->', ev.message)
                    if '来' in ev.message and '张' in ev.message:
                        pat = re.compile(
                            '^.*(来一?张.+)$'
                        )
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
                    # 最后交给gpt
                    f.normal_chat(self, ev, item)
            except Exception as e:
                print('except节点202')
                print(e)

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
