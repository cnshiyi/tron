from rest_framework import viewsets
from .models import MemberGoods, MemberOrder
from .serializers import MemberGoodsSerializer, MemberOrderSerializer

class MemberGoodsViewSet(viewsets.ModelViewSet):
    queryset = MemberGoods.objects.all()
    serializer_class = MemberGoodsSerializer
    search_fields = ["name"]

class MemberOrderViewSet(viewsets.ModelViewSet):
    queryset = MemberOrder.objects.all()
    serializer_class = MemberOrderSerializer
    filterset_fields = ["user_id", "target_user_id", "status", "pay_type"]
    search_fields = ["order_no", "txid"]
