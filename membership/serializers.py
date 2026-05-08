from rest_framework import serializers
from .models import MemberActivity, MemberCommission, MemberGoods, MemberOrder, MemberRecharge

class MemberGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberGoods
        fields = "__all__"

class MemberOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberOrder
        fields = "__all__"

class MemberRechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberRecharge
        fields = "__all__"

class MemberActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberActivity
        fields = "__all__"

class MemberCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberCommission
        fields = "__all__"


class MemberTxidSerializer(serializers.Serializer):
    txid = serializers.CharField(required=False, allow_blank=True, default="")

class MemberCommissionSettleSerializer(serializers.Serializer):
    reviewed_by = serializers.CharField(required=False, allow_blank=True, default="admin")
