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


def my_poet() -> str:
    content = "今日的推荐诗词是"
    title = ''
    count = 0
    with open("poetry.txt", "r") as file:
        for line in file:
            count += 1
            if count == 1:
                title = line.replace('\n','')
            elif count == 2:
                content += line.replace('\n','') + '的' + title + '：\n'
            elif line[0:3] == 'end':
                break
            else:
                content += line
    return content

if __name__ == '__main__':
    print(generate_recom(my_poet()))
