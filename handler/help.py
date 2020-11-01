import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain
from graia.broadcast import ExecutionStop
from loguru import logger

from .sender_filter_query_handler import SenderFilterQueryHandler

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


class Help(SenderFilterQueryHandler):
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

        msg = MessageChain.create([Plain(help_str)])
        yield msg
        logger.info("Send help ok")
