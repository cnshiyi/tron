from rest_framework import serializers
from .models import ExchangeConfig, ExchangeOrder, ExchangeBlacklist

class ExchangeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeConfig
        fields = "__all__"

class ExchangeOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeOrder
        fields = "__all__"

class ExchangeBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeBlacklist
        fields = "__all__"

