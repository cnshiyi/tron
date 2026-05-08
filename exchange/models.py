from django.db import models
from common.models import TimeStampedModel

class ExchangeConfig(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    usdt_to_trx_rate = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    trx_to_usdt_rate = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    float_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name="上浮费率")
    max_limit = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    min_limit = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    auto_mode = models.BooleanField(default=True)

class ExchangeOrder(TimeStampedModel):
    TYPE_CHOICES = [("usdt_to_trx", "USDT兑换TRX"), ("trx_to_usdt", "TRX兑换USDT")]
    STATUS_CHOICES = [("pending", "待支付"), ("paid", "已支付"), ("sent", "已出款"), ("cancelled", "已取消"), ("failed", "失败")]
    order_no = models.CharField(max_length=64, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    address = models.CharField(max_length=64, blank=True, default="")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    return_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    pay_txid = models.CharField(max_length=128, blank=True, default="")
    payout_txid = models.CharField(max_length=128, blank=True, default="")
    profit_usdt = models.DecimalField(max_digits=30, decimal_places=8, default=0)

class ExchangeBlacklist(TimeStampedModel):
    address = models.CharField(max_length=64, unique=True)
    reason = models.CharField(max_length=255, blank=True, default="")


class ExchangeRecord(TimeStampedModel):
    order_no = models.CharField(max_length=64, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    from_token = models.CharField(max_length=20, default="usdt")
    to_token = models.CharField(max_length=20, default="trx")
    from_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    to_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    rate = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    fee = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    status = models.CharField(max_length=20, default="pending")
    pay_txid = models.CharField(max_length=128, blank=True, default="")
    payout_txid = models.CharField(max_length=128, blank=True, default="")
