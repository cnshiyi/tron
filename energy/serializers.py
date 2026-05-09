from rest_framework import serializers
from .models import (
    AdvanceRecord,
    EnergyAddressConfig,
    EnergyAgentRecord,
    EnergyCommission,
    EnergyHourlyTime,
    EnergyHourlyTimePrice,
    EnergyIntelligentPlan,
    EnergyOrder,
    EnergyPenFlashEntry,
    EnergyPenPlan,
    EnergyPlan,
    EnergyRecord,
    NumberOfOrders,
    StakingAccount,
    StakingOrder,
    StakingTransaction,
)

class EnergyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPlan
        fields = "__all__"

class EnergyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyOrder
        fields = "__all__"

class EnergyCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyCommission
        fields = "__all__"

class EnergyAgentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyAgentRecord
        fields = "__all__"

class AdvanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceRecord
        fields = "__all__"

class EnergyAddressConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyAddressConfig
        fields = "__all__"

class EnergyHourlyTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyHourlyTime
        fields = "__all__"

class EnergyHourlyTimePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyHourlyTimePrice
        fields = "__all__"

class EnergyPenPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPenPlan
        fields = "__all__"

class NumberOfOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberOfOrders
        fields = "__all__"

class EnergyPenFlashEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPenFlashEntry
        fields = "__all__"

class EnergyIntelligentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyIntelligentPlan
        fields = "__all__"

class EnergyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyRecord
        fields = "__all__"


class EnergyDelegateSerializer(serializers.Serializer):
    dry_run = serializers.BooleanField(required=False, default=True)
    mode = serializers.ChoiceField(choices=["smart", "times"], required=False, default="smart")


class StakingAccountSerializer(serializers.ModelSerializer):
    available_balance_sun = serializers.IntegerField(read_only=True)
    available_energy = serializers.IntegerField(read_only=True)

    class Meta:
        model = StakingAccount
        fields = "__all__"


class StakingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakingOrder
        fields = "__all__"


class StakingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakingTransaction
        fields = "__all__"


class StakingStakeSerializer(serializers.Serializer):
    amount_sun = serializers.IntegerField(min_value=1)
    broadcast = serializers.BooleanField(required=False, default=False)


class StakingDelegateOrderSerializer(serializers.Serializer):
    broadcast = serializers.BooleanField(required=False, default=False)
    lock = serializers.BooleanField(required=False, default=False)
    lock_period = serializers.IntegerField(required=False, min_value=0, allow_null=True)


class StakingReclaimDueSerializer(serializers.Serializer):
    broadcast = serializers.BooleanField(required=False, default=False)
    limit = serializers.IntegerField(required=False, default=100, min_value=1, max_value=500)
