from rest_framework import viewsets
from .models import MemberActivity, MemberCommission, MemberGoods, MemberOrder, MemberRecharge
from .serializers import (
    MemberActivitySerializer,
    MemberCommissionSerializer,
    MemberGoodsSerializer,
    MemberOrderSerializer,
    MemberRechargeSerializer,
)

class MemberGoodsViewSet(viewsets.ModelViewSet):
    queryset = MemberGoods.objects.all()
    serializer_class = MemberGoodsSerializer
    search_fields = ["name"]

class MemberOrderViewSet(viewsets.ModelViewSet):
    queryset = MemberOrder.objects.all()
    serializer_class = MemberOrderSerializer
    filterset_fields = ["user_id", "target_user_id", "status", "pay_type"]
    search_fields = ["order_no", "txid"]

class MemberRechargeViewSet(viewsets.ModelViewSet):
    queryset = MemberRecharge.objects.all()
    serializer_class = MemberRechargeSerializer
    filterset_fields = ["bot_id", "user_id", "status", "token_type"]
    search_fields = ["order_no", "txid"]

class MemberActivityViewSet(viewsets.ModelViewSet):
    queryset = MemberActivity.objects.all()
    serializer_class = MemberActivitySerializer
    filterset_fields = ["bot_id", "activity_type", "enabled"]
    search_fields = ["title", "rule"]

class MemberCommissionViewSet(viewsets.ModelViewSet):
    queryset = MemberCommission.objects.all()
    serializer_class = MemberCommissionSerializer
    filterset_fields = ["bot_id", "user_id", "inviter_id", "status", "token_type"]
    search_fields = ["source_order_no"]
