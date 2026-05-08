from django.db import models
from common.models import TimeStampedModel

class Balance(TimeStampedModel):
    user_id = models.CharField(max_length=128, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    usdt = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    integral = models.DecimalField(max_digits=30, decimal_places=8, default=0)

class RunningWater(TimeStampedModel):
    user_id = models.CharField(max_length=128)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    business_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    token_type = models.CharField(max_length=20, default="usdt")
    before_balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    after_balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    ref_no = models.CharField(max_length=128, blank=True, default="")

class Withdrawal(TimeStampedModel):
    STATUS_CHOICES = [("pending", "待审批"), ("approved", "已通过"), ("rejected", "已拒绝"), ("paid", "已打款")]
    user_id = models.CharField(max_length=128)
    address = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    token_type = models.CharField(max_length=20, default="usdt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    txid = models.CharField(max_length=128, blank=True, default="")
    reviewed_by = models.CharField(max_length=128, blank=True, default="")


class RechargeConfig(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    token_type = models.CharField(max_length=20, default="usdt")
    address = models.CharField(max_length=64, blank=True, default="")
    min_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    confirmations = models.PositiveIntegerField(default=1)
    enabled = models.BooleanField(default=True)
    remark = models.CharField(max_length=255, blank=True, default="")
