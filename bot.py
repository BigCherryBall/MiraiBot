from http.client import HTTPConnection, HTTPResponse
import json
import sys
import threading
from event import event, Type
import feature as f
import asyncio
import schedule
from tool import config


class bot:
    def __init__(self, address, port=config['http_port'], authKey = "BigCherryBall"):
        self.author = config['author_qq']
        self.bot_qq = config['bot_qq']
        self.conn = HTTPConnection(address, port)
        self.authKey = authKey
        self.sessionKey = self.bind()
        self.lock = threading.Lock()

    def bind(self):
        auth = json.dumps({"verifyKey": self.authKey})
        conn = self.conn
        conn.request('POST', '/verify', auth)
        response = conn.getresponse()
        session = response.read().decode('utf-8')
        print(session)
        sessionKey = json.loads(session)['session']
        bind = json.dumps({"sessionKey": sessionKey, "qq": self.bot_qq})
        conn.request('POST', '/bind', bind)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(data)
        return sessionKey
    
    def __conn_mirai__(self, method: str, url: str, js: str = None) -> HTTPResponse:
        self.lock.acquire()
        response = None
        try:
            self.conn.request(method, url, js)
            response = self.conn.getresponse()
        finally:
            self.lock.release()
            return response

    def send_text(self, ev: event, text):
        sessionKey = self.sessionKey
        js = json_deal.build_text_json(sessionKey, ev.location_id, text)
        if ev.where == 'group':
            response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        else:
            response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def send_image(self, ev: event, url):
        sessionKey = self.sessionKey
        js = json_deal.build_image_json(sessionKey, ev.location_id, url)
        if ev.where == 'group':
            response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        else:
            response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def send_voice(self, ev: event, url):
        sessionKey = self.sessionKey
        js = json_deal.build_voice_json(sessionKey, ev.location_id, url)
        if ev.where == 'group':
            response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        else:
            response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def send_m_i_m_i(self, ev: event, m1='', u1='', m2='', u2=''):
        msg_chain = []
        if m1:
            msg_chain.append({"type": "Plain", "text": m1})
        if u1:
            msg_chain.append({"type": "Image", "url": u1})
        if m2:
            msg_chain.append({"type": "Plain", "text": m2})
        if u2:
            msg_chain.append({"type": "Image", "url": u2})
        js = json_deal.build_mix_json(self.sessionKey, ev.location_id, msg_chain)
        if ev.where == 'group':
            response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        else:
            response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def send_private_text(self, id, text):
        sessionKey = self.sessionKey
        js = json_deal.build_text_json(sessionKey, id, text)
        response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def send_group_text(self, group_id, text: str):
        sessionKey = self.sessionKey
        js = json_deal.build_text_json(sessionKey, group_id, text)
        response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        response.read()

    def send_custom_msg(self, ev: event, data: list):
        sessionKey = self.sessionKey
        js = json_deal.build_mix_json(sessionKey, ev.location_id, data)
        if ev.where == 'group':
            response = self.__conn_mirai__('POST', '/sendGroupMessage', js)
        else:
            response = self.__conn_mirai__('POST', '/sendFriendMessage', js)
        response.read()

    def get_msg_by_id(self, location_id, msg_id):
        response = self.__conn_mirai__('GET', '/messageFromId?sessionKey={}&messageId={}&target={}'.format(self.sessionKey, msg_id,
                                                                                              location_id))
        data = response.read().decode('utf-8')
        data = json.loads(data)
        return data

    def _step_deal_data(self, i):
        try:
            ev = event(i)
            if ev.where != 'group':
                return

            # 先判定是不是支持类型的事件
            if not ev.type:
                return
            # 撤回消息
            elif ev.type == Type.recall:
                if f.power['防撤回']:
                    data = self.get_msg_by_id(ev.location_id, ev.msg_id)
                    f.void_recall(self, ev, data)
                return
            # 调用功能列表
            for fun in f.function_list:
                if fun(self, ev):
                    return

        except Exception as e:
            print('[bot _step_deal_data] error:', e)

    def deal_data(self, data):
        if not f.power['总']:
            return
        # 这里是处理消息的代码，解析消息并进行回复
        for i in data:
            threading.Thread(target=self._step_deal_data, args=(i,)).start()

    async def fetch_message(self):
        sessionKey = self.sessionKey
        while True:
            try:
                response = self.__conn_mirai__('GET', '/fetchLatestMessage?sessionKey=' + sessionKey + '&count=10')
                data = response.read().decode('utf-8')
                j = json.loads(data)
                data = j["data"]
                if data:
                    threading.Thread(target=self.deal_data, args=(data,)).start()  # 多线程启动
            except Exception as e:
                print('[feature fetch_message]error :' + str(e))
            await asyncio.sleep(1)

    async def run(self):
        schedule.every().day.at('21:00').do(f.send_poetry, self)
        schedule.every().day.at('08:00').do(f.send_poetry, self)  # 设计任务日程表
        schedule.every().day.at('20:20').do(f.remind_work_over, self)

        async def check_schedule():
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)  # 每分钟检查是否满足条件

        tasks = [asyncio.create_task(self.fetch_message()), asyncio.create_task(check_schedule())]
        # 在这里运行协程
        await asyncio.gather(*tasks)


class json_deal:
    @staticmethod
    def build_msg_dic(text):
        return {"type": "Plain", "text": text}

    @staticmethod
    def build_image_dic(url):
        return {"type": "Image", "url": url}

    @staticmethod
    def build_text_json(sessionKey, target, message):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": [{"type": "Plain", "text": message}]
        }
        js = json.dumps(dic)
        return js

    @staticmethod
    def build_image_json(sessionKey, target, url):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": [{"type": "Image", "url": url}]
        }
        js = json.dumps(dic)
        return js

    @staticmethod
    def build_voice_json(sessionKey, target, url):
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": [{"type": "Voice", "url": url}]
        }
        js = json.dumps(dic)
        return js

    @staticmethod
    def build_mix_json(sessionKey, target, messageChain=None):
        if messageChain is None:
            messageChain = []
        dic = {
            "sessionKey": sessionKey,
            "target": target,
            "messageChain": messageChain
        }
        js = json.dumps(dic)
        return js


if __name__ == '__main__':
    print('begin')
    b = bot("127.0.0.1")
    r = asyncio.run(b.run())
    sys.exit(r)
