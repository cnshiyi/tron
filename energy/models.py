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


class EnergyHourlyTime(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    name = models.CharField(max_length=100)
    hours = models.PositiveIntegerField(default=1)
    enabled = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

class EnergyHourlyTimePrice(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    time = models.ForeignKey(EnergyHourlyTime, null=True, blank=True, on_delete=models.SET_NULL)
    energy_amount = models.PositiveIntegerField(default=32000)
    price_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    price_usdt = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    enabled = models.BooleanField(default=True)

class EnergyPenPlan(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    name = models.CharField(max_length=100)
    number_of_times = models.PositiveIntegerField(default=1)
    energy_amount = models.PositiveIntegerField(default=32000)
    price_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    price_usdt = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    enabled = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

class NumberOfOrders(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    available_times = models.PositiveIntegerField(default=0)
    used_times = models.PositiveIntegerField(default=0)
    source_order_no = models.CharField(max_length=64, blank=True, default="")
    expire_at = models.DateTimeField(null=True, blank=True)

class EnergyPenFlashEntry(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    title = models.CharField(max_length=128)
    address = models.CharField(max_length=64, blank=True, default="")
    energy_amount = models.PositiveIntegerField(default=0)
    price_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    enabled = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

class EnergyIntelligentPlan(TimeStampedModel):
    bot_id = models.CharField(max_length=128, blank=True, default="")
    name = models.CharField(max_length=100)
    min_energy = models.PositiveIntegerField(default=0)
    max_energy = models.PositiveIntegerField(default=0)
    price_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    strategy = models.CharField(max_length=50, default="auto")
    enabled = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

class EnergyRecord(TimeStampedModel):
    order_no = models.CharField(max_length=64, unique=True)
    bot_id = models.CharField(max_length=128, blank=True, default="")
    user_id = models.CharField(max_length=128, blank=True, default="")
    receiver_address = models.CharField(max_length=64, blank=True, default="")
    mode = models.CharField(max_length=20, default="hourly")
    energy_amount = models.PositiveIntegerField(default=0)
    duration_hours = models.PositiveIntegerField(default=0)
    number_of_times = models.PositiveIntegerField(default=0)
    amount_trx = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    txid = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, default="pending")


class StakingAccount(TimeStampedModel):
    """TRON 原生质押账户，支持 active permission 多签调用。"""

    RESOURCE_CHOICES = [("ENERGY", "能量"), ("BANDWIDTH", "带宽")]
    name = models.CharField(max_length=100, blank=True, default="")
    bot_id = models.CharField(max_length=128, blank=True, default="")
    address = models.CharField(max_length=64, unique=True, verbose_name="质押地址")
    private_key_encrypted = models.TextField(blank=True, default="", verbose_name="主签私钥/密文")
    multisig_private_keys = models.TextField(blank=True, default="", verbose_name="多签私钥/密文，一行一个")
    permission_id = models.PositiveIntegerField(default=0, verbose_name="Active Permission ID，0 表示 owner/default")
    required_signature_count = models.PositiveIntegerField(default=1, verbose_name="本系统签名数量要求")
    resource = models.CharField(max_length=20, choices=RESOURCE_CHOICES, default="ENERGY")
    frozen_balance_sun = models.BigIntegerField(default=0, verbose_name="已质押 SUN")
    max_delegable_sun = models.BigIntegerField(default=0, verbose_name="最大可委托 SUN")
    delegated_balance_sun = models.BigIntegerField(default=0, verbose_name="已委托 SUN")
    max_energy = models.PositiveIntegerField(default=0, verbose_name="最大能量")
    used_energy = models.PositiveIntegerField(default=0, verbose_name="已用能量")
    min_reserve_energy = models.PositiveIntegerField(default=0, verbose_name="保留能量")
    auto_reclaim = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    last_sync_payload = models.JSONField(default=dict, blank=True)

    @property
    def available_balance_sun(self):
        return max(0, int(self.max_delegable_sun or self.frozen_balance_sun) - int(self.delegated_balance_sun or 0))

    @property
    def available_energy(self):
        return max(0, int(self.max_energy or 0) - int(self.used_energy or 0) - int(self.min_reserve_energy or 0))


class StakingOrder(TimeStampedModel):
    STATUS_CHOICES = [("pending", "待处理"), ("delegating", "委托中"), ("success", "已委托"), ("failed", "失败"), ("reclaiming", "回收中"), ("reclaimed", "已回收")]
    order_no = models.CharField(max_length=64, unique=True)
    energy_order = models.ForeignKey(EnergyOrder, null=True, blank=True, on_delete=models.SET_NULL, related_name="staking_orders")
    account = models.ForeignKey(StakingAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="staking_orders")
    receiver_address = models.CharField(max_length=64)
    resource = models.CharField(max_length=20, default="ENERGY")
    energy_amount = models.PositiveIntegerField(default=0)
    delegate_balance_sun = models.BigIntegerField(default=0)
    lock = models.BooleanField(default=False)
    lock_period = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    delegate_txid = models.CharField(max_length=128, blank=True, default="")
    undelegate_txid = models.CharField(max_length=128, blank=True, default="")
    expire_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")


class StakingTransaction(TimeStampedModel):
    OPERATION_CHOICES = [("stake", "质押"), ("unstake", "解押"), ("delegate", "委托"), ("undelegate", "回收")]
    account = models.ForeignKey(StakingAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    staking_order = models.ForeignKey(StakingOrder, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    resource = models.CharField(max_length=20, default="ENERGY")
    amount_sun = models.BigIntegerField(default=0)
    receiver_address = models.CharField(max_length=64, blank=True, default="")
    permission_id = models.PositiveIntegerField(default=0)
    signature_count = models.PositiveIntegerField(default=0)
    txid = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, default="built")
    broadcast_result = models.JSONField(default=dict, blank=True)
    raw_transaction = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
