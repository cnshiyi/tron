from rest_framework import serializers
from .models import EnergyPlan, EnergyOrder, EnergyCommission

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

