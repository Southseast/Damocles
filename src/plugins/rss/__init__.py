# @Author: south
# @Date: 2023-06-23 10:40
from datetime import datetime, timedelta

import feedparser
import nonebot
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v12 import Bot, GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_tortoise_orm import add_model

from .config import Config
from .models import *
from .models import update_rss_subscription, select_rss_subscription

global_config = get_driver().config
config = Config.parse_obj(global_config)

add_model("src.plugins.rss.models")

rss_on = on_command("rss_on", priority=5, permission=SUPERUSER)


@rss_on.handle()
async def rss_on_receive(bot: Bot, event: GroupMessageEvent):
    res, error = await update_rss_subscription(subscriber_id=event.group_id, status=True, bot_id=bot.self_id)
    print(res.status, error)
    if res:
        await rss_on.finish(f"rss link started.")
    else:
        await rss_on.finish(f"rss link failed.")


rss_off = on_command("rss_off", priority=5, permission=SUPERUSER)


@rss_off.handle()
async def rss_off_receive(bot: Bot, event: GroupMessageEvent):
    res, error = await update_rss_subscription(subscriber_id=event.group_id, status=False, bot_id=bot.self_id)
    print(res.status, error)
    if res:
        await rss_on.finish(f"rss unlink succeed.")
    else:
        await rss_on.finish(f"rss unlink failed.")


@scheduler.scheduled_job("cron", hour='9', minute='00', id="rss_push", max_instances=3, misfire_grace_time=600)
async def rss_push():
    for bot_id in nonebot.get_bots():
        bot = nonebot.get_bots()[bot_id]
        result = await select_rss_subscription(bot_id=bot_id)

        for subscription in result:
            res = ""
            # xz rss
            newsfeed = feedparser.parse("https://xz.aliyun.com/feed")

            for i in newsfeed.entries:
                published_time = datetime.fromisoformat(i["published"])
                now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0).astimezone()
                end_of_day = now - timedelta(days=1)

                # 判断published是否在当前日期的范围内
                if end_of_day < published_time < now:
                    res += f"{i['title']} {i['link']} \n"

            if len(res) > 0:
                await bot.call_api("send_message", **{
                    "detail_type": "group",
                    "message": res,
                    "group_id": subscription.subscriber_id
                })
