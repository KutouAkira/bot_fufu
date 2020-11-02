# https://bandori.ga
# https://bestdori.com
# API来自互联网
import http.client
import json
import time
import datetime
import typing as T
from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain, Image_NetworkAddress
from utils import match_groups
from loguru import logger

from .sender_filter_query_handler import SenderFilterQueryHandler


class BangDream(SenderFilterQueryHandler):
    def __find_server(self, message: MessageChain) -> T.Optional[str]:
        content = message.asDisplay()
        for x in self.trigger:
            result = match_groups(x, ['$server'], content)
            if result is None:
                continue
            return result['$server']
        return None

    def getEventId(self, events, serverId):
        if events:
            now = int(time.time()) * 1000
            eventId = None
            end = None
            for i in events:
                event = events[i]
                if event['endAt'][serverId] != None and int(event['endAt'][serverId]) > now and (
                        eventId == None or int(event['endAt'][serverId]) < end):
                    eventId = int(i)
                    end = int(event['endAt'][serverId])
            if eventId:
                return eventId, None
            eventId = None
            end = None
            for i in events:
                event = events[i]
                if event['endAt'][serverId] != None and (eventId == None or int(event['endAt'][serverId]) > end):
                    eventId = int(i)
                    end = int(event['endAt'][serverId])
            if len(events) == eventId:
                logger.info(f"EventId is {eventId}, no next event.")
                return eventId, None
            logger.info(f"EventId is {eventId}, may no next event.")
            return eventId, eventId+1 if events[str(eventId+1)] else None
        logger.info("No events.")
        return None, None

    def bang(self, q):
        bestDR = None
        banDR = None
        res = []
        chinese_dict = dict(zip(['日', '英', '台', '国', '韩'], ['jp', 'en', 'tw', 'cn', 'kr']))
        if not q.islower() and not q.isupper():
            q = chinese_dict[q]
        if q.isupper():
            q = q.lower()
        server = dict(zip(['jp', 'en', 'tw', 'cn', 'kr'], [0, 1, 2, 3, 4]))
        next_event = None
        try:
            # 获取活动id
            # if self.proxy:
            #     banDR = http.client.HTTPSConnection(self.proxy_server, self.proxy_port)
            #     banDR.set_tunnel('api.bandori.ga')
            # else:
            #     banDR = http.client.HTTPSConnection('api.bandori.ga')
            # banDR.request('GET', '/v1/' + q + '/event')
            # response = banDR.getresponse()
            # result_all = response.read().decode("utf-8")
            # event_id = str(json.loads(result_all)['eventId'])

            # 获取活动信息
            if self.proxy:
                bestDR = http.client.HTTPSConnection(self.proxy_server, self.proxy_port)
                bestDR.set_tunnel('bestdori.com')
            else:
                bestDR = http.client.HTTPSConnection('bestdori.com')
            bestDR.request('GET', '/api/events/all.3.json')
            response = bestDR.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            event_id, next_event = self.getEventId(result, int(server[q]))
            result = json.loads(result_all)[str(event_id)]
            name = result['eventName'][int(server[q])]
            banner = 'https://bestdori.com/assets/' + q + '/homebanner_rip/' + result['bannerAssetBundleName'] + '.png'

            # 处理活动时间
            start_timestamp = result['startAt'][int(server[q])]
            end_timestamp = result['endAt'][int(server[q])]
            start_time = datetime.datetime.fromtimestamp(int(start_timestamp[:-3]))
            end_time = datetime.datetime.fromtimestamp(int(end_timestamp[:-3]))
            now = datetime.datetime.fromtimestamp(int(time.time()))
            restr = '\n名称: ' + name + '\n开始于: ' + str(start_time) + '\n结束于: ' + str(end_time)

            # 处理剩余时间
            pre = int((start_time - now).total_seconds())
            left = int((end_time - now).total_seconds())
            if pre > 0:
                m, s = divmod(pre, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                restr += '\n还有: %d天%02d小时%02d分%02d秒开始' % (d, h, m, s)
            elif left > 0:
                m, s = divmod(left, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                restr += '\n剩余: %d天%02d小时%02d分%02d秒' % (d, h, m, s)
            else:
                left = int((now - end_time).total_seconds())

                m, s = divmod(left, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                restr += '\n已结束: %d天%02d小时%02d分%02d秒' % (d, h, m, s)
            res.append(banner)
            res.append(restr)

            # 处理日服外其他服的下一个活动
            if next_event:
                next_result = json.loads(result_all)[str(next_event)]
                next_name = next_result['eventName'][0]
                next_banner = 'https://bestdori.com/assets/jp/homebanner_rip/' + next_result[
                    'bannerAssetBundleName'] + '.png'
                next_restr = '\n名称: ' + next_name
                res.append(next_banner)
                res.append(next_restr)

        except Exception as e:
            print(e)

        finally:
            if bestDR:
                bestDR.close()
            # if banDR:
            #     banDR.close()
        return res, next_event

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:

        req = self.__find_server(message)
        if req:
            result, next_event = self.bang(req)
            msg = MessageChain.create([
                Image_NetworkAddress(result[0]),
                Plain(result[1])
            ])
            if next_event:
                msg = MessageChain.join(msg, MessageChain.create([
                    Plain("\n下一个活动(未开始):\n"),
                    Image_NetworkAddress(result[2]),
                    Plain(result[3])
                ]))
            yield msg
