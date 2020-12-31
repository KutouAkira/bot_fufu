import asyncio
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from loguru import logger

from .abstract_message_handler import AbstractMessageHandler

class Template(AbstractMessageHandler):
    def __init__(self, tag: str, settings: dict, **kwargs):
        super().__init__(tag, settings, **kwargs)

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

        await channel.put(self.text)
        logger.info("Send ok")
        return True
