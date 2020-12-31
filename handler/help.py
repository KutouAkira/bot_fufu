import asyncio
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from loguru import logger
from .abstract_message_handler import AbstractMessageHandler

help_str = '''命令列表：
 - 打仗(查看世萌赛事)
 - 好好说话 +句子(翻译缩写)
 - 搜图+图片(SauceNAO搜索)
 - 二刺螈生日(今天是哪些角色的生日)
 - 邦 +服务器代号(jp,en,tw,cn,kr)查看活动信息
 - 开车/爆破(普通/R18色图),后跟字母G/C(灰色色/迷彩幻影坦克)
 - 看(前天/昨天/今天/明天/后天的)番(默认今天，数据来自bilibili)
 - 烤肉 原语言 目标语言 句子(注意空格，中文:zh，英语:en，日文:jp)
'''

class Help(AbstractMessageHandler):
    text: str

    def __init__(self, tag: str, settings: dict, **kwargs):
        super().__init__(tag, settings, **kwargs)
        self.text = help_str

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
        logger.info("Send help ok")
        return True
