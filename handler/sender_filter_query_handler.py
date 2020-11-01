import abc
import typing as T

from graia.application import GraiaMiraiApplication, Group, Friend, MessageChain
from graia.broadcast import Broadcast, ExecutionStop

from handler.abstract_message_handler import AbstractMessageHandler


class SenderFilterQueryHandler(AbstractMessageHandler, metaclass=abc.ABCMeta):
    def __init__(self, tag: str,
                 settings: dict,
                 bcc: Broadcast):
        super().__init__(tag, settings, bcc)
        self.allow_friend = settings['friend'] if settings['enable'] else []
        self.allow_group = settings['group'] if settings['enable'] else []

    def judge(self, app: GraiaMiraiApplication,
              subject: T.Union[Group, Friend],
              message: MessageChain) -> T.NoReturn:
        if isinstance(subject, Group):
            if (self.allow_group is not None) and (subject.id not in self.allow_group):
                raise ExecutionStop()
        elif isinstance(subject, Friend):
            if (self.allow_friend is not None) and (subject.id not in self.allow_friend):
                raise ExecutionStop()
