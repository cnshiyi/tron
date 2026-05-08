from django.db import models
from common.models import TimeStampedModel

class EnergyPlan(TimeStampedModel):
    MODE_CHOICES = [("hourly", "能量闪租"), ("duration", "时长套餐"), ("times", "笔数套餐"), ("smart", "智能托管")]
    bot_id = models.CharField(max_length=128, blank=True, default="")
    name = models.CharField(max_length=100)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    energy_amount = models.PositiveIntegerField(default=32000)
    duration_hours = models.PositiveIntegerField(default=1)
    number_of_times = models.PositiveIntegerField(default=0)
    price_trx = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    price_usdt = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    sort = models.IntegerField(default=0)

class EnergyOrder(TimeStampedModel):
    STATUS_CHOICES = [("pending", "待支付"), ("paid", "已支付"), ("delegating", "委托中"), ("success", "成功"), ("failed", "失败"), ("expired", "已过期")]
    order_no = models.CharField(max_length=64, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    receiver_address = models.CharField(max_length=64)
    plan = models.ForeignKey(EnergyPlan, null=True, blank=True, on_delete=models.SET_NULL)
    energy_amount = models.PositiveIntegerField(default=0)
    trx_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    usdt_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    pay_type = models.CharField(max_length=20, default="balance")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    pay_txid = models.CharField(max_length=128, blank=True, default="")
    energy_txid = models.CharField(max_length=128, blank=True, default="")
    platform_order_id = models.CharField(max_length=128, blank=True, default="")
    callback_payload = models.JSONField(default=dict, blank=True)

class EnergyCommission(TimeStampedModel):
    order = models.ForeignKey(EnergyOrder, on_delete=models.CASCADE, related_name="commissions")
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    profit_usdt = models.DecimalField(max_digits=30, decimal_places=8, default=0)

class EnergyAgentRecord(TimeStampedModel):
    order_no = models.CharField(max_length=64, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    agent_user_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    receiver_address = models.CharField(max_length=64, blank=True, default="")
    energy_amount = models.PositiveIntegerField(default=0)
    cost_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    profit_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    status = models.CharField(max_length=20, default="pending")
    txid = models.CharField(max_length=128, blank=True, default="")

class AdvanceRecord(TimeStampedModel):
    user_id = models.CharField(max_length=128)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    token_type = models.CharField(max_length=20, default="trx")
    status = models.CharField(max_length=20, default="pending")
    reason = models.TextField(blank=True, default="")
    reviewed_by = models.CharField(max_length=128, blank=True, default="")

class EnergyAddressConfig(TimeStampedModel):
    MODE_CHOICES = [("pen", "笔数地址"), ("smart", "智能托管地址"), ("hourly", "闪租地址")]
    bot_id = models.CharField(max_length=128, blank=True, default="")
    address = models.CharField(max_length=64)
    private_key_encrypted = models.TextField(blank=True, default="")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="pen")
    max_energy = models.PositiveIntegerField(default=0)
    used_energy = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
