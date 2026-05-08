from rest_framework import serializers
from .models import Balance, RunningWater, Withdrawal

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

