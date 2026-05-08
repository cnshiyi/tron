from django.db import models
from common.models import TimeStampedModel

class MemberGoods(TimeStampedModel):
    name = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(default=30)
    sell_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    min_limit = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    max_limit = models.DecimalField(max_digits=20, decimal_places=8, default=0)

class MemberOrder(TimeStampedModel):
    STATUS_CHOICES = [("pending", "待支付"), ("paid", "已支付"), ("activated", "已开通"), ("cancelled", "已取消")]
    order_no = models.CharField(max_length=64, unique=True)
    user_id = models.CharField(max_length=128)
    target_user_id = models.CharField(max_length=128, blank=True, default="")
    goods = models.ForeignKey(MemberGoods, on_delete=models.PROTECT)
    pay_type = models.CharField(max_length=20, default="usdt")
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    txid = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

class MemberRecharge(TimeStampedModel):
    order_no = models.CharField(max_length=64, unique=True)
    user_id = models.CharField(max_length=128)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    token_type = models.CharField(max_length=20, default="usdt")
    txid = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, default="pending")

class MemberActivity(TimeStampedModel):
    title = models.CharField(max_length=128)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    activity_type = models.CharField(max_length=50, default="recharge")
    reward_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    reward_token = models.CharField(max_length=20, default="usdt")
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    rule = models.TextField(blank=True, default="")

class MemberCommission(TimeStampedModel):
    user_id = models.CharField(max_length=128)
    inviter_id = models.CharField(max_length=128, blank=True, default="")
    bot_id = models.CharField(max_length=128, blank=True, default="")
    source_order_no = models.CharField(max_length=64, blank=True, default="")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    token_type = models.CharField(max_length=20, default="usdt")
    status = models.CharField(max_length=20, default="pending")
