# MiraiBot丸子
本项目主要是用python写了一个qq群聊机器人，项目是基于mirai项目的http-api-v2插件，目标是让所有会python语言的都能搭建一个用python开发的qq机器人。也做得蛮多东西了得，把丸子的代码发出来。反正也没啥人看，就把ReadMe写得详细点就行了。作者是新手，弄得不太好，也还在学习当中。

具体而言就是绑定一个qq机器人号，向机器人账号发送信息mirai可以收到信息，并通过http-api插件把信息传到自己写的python脚本上，python处理相关信息后将得到应该回复的消息，再将消息通过mirai发送出去。

本项目主要包含的功能是：

1、中国象棋

2、定时任务（每天9点以及21点向发送过消息的群聊，发送一首诗词作为问候）

3、chatgpt聊天api（实现了私聊以及群聊两种方式，为每个用户设立单独的存储列表，用来存用户的历史记录，进而实现持续的聊天）

4、角色扮演

5、防撤回


## Mirai安装
先安装mirai以及http-v2的插件，这里不对mirai如何安装使用进行说明，因为没啥人看，有需要的话作者会更新。

这里放点链接以及群聊

[mirai论坛](https://mirai.mamoe.net/)

有个别人建的mirai的qq讨论群群：780594692

本人是使用mcl的，用core也行，反正是用的http-api开发的：

[mirai-mcl](https://github.com/iTXTech/mirai-console-loader)

配置号mirai,可以运行后，下载并将http-v2的插件放到plugins文件夹下，重新启动mirai即可自动完成安装：

[http-api插件](https://github.com/project-mirai/mirai-api-http/releases)

具体内容关注这个，也可以不看，因为我都封装到even类里面，处理好了的：

[http-v2插件的官方文档说明](https://docs.mirai.mamoe.net/mirai-api-http/api/API.html#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%88%90%E5%91%98%E5%88%97%E8%A1%A8)

### 需要注意一点，绑定python脚本以及mirai

在成功运行上http-api插件后，会在mirai-mcl\config\net.mamoe.mirai-api-http路径下生成setting.yml文件，查看文件里面http的端口，以及verifyKey。

在文件bott.py的这里，将作者的port以及authKey改成使用者的（~~话说，把自己使用着的密钥放上去真的好么~~）

```
class bot():
    def __init__(self,address,port=8080,authKey="INITKEYTgtK4P"):
        self.conn = http.client.HTTPConnection(address,port)
        self.authKey=authKey
        self.sessionKey=self.bind()
```

替换机器人qq号，在bot.py脚本里面，搜索作者的机器人账号`1969712698`,将其替换为自己的即可。

替换作者qq号，在feature.py脚本里面，搜索作者的账号`2655`,将其替换为自己的即可。

替换本地图库的绝对路径：
①在feature.py脚本里面，将basePath的值改为本项目的本地路径即可。
②在chesses.py里面，替换pic-root的路径

## python3使用到的相关的库汇总

```
pip install requests asyncio schedule openai
```

### 代理的说明

代码中使用到了科学上网，代理的相关代码在bot.py里面，将其改为自己vpn的设定即可，因为openai需要用到，不需要的话注释掉即可。

## 运行本项目

先把mirai跑起来，然后在mirai上登录上自己的机器人账号。随后再进入本项目的目录，运行脚本bot.py。

## 一些说明

## #重要： bot类，event类，feature脚本的关系
event类：封装了来自Mirai的消息，将其变为方便的成员变量；

feature脚本，里面是各种各样的功能函数，函数的参数通常是：b:机器人对象，ev：event对象；返回值是bool类型。把所有的功能函数写在这个脚本里。这些函数通过ev.massage获取消息，并判断这个消息是否触发功能，触发了返回True，没触发返回False。feature中的函数通过b.send_msg()函数发送消息。

在bot.py文件下，有class bot类，下面有deal_data方法，这个是bot处理消息的代码。Bot将收到的消息创建为event对象ev，在deal_data里面将ev,self交给feature中的功能函数一一辨认。

#象棋模块chesses里面是一些算法，不用看
主要看game_control类向外提供的接口

event类，我把消息大致处理为这个类的各种属性了。有message代表收到的消息，at代表是否有人at本bot，sender关心发送者，location_id关心发送的地点在哪里，私聊消息发送地等于发送者。

### 使用协程来实现定时任务

具体这方面的内容在bot.py的run方法里面，使用schedule绑定定时需要触发的方法即可。

## 写在最后

本项目bot.py是入口，其他的文件都只是一些模块文件罢了，运行的话配好环境只需要运行起来bot即可。

作者只是个半路出家，凭借自己的喜好去编程的爱好者。所以很多内容都不规范，我也想写得好一点，但所有得东西基本都是自学得，没什么人带，所以有什么问题或者改进，请务必告诉作者，如何能做得更好，谢谢。

作者qq：2655602003

另外作者的一个朋友申请到了chat4的权限，还在开发一些响应的小功能，如果有什么想法，也可以一起聊聊。


[参考项目：Mikky-cat](https://github.com/Mikky574/Mikky_cat)
