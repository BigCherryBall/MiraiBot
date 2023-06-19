# Mikky_cat
本项目主要是用python写了一个qq群聊机器人，项目是基于mirai项目的http-api-v2插件，目标是让所有会python语言的都能搭建一个用python开发的qq机器人。也做得蛮多东西了得，把凯露的代码发出来。具体整理得不太好，感觉还是有点乱，最后干脆摆了，反正也没啥人关注，就把ReadMe写得详细点就行了。作者是新手，弄得不太好，也还在学习当中。

具体而言就是绑定一个qq机器人号，向机器人账号发送信息mirai可以收到信息，并通过http-api插件把信息传到自己写的python脚本上，python处理相关信息后将得到应该回复的消息，再将消息通过mirai发送出去。

本项目主要包含的功能是：

1、抽卡小游戏（响应特定关键词，然后发送回一段文字描述以及一张抽卡结果的图片）

2、定时任务（每天8点以及21点向发送过消息的群聊，发送一首诗词作为问候）

3、chatgpt聊天api（实现了私聊以及群聊两种方式，为每个用户设立单独的存储列表，用来存用户的历史记录，进而实现持续的聊天）

4、网页截屏（响应用户发送的消息内携带网址的片段，使用爬虫访问对应网址并截屏）

~~5、AI绘画（之前是实现了的，但作者太懒，没更新模型，后面就舍弃了。有需要作者再考虑少打几把LOL来加回去）~~

~~6、原本还有写数据库的，若干个版本后懒惰了，就没这块内容了，也是懒得，同时也是没啥用户使用，有需求的话，我再加回去。~~

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

替换机器人qq号，在bott.py脚本里面，搜索作者的机器人账号`3498250046`,将其替换为自己的即可。

替换作者qq号，在bott.py脚本里面，搜索作者的账号`837979619`,将其替换为自己的即可。

替换项目的绝对路径，在bott.py脚本里面，将basePath的值改为本项目的本地路径即可。

## python3使用到的相关的库汇总

```
pip install requests asyncio schedule openai
```

### 代理的说明

代码中使用到了科学上网，代理的相关代码在bott.py里面，将其改为自己vpn的设定即可，因为openai需要用到，不需要的话注释掉即可。

## 运行本项目

先把mirai跑起来，然后在mirai上登录上自己的机器人账号。随后再进入本项目的目录，运行脚本bott.py。

## 一些说明

### bot类的扩展，收发消息啥的

在bott.py文件下，有class bot类，下面有deal_data方法，这个是bot收发消息的主要代码模块，在这里更改即可，ev.message是收到的消息，ev.at代表消息的开头at了机器人bot，处理完后，通过send的一系列函数，把消息再发回去，发送带图片的消息的方法，参考WebShot函数下面的self.send_group_msg函数的使用。（~~~有一说一，堆砌if-else结构确实有点笨笨的。不过作者把无参数要求的方法使用字典调用，具体在function_no_pam这个变量上~~~）

在bott.py文件下，有event类，我把消息大致处理为这个类的各种属性了。有message代表收到的消息，at代表是否有人at本bot，group_id代表群聊号，sender_id发送消息者的qq号，此外私聊也有着私聊的设定。我本来也把发送者，如果有发图片类型的数据应该怎么处理也做了，这部分是在ai绘画上面，但后面人懒了。具体而言，图片信息就是一个网址，可以在我打印的信息里面看到messageChain下面看到，对应的网址，然后去这个网址上面把图片获取到即可。我把这个网址放在image上了。

### 使用协程来实现定时任务

具体这方面的内容在bott.py的run方法里面，使用schedule绑定定时需要触发的方法即可。

## 写在最后

本项目bott.py是主要的模块，其他的文件都只是一些模块文件罢了，运行的话配好环境只需要运行起来bott即可。

作者只是个半路出家，凭借自己的喜好去编程的爱好者。所以很多内容都不规范，我也想写得好一点，但所有得东西基本都是自学得，没什么人带，所以有什么问题或者改进，请务必告诉作者，如何能做得更好，谢谢。

作者qq：837979619

另外作者申请到了chat4的权限，还在开发一些响应的小功能，如果有什么想法，也可以一起聊聊。
