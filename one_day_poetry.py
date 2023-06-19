import requests
import datetime


def get_token():
    token_url = "https://v2.jinrishici.com/token"
    req = requests.get(token_url)
    response_dict = req.json()
    return response_dict['data']


def get_poetry(token_value):
    poetry_url = "https://v2.jinrishici.com/sentence"
    headers = {
        "X-User-Token": token_value
    }
    response = requests.get(poetry_url, headers=headers)
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


if __name__ == '__main__':
    token_value = get_token()
    print(generate_recom(get_poetry(token_value)))
