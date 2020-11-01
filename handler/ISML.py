# https://www.internationalsaimoe.com/
import requests
from bs4 import BeautifulSoup
import time
import datetime
import re
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain
from graia.broadcast import ExecutionStop
from loguru import logger

from .sender_filter_query_handler import SenderFilterQueryHandler


class ISML(SenderFilterQueryHandler):
    def judge(self, app: GraiaMiraiApplication,
              subject: T.Union[Group, Friend],
              message: MessageChain):
        super().judge(app, subject, message)
        content = message.asDisplay()
        for x in self.trigger:
            if x in content:
                return
        raise ExecutionStop()

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

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:

        msg = MessageChain.create([Plain(self.__isml())])
        logger.info("Send ISML info")
        yield msg
