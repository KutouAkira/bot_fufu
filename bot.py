import asyncio

from graia.application import GraiaMiraiApplication, Session
from graia.application.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.broadcast import Broadcast

from handler import *
from my_logger import MyLogger
from utils import settings, start_reply_queue, stop_reply_queue

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
bot = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=f"""https://{settings["mirai"]["host"]}:{settings["mirai"]["port"]}""",  # 填入 httpapi 服务运行的地址
        authKey=settings["mirai"]["auth_key"],  # 填入 authKey
        account=int(settings["mirai"]["qq"]),  # 你的机器人的 qq 号
        # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        websocket=settings["mirai"]["enable_websocket"]
    ),
    logger=MyLogger()
)

handlers = {
    "AntiEro": AntiEro(
        tag="AntiEro",
        settings=settings["AntiEro"],
        bcc=bcc
    ),
    "BangDream": BangDream(
        tag="BangDream",
        settings=settings["bang_dream"],
        bcc=bcc
    ),
    "Bangumi": Bangumi(
        tag="Bangumi",
        settings=settings["bangumi"],
        bcc=bcc
    ),
    "Birthday": Birthday(
        tag="Birthday",
        settings=settings["birthday"],
        bcc=bcc
    ),
    "Cars": Cars(
        tag="Cars",
        settings=settings["cars"],
        bcc=bcc
    ),
    "help": Help(
        tag="help",
        settings=settings["help"],
        bcc=bcc
    ),
    "HHSH": HHSH(
        tag="HHSH",
        settings=settings["hhsh"],
        bcc=bcc
    ),
    "ISML": ISML(
        tag="ISML",
        settings=settings["isml"],
        bcc=bcc
    ),
    "SauceNAO": SauceNAO(
        tag="SauceNAO",
        settings=settings["SauceNAO"],
        bcc=bcc
    ),
    "Translate": Translate(
        tag="Translate",
        settings=settings["translate"],
        bcc=bcc
    )
}


@bcc.receiver(ApplicationLaunched, priority=16)
async def prepare_bot():
    await start_reply_queue()


@bcc.receiver(ApplicationShutdowned, priority=16)
async def close_bot():
    await stop_reply_queue()


if __name__ == "__main__":
    try:
        bot.launch_blocking()
    except KeyboardInterrupt:
        pass
