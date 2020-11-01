import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain
from graia.broadcast import ExecutionStop
from loguru import logger

from .sender_filter_query_handler import SenderFilterQueryHandler


class Template(SenderFilterQueryHandler):
    def judge(self, app: GraiaMiraiApplication,
              subject: T.Union[Group, Friend],
              message: MessageChain):
        super().judge(app, subject, message)
        content = message.asDisplay()
        for x in self.trigger:
            if x in content:
                return
        raise ExecutionStop()

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:

        msg = MessageChain.create([])
        yield msg
        logger.info("")
