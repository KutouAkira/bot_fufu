# API来自互联网
import requests
import json
import time
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups

url = 'https://bangumi.bilibili.com/web_api/timeline_global'
youbi_map = {'前天的': 4, '昨天的': 5, '今天的': 6, '明天的': 7, '后天的': 8}


class bangumi(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain, member: Member):
        msg = plain_str(message)

        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group or member.id in self.ban:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            day = search_groups(key, ["$day"], msg)
            if day is None:
                return False
            elif str(day) == "['']":
                return 6
            else:
                return youbi_map[day[0]]
        return False

    def get_bangumi(self, youbi: int):
        json_res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                            'Chrome/81.0.4044.122 Safari/537.36'}).text
        res = json.loads(json_res)
        ret = ''
        now = time.strftime("%m.%d %H:%M", time.localtime())
        delay = []
        for i in res['result'][youbi]['seasons']:
            if not i['delay']:
                ret += i['title'] + '\n'
                if youbi < 6:
                    t = '00.00 ' + i['pub_time']
                elif youbi > 6:
                    t = '99.99 ' + i['pub_time']
                else:
                    t = time.strftime("%m.%d ", time.localtime()) + i['pub_time']
                if t > now:
                    ret += i['pub_index'] + '将于' + i['pub_time'] + '更新\n\n'
                else:
                    ret += i['pub_index'] + '已于' + i['pub_time'] + '更新\n\n'
            else:
                delay.append(i['title'])
        ret = ret[:-2]
        if delay:
            ret += '\n\n' + '、'.join(delay) + '本周停更'
        return ret

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        day = self.__check__(user, message, member)
        if day:
            message = [Plain(self.get_bangumi(day))]
            yield message
