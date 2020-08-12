# https://bandori.ga
# https://bestdori.com
# API来自互联网
import http.client
import json
import time
import datetime
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups


class bang(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        msg = plain_str(message)

        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            result = search_groups(key, ["$server"], msg)
            if result:
                return result
        return False

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
            return eventId, eventId+1 if events[str(eventId+1)] else None
        return None, None

    def bang(self, q):
        bestDR = None
        banDR = None
        res = []
        server = dict(zip(['jp', 'en', 'tw', 'cn', 'kr'], [0, 1, 2, 3, 4]))
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
            res.append('https://http.cat/500')
            res.append(str(e))

        finally:
            if bestDR:
                bestDR.close()
            # if banDR:
            #     banDR.close()
        return res, next_event

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        req = self.__check__(user, message)
        if req:
            result,next_enent = self.bang(req[0])
            message = [
                await Image.fromRemote(result[0]),
                Plain(result[1])
            ]
            if next_enent:
                message.append(Plain("\n下一个活动(未开始):\n"))
                message.append(await Image.fromRemote(result[2]))
                message.append(Plain(result[3]))
            yield message
