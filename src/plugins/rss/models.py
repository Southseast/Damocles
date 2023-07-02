# @Author: south
# @Date: 2023-06-23 10:40

from tortoise import fields, Model


class RSS_Subscription(Model):
    id = fields.BigIntField(pk=True)
    subscriber_id = fields.CharField(32, description="订阅者ID")
    bot_id = fields.CharField(32, description="BOT ID")
    status = fields.BooleanField(description="启用状态")

    class Meta:
        table = "damocles_rss_subscription"
        table_description = "RSS订阅记录"


async def update_rss_subscription(subscriber_id, bot_id, status):
    result, error = await RSS_Subscription.update_or_create(
        defaults={
            "status": status,
        },
        subscriber_id=subscriber_id,
        bot_id=bot_id,
    )
    return result, error


async def select_rss_subscription(bot_id):
    result = await RSS_Subscription.filter(
        bot_id=bot_id,
        status=True,
    )
    return result
