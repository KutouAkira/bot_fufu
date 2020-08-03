# 二刺螈人物生日，数据来源萌娘百科
import requests
import time
from bs4 import BeautifulSoup
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups

class birthday(reactor):
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

    def birthday(self):
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

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        if self.__check__(user, message):
            message = [Plain(self.birthday())]
            yield message
