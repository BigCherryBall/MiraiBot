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
    poety = '今日的推荐诗词是现代诗人罗伯特·弗罗斯特的《未选择的路》:\n\n\
黄色的树林里分出两条路，\n可惜我不能同时去涉足，\n我在那路口久久伫立，\n我向着一条路极目望去，\n直到它消失在丛林深处。\n\
但我却选了另外一条路，\n它荒草萋萋，十分幽寂，\n显得更诱人、更美丽；\n虽然在这两条小路上，\n都很少留下旅人的足迹；\n\
虽然那天清晨落叶满地，\n两条路都未经脚印污染。\n呵，留下一条路等改日再见！\n但我知道路径延绵无尽头，\n恐怕我难以再回返。\n\
也许多少年后在某个地方，\n我将轻声叹息把往事回顾：\n一片树林里分出两条路，\n而我选了人迹更少的一条，\n从此决定了我一生的道路。'
    return generate_recom(poety)

if __name__ == '__main__':
    
    r = requests.get('https://v2.jinrishici.com/info')
    if r.status_code == 200:
        print(r.json())
