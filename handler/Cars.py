# https://github.com/Aloxaf/MirageTankGo
from PIL import Image as PImage
from PIL import ImageEnhance
from typing import Tuple
import numpy as np
import random
import yaml
import io
import requests
import string
import json
import os
import typing as T

from graia.application import MessageChain, GraiaMiraiApplication, Group, Friend
from graia.application.message.elements.internal import Plain, Image_LocalFile
from loguru import logger
from utils import match_groups

from .sender_filter_query_handler import SenderFilterQueryHandler


class Cars(SenderFilterQueryHandler):
    def __check__(self, message: MessageChain):
        content = message.asDisplay()
        if content == self.normal_trigger or content == self.r18_trigger:
            return content, None
        if content[:2] == self.normal_trigger or content[:2] == self.r18_trigger:
            for x in self.trigger:
                result = match_groups(x, ['$mode'], content)
                if result is None:
                    continue
                return content[:2], result['$mode']
        return False

    def fileListFunc(self, filePath):
        fileList = []
        ext = [".jpg", ".png", ".bmp", ".gif"]
        for top, dirs, nondirs in os.walk(filePath):
            for item in nondirs:
                if os.path.splitext(item)[1] in ext:
                    fileList.append(os.path.join(top, item))
        return fileList

    def choice_img(
            self,
            kind: str,
            return_mode: str,
            src: str
    ):
        '''
        图片种类 kind: normal | R18;
        返回形式 mode: info | Image;
        源 src: local | yml | lolicon
        '''
        if src == 'lolicon':
            url = 'https://api.lolicon.app/setu/?apikey=' + self.lolicon_apikey
            if kind == 'R18':
                url += '&r18=1'
            url += '&size1200=1'
            logger.info(f"Lolicon request: {url}")
            res = requests.get(url).text
            choice = json.loads(res)['data'][0]
        elif src == 'yml':
            imgs = yaml.load(open(self.yml_path, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)
            if kind == 'normal':
                choice = random.choice(imgs['normal'])
            elif kind == 'R18':
                choice = random.choice(imgs['R18'])
        else:
            normal_list = self.fileListFunc(self.local_dir)
            r18_list = self.fileListFunc(self.local_r18_dir)
            if kind == 'normal':
                choice = random.choice(normal_list)
            elif kind == 'R18':
                choice = random.choice(r18_list)

        if src == 'local':
            logger.info(f"From local: {choice}")
            if self.is_resize:
                img = self.resize(PImage.open(choice))  # resize 可选
            else:
                img = PImage.open(choice)
        else:
            data = io.BytesIO()
            if src == 'lolicon':
                url = choice['url']
            else:
                url = choice['cover']
            logger.info(f"From remote: {url}")
            if self.proxy:
                data.write(requests.get(url, proxies=self.proxy_dict).content)
            else:
                data.write(requests.get(url).content)
            img = PImage.open(data)

        if return_mode == 'info':
            file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
            img.save(file_name, format='PNG')
            res = [str(file_name)]
        elif return_mode == 'Image':
            res = [img]

        if src != 'local':
            res.append(choice['author'])
            res.append(choice['uid'])
            res.append('https://www.pixiv.net/artworks/' + str(choice['pid']))
        return res

    def resize(self, img):
        if img.size[0] > img.size[1]:
            return img.resize((self.max_length, int(img.size[1] * self.max_length / img.size[0])), PImage.ANTIALIAS)
        else:
            return img.resize((int(img.size[0] * self.max_length / img.size[1]), self.max_length), PImage.ANTIALIAS)

    def unisize_image(self, im1: PImage.Image, im2: PImage.Image, mode: str) -> Tuple[PImage.Image, PImage.Image]:
        """
        统一图像大小
        """
        _wimg = im1.convert(mode)
        _bimg = im2.convert(mode)

        wwidth, wheight = _wimg.size
        bwidth, bheight = _bimg.size

        width = max(wwidth, bwidth)
        height = max(wheight, bheight)

        wimg = PImage.new(mode, (width, height), 255)
        bimg = PImage.new(mode, (width, height), 0)

        wimg.paste(_wimg, ((width - wwidth) // 2, (height - wheight) // 2))
        bimg.paste(_bimg, ((width - bwidth) // 2, (height - bheight) // 2))

        return wimg, bimg

    # 感谢老司机
    # https://zhuanlan.zhihu.com/p/31164700
    def gray_car(
            self,
            bimg: PImage,
            wlight: float = 1.0,
            blight: float = 0.5,
            chess: bool = False,
    ) -> str:
        """
        发黑白车
        :param wimg: 白色背景下的图片路径
        :param bimg: 黑色背景下的图片路径
        :param wlight: wimg 的亮度
        :param blight: bimg 的亮度
        :param chess: 是否棋盘格化
        :return: 处理后的图像
        """
        wimg = PImage.open(self.cover)
        wimg, bimg = self.unisize_image(wimg, bimg, "L")
        wpix = np.array(wimg).astype("float64")
        bpix = np.array(bimg).astype("float64")

        # 棋盘格化
        # 规则: if (x + y) % 2 == 0 { wpix[x][y] = 255 } else { bpix[x][y] = 0 }
        if chess:
            wpix[::2, ::2] = 255.0
            bpix[1::2, 1::2] = 0.0

        wpix *= wlight
        bpix *= blight

        a = 1.0 - wpix / 255.0 + bpix / 255.0
        r = np.where(a != 0, bpix / a, 255.0)

        pixels = np.dstack((r, r, r, a * 255.0))

        pixels[pixels > 255] = 255

        file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
        PImage.fromarray(pixels.astype("uint8"), "RGBA").save(file_name, format='PNG')
        return file_name

    # https://zhuanlan.zhihu.com/p/32532733
    def color_car(
            self,
            bimg: PImage,
            wlight: float = 1.0,
            blight: float = 0.3,
            wcolor: float = 0.5,
            bcolor: float = 0.7,
            chess: bool = False,
    ) -> str:
        """
        发彩色车
        :param wimg: 白色背景下的图片
        :param bimg: 黑色背景下的图片
        :param wlight: wimg 的亮度
        :param blight: bimg 的亮度
        :param wcolor: wimg 的色彩保留比例
        :param bcolor: bimg 的色彩保留比例
        :param chess: 是否棋盘格化
        :return: 处理后的图像
        """
        wimg = PImage.open(self.cover)
        wimg = ImageEnhance.Brightness(wimg).enhance(wlight)
        bimg = ImageEnhance.Brightness(bimg).enhance(blight)
        wimg, bimg = self.unisize_image(wimg, bimg, "RGB")
        wpix = np.array(wimg).astype("float64")
        bpix = np.array(bimg).astype("float64")

        if chess:
            wpix[::2, ::2] = [255., 255., 255.]
            bpix[1::2, 1::2] = [0., 0., 0.]

        wpix /= 255.
        bpix /= 255.

        wgray = wpix[:, :, 0] * 0.334 + wpix[:, :, 1] * 0.333 + wpix[:, :, 2] * 0.333
        wpix *= wcolor
        wpix[:, :, 0] += wgray * (1. - wcolor)
        wpix[:, :, 1] += wgray * (1. - wcolor)
        wpix[:, :, 2] += wgray * (1. - wcolor)

        bgray = bpix[:, :, 0] * 0.334 + bpix[:, :, 1] * 0.333 + bpix[:, :, 2] * 0.333
        bpix *= bcolor
        bpix[:, :, 0] += bgray * (1. - bcolor)
        bpix[:, :, 1] += bgray * (1. - bcolor)
        bpix[:, :, 2] += bgray * (1. - bcolor)

        d = 1. - wpix + bpix

        d[:, :, 0] = d[:, :, 1] = d[:, :, 2] = d[:, :, 0] * 0.222 + d[:, :, 1] * 0.707 + d[:, :, 2] * 0.071

        p = np.where(d != 0, bpix / d * 255., 255.)
        a = d[:, :, 0] * 255.

        colors = np.zeros((p.shape[0], p.shape[1], 4))
        colors[:, :, :3] = p
        colors[:, :, -1] = a

        colors[colors > 255] = 255

        file_name = 'tmp/' + ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
        PImage.fromarray(colors.astype("uint8")).convert("RGBA").save(file_name, format='PNG')
        return file_name

    async def generate_reply(self, app: GraiaMiraiApplication,
                             subject: T.Union[Group, Friend],
                             message: MessageChain) -> T.AsyncGenerator[T.Union[str, MessageChain], None]:
        result = self.__check__(message)
        if result:
            car, mod = result
            src = self.source
            if car == self.normal_trigger:
                kind = "normal"
            elif car == self.r18_trigger and subject.id in self.allow_r18:
                kind = "R18"
            else:
                logger.info(f"{subject.id} 无{car}权限")
                return
            if mod is None:
                img = self.choice_img(kind, "info", src)

                if src == "local":
                    msg = MessageChain.create([Image_LocalFile(img[0])])
                else:
                    msg = MessageChain.create([
                        Image_LocalFile(img[0]),
                        Plain('\n作者: ' + img[1] + '(' + str(img[2]) + ')' + '\n' + img[3])
                    ])
            else:
                choice = self.choice_img(kind, "Image", src)
                if mod == self.gray_trigger:
                    img = self.gray_car(choice[0])
                elif mod == self.color_trigger:
                    img = self.color_car(choice[0])

                if src == "local":
                    msg = MessageChain.create([Image_LocalFile(img)])
                else:
                    msg = MessageChain.create([
                        Image_LocalFile(img),
                        Plain('\n作者: ' + choice[1] + '(' + str(choice[2]) + ')' + '\n' + choice[3])
                    ])
            yield msg
