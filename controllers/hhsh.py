# https://lab.magiconch.com/
# API来自互联网
import typing as T
import json
import requests
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups


class hhsh(reactor):
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

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        result = self.__check__(user, message)
        if result:
            message = [Plain(self.hhsh(result[0]))]
            yield message
