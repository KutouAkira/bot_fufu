# 关联https://github.com/yahoo/open_nsfw
# 关联https://github.com/devzwy/NSFW-Python
import os
import random
import requests
import string
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import At, Plain, Image
from graia.broadcast import ExecutionStop
from loguru import logger
from aip import AipImageCensor
from .NSFW import getResultFromFilePathByTFLite as tfi
from .NSFW import getResultFromFilePathByPyModle as bpm
from .sender_filter_query_handler import SenderFilterQueryHandler


class AntiEro(SenderFilterQueryHandler):
    def judge(self, app: GraiaMiraiApplication,
              subject: T.Union[Group, Friend],
              message: MessageChain):
        super().judge(app, subject, message)
        if message.get(Image):
            return
        raise ExecutionStop()

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:
        imgs = message.get(Image)
        flag = False
        for img in imgs:
            file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
            open(file_name, 'wb').write(requests.get(img.url).content)
            avg = bpm(file_name)[1] + tfi(file_name)[1]
            os.remove(file_name)
            logger.info(avg / 2)
            if avg / 2 > 0.8:
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
            yield msg