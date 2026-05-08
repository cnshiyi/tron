from rest_framework import serializers
from .models import Address, ChainTransaction

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class ChainTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChainTransaction
        fields = "__all__"

