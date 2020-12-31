# https://www.internationalsaimoe.com/
import asyncio
import requests
from bs4 import BeautifulSoup
import time
import datetime
import re
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from loguru import logger

from .abstract_message_handler import AbstractMessageHandler


class ISML(AbstractMessageHandler):
    def __isml(self):
        class moeEvevt:
            eventTime = 0
            eventName = ""

        url = "https://www.internationalsaimoe.com/"
        msg = ""

        result = requests.get(url).content
        soup = BeautifulSoup(result, 'html.parser')
        res_now = soup.find_all('h2', class_='currentEvent center-text')
        res_future = soup.find_all('h4', class_='upcomingEvent')
        regex = r"(Nominations|Aquamarine|Topaz|Amethyst|Sapphire|Emerald|Ruby|Diamond|Elimination) " \
                r"([1-9]|\(spring\)|\(summer\)|\(autumn\)|\(winter\))"
        events = []
        if len(res_now) > 0:
            for event in res_now:
                moe = moeEvevt()
                moe.eventTime = int(time.mktime(time.strptime(event['data-end'][:-6], "%Y-%m-%dT%H:%M:%S"))) + 28800
                moe.eventName = re.search(regex, event.text).group().replace("Nominations", "海选").\
                    replace("Aquamarine","海蓝宝石").replace("Topaz", "黄玉").replace("Amethyst", "紫水晶").\
                    replace("Sapphire", "蓝宝石").replace("Emerald","翡翠").replace("Ruby","红宝石").\
                    replace("Diamond", "钻石").replace("Elimination", "淘汰赛").replace("spring", "春季").\
                    replace("summer", "夏季").replace("autumn", "秋季").replace("winter", "冬季")
                events.append(moe)

        for event in res_future:
            moe = moeEvevt()
            moe.eventTime = int(time.mktime(time.strptime(event['data-start'][:-6], "%Y-%m-%dT%H:%M:%S"))) + 28800
            moe.eventName = re.search(regex, event.text).group().replace("Nominations", "海选").\
                    replace("Aquamarine","海蓝宝石").replace("Topaz", "黄玉").replace("Amethyst", "紫水晶").\
                    replace("Sapphire", "蓝宝石").replace("Emerald","翡翠").replace("Ruby","红宝石").\
                    replace("Diamond", "钻石").replace("Elimination", "淘汰赛").replace("spring", "春季").\
                    replace("summer", "夏季").replace("autumn", "秋季").replace("winter", "冬季")
            events.append(moe)

        for event in events:
            msg += event.eventName+"\n"
            if event.eventTime - 24*60*60 < int(time.time()) and len(res_now) > 0:
                leftTime = event.eventTime - int(time.time())
                m, s = divmod(leftTime, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                msg += '还有: %d天%02d小时%02d分%02d秒结束' % (d, h, m, s)
            elif event.eventTime - 24*60*60 < int(time.time()):
                leftTime = event.eventTime - int(time.time())
                m, s = divmod(leftTime, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                msg += '还有: %d天%02d小时%02d分%02d秒开始' % (d, h, m, s)
            else:
                msg += "开始于: " + str(datetime.datetime.fromtimestamp(event.eventTime))
            if event is not events[-1]:
                msg += "\n\n"

        return msg

    async def handle(self, app: GraiaMiraiApplication,
                     subject: T.Union[Group, Friend],
                     message: MessageChain,
                     channel: asyncio.Queue) -> bool:
        # 检测是否触发
        accept = False
        content = message.asDisplay()
        for x in self.trigger:
            if (self.trigger_mode == "match" and x == content) or (self.trigger_mode == "search" and x in content):
                accept = True
                break

        if not accept:
            return False

        await channel.put(self.__isml())
        logger.info("Send ISML info")
        return True
