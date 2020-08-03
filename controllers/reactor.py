import traceback
import typing as T
import asyncio
import re
import os
from mirai import *
from mirai.event.message.base import BaseMessageComponent
from mirai.image import InternalImage


async def reply(bot: Mirai,
                source: Source,
                user: T.Union[Group, Friend],
                message: T.Union[MessageChain,
                                 BaseMessageComponent,
                                 T.Sequence[T.Union[BaseMessageComponent,
                                                    InternalImage]],
                                 str]) -> T.NoReturn:
    """
    回复消息。若是群组则引用回复，若是好友则普通地回复。
    :param bot: Mirai Bot实例
    :param source: 原消息的Source
    :param user: 回复的对象
    :param message: 回复的消息
    """
    if isinstance(message, tuple):
        message = list(message)
    if isinstance(user, Group):
        await bot.sendGroupMessage(group=user, message=message, quoteSource=source)
        # 自动清理car相关函数在tmp下生成的图片
        if isinstance(message[0], mirai.image.LocalImage) and "tmp" in str(message[0].path):
            os.remove(str(message[0].path).replace('\\', '/'))

    elif isinstance(user, Friend):
        await bot.sendFriendMessage(friend=user, message=message)
        if isinstance(message[0], mirai.image.LocalImage) and "tmp" in str(message[0].path):
            os.remove(str(message[0].path).replace('\\', '/'))


def plain_str(message: MessageChain) -> str:
    """
    提取消息中的文本
    """
    return ' '.join([x.toString() for x in message.getAllofComponent(Plain)])


def search_groups(pattern: str, flags: T.Sequence[str], text: str) -> T.Optional[T.List[T.Optional[str]]]:
    flags_order = dict()
    for i, flag in enumerate(flags):
        flags_order[flag] = i

    position = []
    regex = pattern
    for flag in flags:
        p = pattern.find(flag)
        if p != -1:
            position.append((flag, p))
            regex = regex.replace(flag, "(.*?)")
            regex += "$"
    position.sort(key=lambda x: x[1])

    match_result = re.search(regex, text)

    if match_result is None:
        return None
    else:
        ans = dict()
        for i, (flag, p) in enumerate(position):
            ans[flag] = match_result.group(i + 1)

        ans_sorted = []
        for flag in flags:
            if flag not in ans:
                ans_sorted.append((None, flags_order[flag]))
            else:
                ans_sorted.append((ans[flag], flags_order[flag]))
        ans_sorted.sort(key=lambda x: x[1])

        return [x[0] for x in ans_sorted]


class reactor:
    def __init__(self, settings: dict):
        self.settings = settings

    def __getattr__(self, item):
        return self.settings[item]

    async def generate_reply(self, bot: Mirai, source: Source, subject: T.Union[Group, Friend], message: MessageChain, member: Member):
        raise NotImplementedError
        yield

    async def react(self, bot: Mirai, source: Source, user: T.Union[Group, Friend],
                    message: MessageChain, member: Member) -> T.NoReturn:
        """
        接收消息
        :param bot: Mirai Bot实例
        :param source: 消息的Source
        :param user: 消息的发送对象
        :param message: 消息
        """
        try:
            tasks = []
            async for msg in self.generate_reply(bot, source, user, message, member):
                tasks.append(reply(bot, source, user, msg))
            await asyncio.gather(*tasks)
        except Exception as e:
            traceback.print_exc()
            await reply(bot, source, user, [Plain(str(e)[:128])])
