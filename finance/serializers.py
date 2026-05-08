from rest_framework import serializers
from .models import Balance, RechargeConfig, RunningWater, Withdrawal

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = "__all__"

class BalanceAdjustSerializer(serializers.Serializer):
    token_type = serializers.ChoiceField(choices=[("trx", "TRX"), ("usdt", "USDT"), ("integral", "积分")])
    amount = serializers.DecimalField(max_digits=30, decimal_places=8)
    business_type = serializers.CharField(max_length=50, default="manual_adjust")
    ref_no = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")

class RunningWaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunningWater
        fields = "__all__"

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"

class WithdrawalReviewSerializer(serializers.Serializer):
    reviewed_by = serializers.CharField(max_length=128, required=False, allow_blank=True, default="admin")
    reason = serializers.CharField(required=False, allow_blank=True, default="")

class WithdrawalPaidSerializer(serializers.Serializer):
    txid = serializers.CharField(max_length=128)
    reviewed_by = serializers.CharField(max_length=128, required=False, allow_blank=True, default="admin")

class RechargeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeConfig
        fields = "__all__"
