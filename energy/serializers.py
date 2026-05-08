from rest_framework import serializers
from .models import (
    AdvanceRecord,
    EnergyAddressConfig,
    EnergyAgentRecord,
    EnergyCommission,
    EnergyOrder,
    EnergyPlan,
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
