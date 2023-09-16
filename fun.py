import requests
import re
from bot import bot
from event import event
from pathlib import *


genshin_charactor_list=['神里绫华','刻晴']
genshin_weapon_list=['若水']
img_root = Path(Path.cwd(),'image')

def getMessageFromWeb(url,data,recall=None):
    pass


# 全局变量区
url = 'https://api.caonm.net/api/ai/wx?key=sp4mVsMIBiBslhw56QfpHDXIkg'
url1='https://api.caonm.net/api/ai/gpt-4?key=0GVAs86wZ4KHQA5BOolBJhIzeY'

def chatGPT():
    data={"msg":"樱桃：请你在接下来的对话中扮演一个可爱的猫娘，叫丸子，我是你的主人樱桃\n丸子：樱桃主人，你好呀，我是丸子，喵~有什么需要我帮忙的吗？喵~\n樱桃:中午吃啥好呢？",}
    # 发送post请求
    response = requests.post(url, data=data)
    # 获取响应内容
    result = response.json()
    
    # 打印结果
    print(result) #输出 {'code': 200, 'data': {}}
    print(type(result))  #输出 <class 'dict'>
    #获取output
    print(result['data']['output']) 


def genshinCharactorMsg(b: bot, ev: event) -> bool:
    idx = 0
    char_url= 'https://api.caonm.net/api/ys/j?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    lens=len(genshin_charactor_list)
    if '神里'==ev.message or '绫华' == ev.message :
        msg = '神里绫华'

    else:
        msg = ev.message
    while idx < lens:
        if genshin_charactor_list[idx] == msg:
            break
        idx += 1
    if idx >= lens :
        return False
    filename=Path(img_root,"genshin/info/",msg+".jpg")
    # 这里写如果已经存在该图片的逻辑
    if filename.exists():
        b.send_image(ev,ev.location_id,"file:///"+filename)
        return True
    # 发送post请求
    response = requests.post(char_url, data={"msg":msg})
    
    if response.status_code == 200:
        with filename.open('wb') as file:
            file.write(response.content)
            b.send_image(ev,ev.location_id,"file:///"+filename)
    else:
        b.send_text(ev,ev.location_id,"角色不存在，获取图片失败")

    return True
    


def genshinCharactorImage(b: bot, ev: event) -> bool:
    idx = 0
    weapon_url= 'https://api.caonm.net/api/ys/w?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    lens=len(genshin_weapon_list)

    msg = ev.message
    while idx < lens:
        if genshin_weapon_list[idx] == msg:
            break
        idx += 1
    if idx >= lens :
        return False
    filename=Path(img_root,"genshin/weapon/",msg+".jpg")
    # 这里写如果已经存在该图片的逻辑
    if filename.exists():
        b.send_image(ev,ev.location_id,"file:///"+filename)
        return True
    # 发送post请求
    response = requests.post(weapon_url, data={"msg":msg})
    
    if response.status_code == 200:
        with filename.open('wb') as file:
            file.write(response.content)
            b.send_image(ev,ev.location_id,"file:///"+filename)
    else:
        b.send_text(ev,ev.location_id,"武器不存在，获取图片失败")

    return True

def headPicture2Image(b: bot, ev: event) -> bool:
    pass

def getWeatherMaolinbian(b: bot, ev: event) -> bool:
    pat = re.compile(
        '^天气 (.+)$'
    )  # 正则表达式
    it = re.findall(pat, ev.message)
    if it:
        city = it[0]
    else:
        return False
    url_mao_weather = 'https://api.caonm.net/api/qqtq/t?key=sp4mVsMIBiBslhw56QfpHDXIkg'
    response = requests.post(url_mao_weather, data={"msg":city})
    file_name = Path(img_root,'temp','mao_weather.jpg')
    if response.status_code == 200:
        with file_name.open('wb') as file:
            file.write(response.content)
            b.send_image(ev,ev.location_id,"file:///"+file_name)
            file_name.rmdir()
    else:
        b.send_text(ev,ev.location_id,"获取图片失败")

    return True


# this functions must be standard
function_list = [genshinCharactorImage,genshinCharactorMsg,getWeatherMaolinbian]