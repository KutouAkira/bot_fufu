# https://www.internationalsaimoe.com/
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups
import requests
from bs4 import BeautifulSoup
import time
import datetime
import re

class ISML(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        msg = plain_str(message)

        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            result = search_groups(key, ["$obj"], msg)
            if result:
                return result
        return False

    def ISML(self):
        class moeEvevt:
            eventTime = 0
            eventName = ""

        url = "https://www.internationalsaimoe.com/"
        msg = ""

        result = requests.get(url).content
        soup = BeautifulSoup(result, 'html.parser')
        res_now = soup.find_all('h2', class_='currentEvent center-text')
        res_future = soup.find_all('h4', class_='upcomingEvent')
        regex = r"(Nominations|Aquamarine|Topaz|Amethyst|Sapphire|Emerald|Ruby|Diamond|Elimination) [1-9]"
        events = []
        if len(res_now) > 0:
            for event in res_now:
                moe = moeEvevt()
                moe.eventTime = int(time.mktime(time.strptime(event['data-end'][:-6], "%Y-%m-%dT%H:%M:%S"))) + 28800
                moe.eventName = re.search(regex, event.text).group().replace("Nominations", "海选").\
                    replace("Aquamarine","海蓝宝石").replace("Topaz", "黄玉").replace("Amethyst", "紫水晶").\
                    replace("Sapphire", "蓝宝石").replace("Emerald","翡翠").replace("Ruby","红宝石").\
                    replace("Diamond", "钻石").replace("Elimination", "淘汰赛")
                events.append(moe)

        for event in res_future:
            moe = moeEvevt()
            moe.eventTime = int(time.mktime(time.strptime(event['data-start'][:-6], "%Y-%m-%dT%H:%M:%S"))) + 28800
            moe.eventName = re.search(regex, event.text).group().replace("Nominations", "海选").\
                    replace("Aquamarine","海蓝宝石").replace("Topaz", "黄玉").replace("Amethyst", "紫水晶").\
                    replace("Sapphire", "蓝宝石").replace("Emerald","翡翠").replace("Ruby","红宝石").\
                    replace("Diamond", "钻石").replace("Elimination", "淘汰赛")
            events.append(moe)

        for event in events:
            msg += event.eventName+"\n"
            if event.eventTime - 24*60*60 < int(time.time()):
                leftTime = event.eventTime - int(time.time())
                m, s = divmod(leftTime, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                msg += '还有: %d天%02d小时%02d分%02d秒结束' % (d, h, m, s)
            else:
                msg += "开始于: " + str(datetime.datetime.fromtimestamp(event.eventTime))
            if event is not events[-1]:
                msg += "\n\n"

        return msg

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        if self.__check__(user, message):
            message = [Plain(self.ISML())]
            yield message
