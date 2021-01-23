# 二刺螈人物生日，数据来源萌娘百科
import asyncio
import requests
import time
from bs4 import BeautifulSoup
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend, Member
from loguru import logger

from .abstract_message_handler import AbstractMessageHandler


class Birthday(AbstractMessageHandler):
    def __birthday(self):
        year = time.strftime("20%y", time.localtime())
        month = time.strftime("%#m", time.localtime())
        day = time.strftime("%#d", time.localtime())
        url = f"https://zh.moegirl.org.cn/Category:{month}月{day}日"
        req = requests.get(url).content
        soup = BeautifulSoup(req, 'html.parser')
        res = soup.find('div', class_='mw-category').find_all('a')
        msg = f"今天是{year}年{month}月{day}日\n今天生日的二刺螈人物有: "
        for people in res:
            msg += '\n' + people.string
        return msg

    async def handle(self, app: GraiaMiraiApplication,
                     subject: T.Union[Group, Friend],
                     message: MessageChain,
                     member: Member,
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

        await channel.put(self.__birthday())
        logger.info("Send birthday info.")
        return True
