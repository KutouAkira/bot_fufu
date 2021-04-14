# 关联https://github.com/yahoo/open_nsfw
# 关联https://github.com/devzwy/NSFW-Python
import os
import random
import asyncio
import requests
import string
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend, Member
from graia.application.message.elements.internal import At, Plain, Image
from aip import AipImageCensor
from .NSFW import getResultFromFilePathByTFLite as tfi
from .NSFW import getResultFromFilePathByPyModle as bpm
from loguru import logger
from .abstract_message_handler import AbstractMessageHandler

class AntiEro(AbstractMessageHandler):
    def __judge(self, imgs):
        flag = False
        for img in imgs:
            file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
            open(file_name, 'wb').write(requests.get(img.url).content)
            avg = (bpm(file_name)[1] + tfi(file_name)[1]) / 2
            os.remove(file_name)
            logger.info(avg)
            if avg > self.threshold:
                # 使用百度智能云判断
                bdclient = AipImageCensor(self.APP_ID, self.API_KEY, self.SECRET_KEY)
                result = bdclient.imageCensorUserDefined(img.url)
                logger.info(result)
                if result['conclusion'] != '合规':
                    msg = MessageChain.create([
                        At(self.admin),
                        Plain('\n我看见了，有人发涩图')
                    ])
                    flag = True
                    break
        if flag:
            return msg
        else:
            return False

    async def handle(self, app: GraiaMiraiApplication,
                     subject: T.Union[Group, Friend],
                     message: MessageChain,
                     member: Member,
                     channel: asyncio.Queue) -> bool:
        # 检测是否触发
        imgs = message.get(Image)
        judge = self.__judge(imgs)

        if judge:
            await channel.put(judge)
            return True