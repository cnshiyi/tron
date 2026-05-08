from rest_framework import serializers
from .models import MemberGoods, MemberOrder

class MemberGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberGoods
        fields = "__all__"

class MemberOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberOrder
        fields = "__all__"

