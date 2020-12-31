import asyncio

from graia.application import GraiaMiraiApplication, Session
from graia.application.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.broadcast import Broadcast

from handler import *
from handler.handler_manager import HandlerManager
from my_logger import MyLogger
from utils import settings, start_reply_queue, stop_reply_queue

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
bot = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=f"""http://{settings["mirai"]["host"]}:{settings["mirai"]["port"]}""",  # 填入 httpapi 服务运行的地址
        authKey=settings["mirai"]["auth_key"],  # 填入 authKey
        account=int(settings["mirai"]["qq"]),  # 你的机器人的 qq 号
        # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        websocket=settings["mirai"]["enable_websocket"]
    ),
    logger=MyLogger()
)

manager = HandlerManager(bcc)
manager.register(
    Help(tag="help", settings=settings["help"]),
    allow_friend=settings["help"]["friend"] if settings['help']['enable'] else [],
    allow_group=settings["help"]["group"] if settings['help']['enable'] else [],
    ban_member=settings["help"]["ban"] if settings['help']['enable'] else []
)
manager.register(
    ISML(tag="isml", settings=settings["isml"]),
    allow_friend=settings["isml"]["friend"] if settings['isml']['enable'] else [],
    allow_group=settings["isml"]["group"] if settings['isml']['enable'] else [],
    ban_member=settings["isml"]["ban"] if settings['isml']['enable'] else []
)
manager.register(
    HHSH(tag="hhsh", settings=settings["hhsh"]),
    allow_friend=settings["hhsh"]["friend"] if settings['hhsh']['enable'] else [],
    allow_group=settings["hhsh"]["group"] if settings['hhsh']['enable'] else [],
    ban_member=settings["hhsh"]["ban"] if settings['hhsh']['enable'] else []
)
manager.register(
    Birthday(tag="birthday", settings=settings["birthday"]),
    allow_friend=settings["birthday"]["friend"] if settings['birthday']['enable'] else [],
    allow_group=settings["birthday"]["group"] if settings['birthday']['enable'] else [],
    ban_member=settings["birthday"]["ban"] if settings['birthday']['enable'] else []
)
manager.register(
    Bangumi(tag="bangumi", settings=settings["bangumi"]),
    allow_friend=settings["bangumi"]["friend"] if settings['bangumi']['enable'] else [],
    allow_group=settings["bangumi"]["group"] if settings['bangumi']['enable'] else [],
    ban_member=settings["bangumi"]["ban"] if settings['bangumi']['enable'] else []
)
manager.register(
    Translate(tag="translate", settings=settings["translate"]),
    allow_friend=settings["translate"]["friend"] if settings['translate']['enable'] else [],
    allow_group=settings["translate"]["group"] if settings['translate']['enable'] else [],
    ban_member=settings["translate"]["ban"] if settings['translate']['enable'] else []
)
manager.register(
    SauceNAO(tag="SauceNAO", settings=settings["SauceNAO"]),
    allow_friend=settings["SauceNAO"]["friend"] if settings['SauceNAO']['enable'] else [],
    allow_group=settings["SauceNAO"]["group"] if settings['SauceNAO']['enable'] else [],
    ban_member=settings["SauceNAO"]["ban"] if settings['SauceNAO']['enable'] else []
)
manager.register(
    BangDream(tag="bang_dream", settings=settings["bang_dream"]),
    allow_friend=settings["bang_dream"]["friend"] if settings['bang_dream']['enable'] else [],
    allow_group=settings["bang_dream"]["group"] if settings['bang_dream']['enable'] else [],
    ban_member=settings["bang_dream"]["ban"] if settings['bang_dream']['enable'] else []
)
manager.register(
    Cars(tag="cars", settings=settings["cars"]),
    allow_friend=settings["cars"]["friend"] if settings['cars']['enable'] else [],
    allow_group=settings["cars"]["group"] if settings['cars']['enable'] else [],
    ban_member=settings["cars"]["ban"] if settings['cars']['enable'] else []
)

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
