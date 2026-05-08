from rest_framework import serializers
from .models import Balance, RechargeConfig, RunningWater, Withdrawal

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = "__all__"

class RunningWaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunningWater
        fields = "__all__"

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"

class RechargeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeConfig
        fields = "__all__"
