# API来自互联网
import requests
import json
import time
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain
from loguru import logger
from utils import match_groups

from .sender_filter_query_handler import SenderFilterQueryHandler

url = 'https://bangumi.bilibili.com/web_api/timeline_global'
youbi_map = {'前天的': 4, '昨天的': 5, '今天的': 6, '明天的': 7, '后天的': 8}


class Bangumi(SenderFilterQueryHandler):
    def __find_youbi(self, message: MessageChain):
        content = message.asDisplay()
        for x in self.trigger:
            result = match_groups(x, ['$day'], content)
            if result is None:
                continue
            if result['$day'] is None:
                return False
            elif str(result['$day']) == '':
                return 6
            elif result['$day'] not in youbi_map:
                return False
            else:
                return youbi_map[result['$day']]
        return False

    def __get_bangumi(self, youbi: int):
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

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:
        day = self.__find_youbi(message)
        if day:
            msg = MessageChain.create([Plain(self.__get_bangumi(day))])
            logger.info(f"Find bangumi: {day}")
            yield msg
