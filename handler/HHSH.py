# https://lab.magiconch.com/
# API来自互联网
import asyncio
import json
import requests
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend, Member
from loguru import logger
from utils import match_groups

from .abstract_message_handler import AbstractMessageHandler


class HHSH(AbstractMessageHandler):
    def __find_obj(self, message: MessageChain) -> T.Optional[str]:
        content = message.asDisplay()
        for x in self.trigger:
            result = match_groups(x, ['$obj'], content)
            if result is None:
                continue
            return result['$obj']
        return None

    def hhsh(self, req):
        result = ''
        url = 'https://lab.magiconch.com/api/nbnhhsh/guess'
        head = {'Content-Type': 'application/json'}
        re = {'text': req}
        print(re)
        try:
            post_res = requests.post(url, headers=head, json=re, timeout=3).text
            res = json.loads(post_res)
            try:
                for i in res[0]['trans']:
                    result += '\n' + i
            except:
                result = '\n尚未收录'
        except:
            result = "连接超时"
        return result

    async def handle(self, app: GraiaMiraiApplication,
                     subject: T.Union[Group, Friend],
                     message: MessageChain,
                     member: Member,
                     channel: asyncio.Queue) -> bool:
        # 检测是否触发
        result = self.__find_obj(message)

        if result:
            await channel.put(self.hhsh(result))
            logger.info(f"Find define of {result}")
            return True
