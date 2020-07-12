import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str


help = '''命令列表：
 - 好好说话 +句子(翻译缩写)
 - 搜图+图片(SauceNAO搜索)
 - 邦 +服务器代号(jp,en,tw,cn,kr)查看活动信息
 - 开车/爆破(普通/R18色图),后跟字母G/C(灰色色/迷彩幻影坦克)
 - 看(前天/昨天/今天/明天/后天的)番(默认今天，数据来自bilibili)
 - 翻译 原语言 目标语言 句子(注意空格，中文:zh，英语:en，日文:jp)
'''

class Help(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        msg = plain_str(message)

        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            if key == msg:
                return True
        return False

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        if self.__check__(user, message):
            message = [
                Plain(help),
                Image.fromFileSystem('static/mirai.png')
            ]
            yield message
