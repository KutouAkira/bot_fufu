# 关联https://github.com/yahoo/open_nsfw
# 关联https://github.com/devzwy/NSFW-Python
import os
import random
import requests
import string
import typing as T
from mirai import *
from controllers.reactor import reactor
from aip import AipImageCensor
from .NSFW import getResultFromFilePathByTFLite as tfi
from .NSFW import getResultFromFilePathByPyModle as bpm


class AntiEro(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            return False
        if not message.getFirstComponent(Image):
            return False
        return True

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        if self.__check__(user, message):
            img = str(message.getFirstComponent(Image)).split("'")[5]
            # 本地先使用Open_NSFW判断，减少API调用次数
            file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
            open(file_name, 'wb').write(requests.get(img).content)
            avg = bpm(file_name)[1] + tfi(file_name)[1]
            os.remove(file_name)
            print(avg / 2)
            if avg / 2 > 0.8:
                # 使用百度智能云判断
                bdclient = AipImageCensor(self.APP_ID, self.API_KEY, self.SECRET_KEY)
                result = bdclient.imageCensorUserDefined(img)
                print(result)
                if result['conclusion'] != '合规':
                    message = [
                                  At(self.admin),
                                  Plain('\n我看见了，有人发涩图')
                              ]
                    yield message
