# http://api.fanyi.baidu.com/
# https://github.com/KutouAkira/python_Google_TK
import hashlib
import urllib
import random
import json
import http.client
import ctypes
import typing as T
from mirai import *
from controllers.reactor import reactor, plain_str, search_groups


class Translate(reactor):
    def __check__(self, user: T.Union[Group, Friend], message: MessageChain):
        msg = plain_str(message)

        if isinstance(user, Group):
            if self.group is not None and user.id not in self.group:
                return False
        elif isinstance(user, Friend):
            if self.friend is not None and user.id not in self.friend:
                return False

        for key in self.trigger:
            result = search_groups(key, ["$from_lang", "$to_lang", "$obj"], msg)
            if result is not None:
                return result
        return False

    # 百度翻译
    def BDtranslate(self, fromLang, toLang, q):
        trans = None
        myurl = '/api/trans/vip/translate'
        salt = random.randint(32768, 65536)
        sign = self.appid + q + str(salt) + self.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + self.appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

        try:
            trans = http.client.HTTPConnection('api.fanyi.baidu.com')
            trans.request('GET', myurl)
            response = trans.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            res = result['trans_result'][0]['dst']

        except Exception as e:
            res = e

        finally:
            if trans:
                trans.close()
        return res

    # 以下是计算Google翻译TK参数部分
    def int_overflow(self, val):
        maxint = 2147483647
        if not -maxint - 1 <= val <= maxint:
            val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        return val

    def unsigned_right_shitf(self, n, i):
        # 数字小于0，则转为32位无符号uint
        if n < 0:
            n = ctypes.c_uint32(n).value
        # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
        if i < 0:
            return -self.int_overflow(n << abs(i))
        return self.int_overflow(n >> i)

    def google_TL(self, src):
        a = src.strip()
        b = 406644
        b1 = 3293161072

        jd = "."
        美元b = "+-a^+6"
        Zb = "+-3^+b+-f"

        e = []
        for g in range(len(a)):
            m = ord(a[g])
            if 128 > m:
                e.append(m)
            else:
                if 2048 > m:
                    e.append(m >> 6 | 192)
                else:
                    if 55296 == (m & 64512) and g + 1 < len(a) and 56320 == (a[g + 1] & 64512):
                        g += 1
                        m = 65535 + ((m & 1024) << 10) + (a[g] & 1023)
                        e.append(m >> 18 | 240)
                        e.append(m >> 12 & 63 | 128)
                    else:
                        e.append(m >> 12 | 224)
                        e.append(m >> 6 & 63 | 128)
                    e.append(m & 63 | 128)
        a = b
        for f in range(len(e)):
            a += int(e[f])
            a = self.google_RL(a, 美元b)
        a = self.google_RL(a, Zb)
        if b1:
            a ^= b1
        else:
            a ^= 0
        if 0 > a:
            a = (a & 2147483647) + 2147483647
        a %= 1E6
        return str(int(a)) + jd + str(int(a) ^ b)

    def google_RL(self, a, b):
        t = 'a'
        Yb = '+'
        for c in range(0, len(b) - 2, 3):
            d = b[c + 2]
            if d >= t:
                d = ord(d[0]) - 87
            else:
                d = int(d)
            if b[c + 1] == Yb:
                d = self.unsigned_right_shitf(a, d)
            else:
                d = int(a) << d
            if b[c] == Yb:
                a = int(a) + d & 4294967295
            else:
                a = int(a) ^ d
        return a

    # ----------------------------------------------

    # Google翻译
    def googleTrans(self, fromLang, toLang, q):
        trans = None
        tk = self.google_TL(q)
        url = '/translate_a/single?client=t&sl=' + fromLang + '&tl=' + toLang + '&hl=' + toLang + '&dt=bd&dt=ex&dt=ld' \
                                                                                                  '&dt=md&dt=qc&dt=rw' \
                                                                                                  '&dt=rm&dt=ss&dt=t' \
                                                                                                  '&dt=at&ie=UTF-8&oe' \
                                                                                                  '=UTF-8&source=sel' \
                                                                                                  '&tk=' \
              + tk + '&q=' + urllib.parse.quote(q)
        try:
            trans = http.client.HTTPConnection('translate.google.cn')
            trans.request('GET', url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/81.0.4044.122 Safari/537.36'})
            response = trans.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            # print(result[0][-1][-1]) #原文读音
            # print(result[0][0][1]) #原文
            # print()
            # print(result[0][-1][-2]) #结果读音
            # print(result[0][0][0]) #结果
            # if result[7]:
            #    print(result[7][1]) #罗马音转平假
        except Exception as e:
            print(e)
        finally:
            if trans:
                trans.close()

        # 平假名、片假名、罗马音互转实验性功能
        # if fromLang == 'ja-Latn':
        #     if toLang == 'ja-Hrgn':
        #         return result[7][1]
        #     else:
        #         tk = self.google_TL(result[7][1])
        #         url = '/translate_a/single?client=t&sl=ja&tl=' + toLang + '&hl=' + toLang + '&dt=bd&dt=ex&dt=ld&dt=md' \
        #                                                                                     '&dt=qc&dt=rw&dt=rm&dt=ss' \
        #                                                                                     '&dt=t&dt=at&ie=UTF-8&oe' \
        #                                                                                     '=UTF-8&source=sel&tk=' \
        #               + tk + '&q=' + urllib.parse.quote(result[7][1])
        #         try:
        #             trans = http.client.HTTPConnection('translate.google.com')
        #             trans.request('GET', url)
        #             response = trans.getresponse()
        #             result_all = response.read().decode("utf-8")
        #             result = json.loads(result_all)
        #         except Exception as e:
        #             print(e)
        #         finally:
        #             if trans:
        #                 trans.close()
        #         if toLang == 'ja':
        #             return result[7][1]
        return result[0][0][0]

    google_dict = {"zh": "zh-CN", "jp": "ja", "en": "en"}

    async def generate_reply(self, bot: Mirai, source: Source, user: T.Union[Group, Friend], message: MessageChain,
                             member: Member):
        result = self.__check__(user, message)
        if result:
            fromLang, toLang, q = result
            baidu_res = self.BDtranslate(fromLang, toLang, q)
            google_res = self.googleTrans(self.google_dict[fromLang], self.google_dict[toLang], q)
            message = [
                Plain("度娘: " + baidu_res + "\n"),
                Plain("谷歌: " + google_res)
            ]
            yield message
