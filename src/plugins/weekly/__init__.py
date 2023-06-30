# @Author: south
# @Date: 2023-06-23 10:40
import nonebot
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v12 import Message, Bot, GroupMessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_tortoise_orm import add_model

from .config import Config
from .models import *
from .models import select_users, update_weekly_subscription, select_weekly_subscription

global_config = get_driver().config
config = Config.parse_obj(global_config)

add_model("src.plugins.weekly.models")

weekly_on = on_command("weekly_on", priority=5, permission=SUPERUSER)


@weekly_on.handle()
async def weekly_on_receive(bot: Bot, event: GroupMessageEvent):
    res, error = await update_weekly_subscription(subscriber_id=event.group_id, status=True, bot_id=bot.self_id)
    print(res.status, error)
    if res:
        await weekly_on.finish(f"link started.")
    else:
        await weekly_on.finish(f"link failed.")


weekly_off = on_command("weekly_off", priority=5, permission=SUPERUSER)


@weekly_off.handle()
async def weekly_off_receive(bot: Bot, event: GroupMessageEvent):
    res, error = await update_weekly_subscription(subscriber_id=event.group_id, status=False, bot_id=bot.self_id)
    print(res.status, error)
    if res:
        await weekly_on.finish(f"unlink succeed.")
    else:
        await weekly_on.finish(f"unlink failed.")


weekly = on_command("weekly", priority=5)


@weekly.handle()
async def weekly_receive(event: GroupMessageEvent, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        user_id = event.user_id
        result, error = await insert_weekly(user_id=user_id, content=plain_text)
        if error:
            await weekly.send("收到" + MessageSegment.mention(user_id))
        else:
            await weekly.send("数据库爆炸了" + MessageSegment.mention(user_id))


@scheduler.scheduled_job("cron", hour='9, 17', minute='30', id="weekly_push", max_instances=3, misfire_grace_time=600)
async def weekly_push():
    for bot_id in nonebot.get_bots():
        bot = nonebot.get_bots()[bot_id]
        result = await select_weekly_subscription(bot_id=bot_id)
        for subscription in result:
            users = await select_users()
            print(users)

            member_list = await bot.call_api("get_group_member_list", **{
                "group_id": subscription.subscriber_id
            })
            user_ids = [item['user_id'] for item in member_list]
            user_ids = set(user_ids)
            user_ids.remove(bot_id)

            print(user_ids)
            rest = len(user_ids - set(users))
            if rest > 0:
                await bot.call_api("send_message", **{
                    "detail_type": "group",
                    "message": f"交周报了，本周还有{rest}人没交。",
                    "group_id": subscription.subscriber_id
                })
