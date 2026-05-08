from rest_framework import serializers
from .models import Address, ChainTransaction, ListenAddress

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class ChainTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChainTransaction
        fields = "__all__"

class ListenAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListenAddress
        fields = "__all__"


class ListenAddressScanSerializer(serializers.Serializer):
    apply = serializers.BooleanField(required=False, default=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=200, default=20)
