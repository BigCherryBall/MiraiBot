import requests
import datetime


token_value = 'B1l2QfCZWRLPulrnMpuXuIKArnXuMMuo'

def get_poetry():
    poetry_url = "https://v2.jinrishici.com/sentence"
    headers = {
        "X-User-Token": token_value
    }
    response = requests.get(poetry_url, headers=headers)
    if response.status_code != 200:
        return ""
    poetry_dict = response.json()
    # print(poetry_dict)
    poetry_content_list = poetry_dict["data"]["origin"]["content"]
    poetry_content = "\n".join(poetry_content_list)

    # 整理诗词格式
    poetry_dynasty = poetry_dict["data"]["origin"]["dynasty"]
    poetry_author = poetry_dict["data"]["origin"]["author"]
    poetry_title = poetry_dict["data"]['origin']['title']
    # poetry_recommendation = f"今日推荐诗词：\n{poetry_content}\n—— {poetry_dynasty} {poetry_author}\n"

    poetry_recommendation = f"今日的推荐诗词是{poetry_dynasty}诗人{poetry_author}的《{poetry_title}》：\n"
    poetry_recommendation += f"{poetry_content}"
    return poetry_recommendation


def generate_recom(poetry_recommendation):
    now = datetime.datetime.now()
    weekday = now.weekday()
    hour = now.hour
    is_weekend = (weekday == 5) or (weekday == 6)  # 判断是否为周末
    greetings = ""
    if is_weekend:  # 周末问候语
        greetings = "周末愉快！"
    else:  # 工作日问候语
        if hour < 12:
            greetings = "早上好！"
        else:
            greetings = "晚上好！"

    # 拼接问候语和推荐诗句
    weekday_dict = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    weekday_str = weekday_dict[weekday]
    message = f"{greetings}今天是{weekday_str}，{poetry_recommendation}"
    return message


class poetry:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.content = ''
    
    def __str__(self) -> str:
        return self.title + '\n' + self.author + '\n' + self.content
    
    def get_my_poetry(self):
        return "今日的推荐诗词是" + self.author + '的' + self.title + '：' + self.content

poetry_list: list[poetry] = []
current_poetry: poetry = None
count = 0
begin = False

with open("poetry.txt", "r") as file:
    for line in file:
        if line == '#begin\n':
            current_poetry = poetry()
            begin = True
            count = 1
            poetry_list.append(current_poetry)
        elif begin and count == 1:
            current_poetry.title = line.replace('\n','')
            count = 2
        elif begin and count == 2:
            current_poetry.author = line.replace('\n','')
            count = 0
        elif line == '#end' or line == '#end\n':
            begin = False
            current_poetry = None
        elif begin:
            current_poetry.content += line
        else:
            continue
    
for i in poetry_list:
    print(i)
    print('--------------------------------------')

idx = 0
def get_poetry() -> str:
    return generate_recom(poetry_list[idx % len(poetry_list)].get_my_poetry())




if __name__ == '__main__':
    print('over')
