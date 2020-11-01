# -*- coding: utf8 -*-
import re
import typing as T
from concurrent.futures.thread import ThreadPoolExecutor

__executor = ThreadPoolExecutor(max_workers=8)


def match_groups(pattern: str, placeholders: T.Sequence[str], text: str) -> T.Optional[T.Dict[str, str]]:
    """
    将字符串按照模板提取关键内容
    （譬如，pattern="来$number张$keyword图", flags=["$number", "$keyword"], text="来3张色图"，返回值=["3", "色"]）
    :param pattern: 模板串
    :param placeholders: 标志的占位串
    :param text: 匹配内容
    :return: 提取出的标志的列表。若某个标志搜寻失败，则对应值为None
    """

    pos = []
    for ph in placeholders:
        c = pattern.count(ph)
        if c != -1:
            pos.append((ph, pattern.find(ph)))
            pattern = pattern.replace(ph, "(.*?)")
            pattern += "$"
        elif c > 1:
            raise Exception(f"{c} {ph} were found in pattern.")
    pos.sort(key=lambda x: x[1])

    match_result = re.search(pattern, text)
    if match_result is None:
        return None
    else:
        ans = dict()
        for i, (ph, _) in enumerate(pos):
            ans[ph] = match_result.group(i + 1)
        return ans
