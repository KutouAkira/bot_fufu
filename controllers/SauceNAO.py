# https://saucenao.com
# 免费注册可以用API
import json
import io
import requests
from PIL import Image as PIL_Image
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str


class SauceNAO(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        msg = plain_str(message)

        if not message.getFirstComponent(Image):
            return False
        elif isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            if msg.find(key) != -1:
                return True
        return False

    def SauceNAO(self, imgurl):
        img = io.BytesIO()
        if self.proxy:
            img.write(requests.get(imgurl, proxies=self.proxy_dict).content)
        else:
            img.write(requests.get(imgurl).content)
        image = PIL_Image.open(img)
        image = image.convert('RGB')
        image.thumbnail(self.thumbSize, resample=PIL_Image.ANTIALIAS)
        imageData = io.BytesIO()
        image.save(imageData, format='PNG')

        url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim=' + self.minsim + '&db=999&api_key=' + self.api_key
        files = {'file': ("image.png", imageData.getvalue())}
        imageData.close()

        while True:
            r = requests.post(url, files=files)
            if r.status_code != 200:
                if r.status_code == 403:
                    return '\nIncorrect or Invalid API Key!'
                else:
                    return "\nstatus code: " + str(r.status_code)
            else:
                results = json.loads(r.text)
                if int(results['header']['user_id']) > 0:
                    print('Remaining Searches 30s|24h: ' + str(results['header']['short_remaining']) + '|' + str(
                        results['header']['long_remaining']))
                    break
                    '''
                    if int(results['header']['status']) == 0:
                        break
                    else:
                        if int(results['header']['status']) > 0:
                            return '\nAPI Error.\n'+str(results['header']['status'])
                        else:
                            return '\nBad image or other request error.'
                    '''
                else:
                    return '\nBad image, or API failure.'

        res = ''
        urls = []
        if self.processResults:
            if int(results['header']['results_returned']) > 0:
                print(results)
                for result in results['results']:
                    res = '\n相似度: ' + result['header']['similarity']
                    for key in result['data']:
                        if key == "member_name" or key == "creator":
                            res += '\n作者: ' + result['data'][key]
                        if (key == "source" or key == "ext_urls") and "http" in str(result['data'][key]):
                            if isinstance(result['data'][key], str):
                                urls.append(result['data'][key])
                            else:
                                for url in result['data'][key]:
                                    urls.append(url)
                    res += '\n链接: ' + '\n      - '.join(url for url in urls)
            else:
                res = '\n没有结果'

            if int(results['header']['long_remaining']) < 1:
                res += '\nOut of searches for today.'
            if int(results['header']['short_remaining']) < 1:
                res += '\nOut of searches for this 30 second period.'
            return res

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        if self.__check__(user, message):
            image = message.getFirstComponent(Image)
            result = self.SauceNAO(str(image).split("'")[5])
            message = [Plain(result)]
            yield message
