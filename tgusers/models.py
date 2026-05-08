from django.db import models
from common.models import TimeStampedModel

class TgUser(TimeStampedModel):
    user_id = models.CharField(max_length=128, unique=True, verbose_name="Telegram用户ID")
    bot_id = models.CharField(max_length=128, blank=True, default="", verbose_name="机器人ID")
    username = models.CharField(max_length=128, blank=True, default="", verbose_name="用户名")
    first_name = models.CharField(max_length=128, blank=True, default="", verbose_name="昵称")
    inviter_id = models.CharField(max_length=128, blank=True, default="", verbose_name="邀请人ID")
    member_level = models.CharField(max_length=64, blank=True, default="", verbose_name="会员等级")
    member_expire_at = models.DateTimeField(null=True, blank=True, verbose_name="会员到期时间")
    is_blacklisted = models.BooleanField(default=False, verbose_name="拉黑")
    is_top = models.BooleanField(default=False, verbose_name="置顶")
    total_recharge = models.DecimalField(max_digits=30, decimal_places=8, default=0, verbose_name="累计充值")
    total_consumption = models.DecimalField(max_digits=30, decimal_places=8, default=0, verbose_name="累计消费")

    def __str__(self):
        return f"{self.user_id} {self.username}".strip()

class UserTop(TimeStampedModel):
    user_id = models.CharField(max_length=128, verbose_name="用户ID")
    bot_id = models.CharField(max_length=128, blank=True, default="", verbose_name="机器人ID")
    rank_type = models.CharField(max_length=50, default="recharge", verbose_name="排行类型")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0, verbose_name="金额")
    rank = models.PositiveIntegerField(default=0, verbose_name="排名")
    snapshot_date = models.DateField(null=True, blank=True, verbose_name="快照日期")

    class Meta:
        indexes = [models.Index(fields=["bot_id", "rank_type", "rank"])]
