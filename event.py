class Type:
    normal = 'normal'
    recall = 'recall'
    leave = 'leave'
    join = 'join'


class event:
    def __init__(self, i):
        self.message = ''
        self.image = None
        self.at = 0
        self.face = None
        self.permission = None
        self.sender_name = None
        self.sender_id = None
        self.location_id = None
        self.where = None
        self.type = None
        self.msg_id = None
        t = i['type']
        if t == 'GroupRecallEvent':
            self.recall(i)
        elif t == 'FriendMessage' or t == 'TempMessage' or t == 'StrangerMessage' or t == 'GroupMessage':
            self.chat_event(i)
        elif t == 'MemberLeaveEventQuit' or t == 'MemberLeaveEventKick':
            self.leave_group(i)
        elif t == 'MemberJoinEvent':
            self.join_group(i)
        else:
            self.other()

    def chat_event(self, i):  # 只处理文字消息
        if len(i['messageChain']) > 4:
            self.other()
            return
        self.msg_id = i['messageChain'][0]['id']
        self.type = Type.normal
        if i['type'] == 'GroupMessage':
            self.where = 'group'
            self.location_id = i['sender']['group']['id']
            self.sender_id = i['sender']['id']
            self.sender_name = i['sender']['memberName']
            self.permission = i['sender']['permission']
        else:
            self.where = 'primary'
            self.location_id = i['sender']['id']
            self.sender_id = self.location_id
            self.sender_name = i['sender']['remark']
            if not self.sender_name:
                self.sender_name = i['sender']['nickname']
        if self.sender_id == 2655602003:
            self.permission = "OWNER"

        messageChain = i['messageChain']
        for msg in messageChain:
            message_type = msg['type']
            if message_type == 'Plain':
                text = msg['text']
                if text == ' ':
                    continue
                elif text[0] == ' ':
                    text = text[1:]
                self.message += text
            elif message_type == 'Image':
                self.image = msg['url']  # 图片就暂时这样了
            elif message_type == 'At':
                self.at = msg['target']
            elif message_type == 'Face':
                self.face = msg['name']

    def recall(self, i):
        self.msg_id = i['messageId']
        self.location_id = i['group']['id']
        self.where = 'group'
        self.type = Type.recall
        self.sender_id = i['authorId']
        self.sender_name = i['operator']['memberName']
        if self.sender_id == 2655602003:
            self.permission = "OWNER"
        else:
            self.permission = i['operator']['permission']

    def leave_group(self, i):
        self.type = Type.leave
        self.location_id = i['member']['group']['id']
        self.sender_id = i['member']['id']
        self.sender_name = i['member']['memberName']
        self.where = 'group'
    
    def join_group(self, i):
        self.where = 'group'
        self.type = Type.join
        self.sender_id = i['member']['id']
        self.sender_name = i['member']['memberName']
        self.location_id = i['member']['group']['id']

    def other(self):
        pass
