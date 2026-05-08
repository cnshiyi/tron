from django.db import models
from common.models import TimeStampedModel

class Address(TimeStampedModel):
    TYPE_CHOICES = [("exchange", "兑换"), ("energy", "能量"), ("member", "会员"), ("listen", "监听")]
    address = models.CharField(max_length=64, unique=True, verbose_name="TRON地址")
    private_key_encrypted = models.TextField(blank=True, default="", verbose_name="加密私钥")
    address_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="exchange")
    user_id = models.CharField(max_length=128, blank=True, default="", verbose_name="Telegram用户ID")
    username = models.CharField(max_length=128, blank=True, default="", verbose_name="用户名")
    bot_id = models.CharField(max_length=128, blank=True, default="", verbose_name="机器人ID")
    allocated = models.BooleanField(default=False, verbose_name="已分配")

    def __str__(self):
        return self.address

class ChainTransaction(TimeStampedModel):
    TYPE_CHOICES = [("trx", "TRX"), ("usdt", "USDT"), ("energy", "能量")]
    txid = models.CharField(max_length=128, unique=True, verbose_name="交易Hash")
    from_address = models.CharField(max_length=64, blank=True, default="")
    to_address = models.CharField(max_length=64, blank=True, default="")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    token_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="usdt")
    confirmed = models.BooleanField(default=False)
    raw = models.JSONField(default=dict, blank=True)

class ListenAddress(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    address = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=128, blank=True, default="")
    token_type = models.CharField(max_length=20, default="usdt")
    min_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    enabled = models.BooleanField(default=True)
    last_scanned_txid = models.CharField(max_length=128, blank=True, default="")
