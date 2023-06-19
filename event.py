class Sort:
    Text = '文'
    Picture = '图'
    T_P = '文图'
    P_T = '图文'
    T_P_T = '文图文'


class event:
    def __init__(self, i):
        self.message = None
        self.image = None
        self.at = None
        self.permission = None
        self.memberName = None
        self.sender_id = None
        self.location_id = None
        self.type = None
        self.msg_id = None
        t = i['type']
        if t == 'GroupRecallEvent':
            self.recall(i)
        elif t == 'FriendMessage' or t == 'TempMessage' or t == 'StrangerMessage' or t == 'GroupMessage':
            self.chat_event(i)
        else:
            self.other()

    def chat_event(self, i):
        self.msg_id = i['messageChain'][0]['id']
        self.at = False
        if i['type'] == 'FriendMessage' or i['type'] == 'TempMessage' or i['type'] == 'StrangerMessage':
            self.type = 'primary'
            self.location_id = i['sender']['id']
            self.sender_id = self.location_id
            self.memberName = i['sender']['remark']
            if not self.memberName:
                self.memberName = i['sender']['nickname']
        elif i['type'] == 'GroupMessage':
            self.type = 'group'
            self.location_id = i['sender']['group']['id']
            self.sender_id = i['sender']['id']
            # MemberMuteEvent不处理
            self.memberName = i['sender']['memberName']
        if self.sender_id == 2655602003:
            self.permission = "OWNER"
        else:
            self.permission = 'MEMBER'
        message_type = i['messageChain'][1]['type']  # 这里要改，不能只处理第一条，但可以只处理前两条
        # if(self.message_type=='Face'):
        #     self.message=i['messageChain'][1]['faceId']
        if message_type == 'Plain':
            self.message = i['messageChain'][1]['text']
        elif message_type == 'At' and int(i['messageChain'][1]['target']) == 1969712698:
            self.at = True
            self.message = i['messageChain'][2]['text']  # at符号再往后面跟一个
        if len(i['messageChain']) == 3:
            message_type = i['messageChain'][2]['type']
            if message_type == 'Image':
                self.image = i['messageChain'][2]['url']

    def recall(self, i):
        self.msg_id = i['messageId']
        self.at = False
        self.location_id = i['group']['id']
        self.type = 'group'
        self.sender_id = i['authorId']
        self.memberName = i['operator']['memberName']
        if self.sender_id == 2655602003:
            self.permission = "OWNER"
        else:
            self.permission = i['operator']['permission']
        self.image = ''

        self.message = ''

    def other(self):
        self.type = ''
