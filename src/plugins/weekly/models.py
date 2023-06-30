# @Author: south
# @Date: 2023-06-23 10:40
from datetime import datetime, timedelta

from tortoise import fields, Model
from tortoise.expressions import Q


class Weekly(Model):
    id = fields.BigIntField(pk=True)
    user_id = fields.CharField(32, description="用户ID")
    content = fields.TextField(description="内容")
    create_time = fields.DatetimeField(description="时间")

    class Meta:
        table = "damocles_weekly"
        table_description = "周报记录"


async def select_users():
    # 获取当前日期和时间
    now = datetime.now()
    # 计算本周的星期一
    monday = now - timedelta(days=now.weekday())
    # 将时间设置为 0 点
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    # 计算本周的星期日
    sunday = monday + timedelta(days=7, hours=0, minutes=0, seconds=0)
    result = await Weekly.filter(Q(create_time__gte=monday)).filter(
        Q(create_time__lte=sunday)).all().only("user_id").distinct().values_list("user_id")
    return [x[0] for x in result] if result else []


async def insert_weekly(user_id: str, content: str):
    result, error = await Weekly.get_or_create(
        user_id=user_id,
        content=content,
        create_time=int(datetime.now().timestamp())
    )
    return result, error


class Weekly_Subscription(Model):
    id = fields.BigIntField(pk=True)
    subscriber_id = fields.CharField(32, description="订阅者ID")
    bot_id = fields.CharField(32, description="BOT ID")
    status = fields.BooleanField(description="启用状态")

    class Meta:
        table = "damocles_weekly_subscription"
        table_description = "周报订阅记录"


async def update_weekly_subscription(subscriber_id, bot_id, status):
    result, error = await Weekly_Subscription.update_or_create(
        defaults={
            "status": status,
        },
        subscriber_id=subscriber_id,
        bot_id=bot_id,
    )
    return result, error


async def select_weekly_subscription(bot_id):
    result = await Weekly_Subscription.filter(
        bot_id=bot_id,
        status=True,
    )
    return result
