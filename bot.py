import typing as T
import requests
import json5
from mirai import *
from controllers import AntiEro, Help, Translate, hhsh, bangumi, bang, SauceNAO, cars, birthday, ISML
from controllers.reactor import reactor, plain_str, search_groups

# 初始化
try:
    with open("settings.json", "r", encoding="utf8") as f:
        settings = json5.load(f)
    print("Load seetings successfully")

except Exception as e:
    print(e)
    quit()
qq = settings["mirai"]["qq"]
server = settings["mirai"]["server"]
port = settings["mirai"]["port"]
authKey = settings["mirai"]["auth_key"]
mirai_api_http_locate = f"{server}:{port}/"
if settings["mirai"]["enable_ws"]:
    mirai_api_http_locate = mirai_api_http_locate + "ws"
try:
    bot = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")
    print(f"Connected to {mirai_api_http_locate}")
except Exception as e:
    print(e)
    quit()
# 初始化完成

# 一些管理群用的奇葩功能可以加在这，如果私聊bot使用这个命令可能会导致空消息使Mirai崩溃
class sudo(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        msg = plain_str(message)

        if isinstance(user, Group):
            if user.id not in self.group or member.id not in self.admin:
                return False
        elif isinstance(user, Friend):
            if self.admin is not None and user.id not in self.admin:
                return False

        for key in self.trigger:
            result = search_groups(key, ["$cmd", "$obj"], msg)
            if result is not None:
                return result
            return False

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        result = self.__check__(user, message, member)
        if result:
            cmd, obj = result
            if cmd == "list" and obj == "msg":
                message = [Plain('\n'.join(str(msgid) for msgid in recall_list))]
            elif cmd == "recall" and obj:
                msg = requests.get(f"http://{mirai_api_http_locate}messageFromId?sessionKey={bot.session_key}&id={obj}").text
                message = [Plain(msg)]
            yield message


# 控制器列表
controllers = {
    "sudo": sudo(settings["controllers"]["sudo"]),
    "AntiEro": AntiEro(settings["controllers"]["AntiEro"]),
    "Help": Help(settings["controllers"]["Help"]),
    "Translate": Translate(settings["controllers"]["Translate"]),
    "hhsh": hhsh(settings["controllers"]["hhsh"]),
    "bangumi": bangumi(settings["controllers"]["bangumi"]),
    "bang": bang(settings["controllers"]["bang"]),
    "SauceNAO": SauceNAO(settings["controllers"]["SauceNAO"]),
    "cars": cars(settings["controllers"]["cars"]),
    "birthday": birthday(settings["controllers"]["birthday"]),
    "ISML": ISML(settings["controllers"]["ISML"])
}

recall_list = []


# 将消息传入所有控制器
async def receive(bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
    for key in controllers:
        await controllers[key].react(bot, source, user, message, member)


@bot.receiver("GroupMessage")
async def group_receiver(bot: Mirai, source: Source, group: Group, message: MessageChain, member: Member):
    await receive(bot, source, group, message, member)


@bot.receiver("FriendMessage")
async def friend_receiver(bot: Mirai, source: Source, friend: Friend, message: MessageChain):
    await receive(bot, source, friend, message, None)


# 简单的防撤回实现
@bot.receiver("GroupRecallEvent")
async def cache_msg(event: GroupRecallEvent):
    recall_list.append(event.messageId)

if __name__ == "__main__":
    bot.run()
