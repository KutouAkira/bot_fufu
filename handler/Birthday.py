# 二刺螈人物生日，数据来源萌娘百科
import requests
import time
from bs4 import BeautifulSoup
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain
from graia.broadcast import ExecutionStop
from loguru import logger

from .sender_filter_query_handler import SenderFilterQueryHandler


class Birthday(SenderFilterQueryHandler):
    def judge(self, app: GraiaMiraiApplication,
              subject: T.Union[Group, Friend],
              message: MessageChain):
        super().judge(app, subject, message)
        content = message.asDisplay()
        for x in self.trigger:
            if x in content:
                return
        raise ExecutionStop()

    def __birthday(self):
        year = time.strftime("20%y", time.localtime())
        month = time.strftime("%#m", time.localtime())
        day = time.strftime("%#d", time.localtime())
        url = f"https://zh.moegirl.org.cn/Category:{month}月{day}日"
        req = requests.get(url).content
        soup = BeautifulSoup(req, 'html.parser')
        res = soup.find('div', id='mw-pages').find_all('a')
        msg = f"今天是{year}年{month}月{day}日\n今天生日的二刺螈人物有: "
        for people in res:
            msg += '\n' + people.string
        return msg

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:

        msg = MessageChain.create([Plain(self.__birthday())])
        yield msg
        logger.info("Send birthday info.")
