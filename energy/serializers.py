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
