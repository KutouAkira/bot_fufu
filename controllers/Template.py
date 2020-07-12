# 控制器模板
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups


class Templete(reactor):
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

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        if self.__check__(user, message):
            message = [Plain("Temp")]
            yield message
