from rest_framework import viewsets
from .models import ExchangeConfig, ExchangeOrder, ExchangeBlacklist
from .serializers import ExchangeConfigSerializer, ExchangeOrderSerializer, ExchangeBlacklistSerializer

class ExchangeConfigViewSet(viewsets.ModelViewSet):
    queryset = ExchangeConfig.objects.all()
    serializer_class = ExchangeConfigSerializer
    filterset_fields = ["bot_id", "auto_mode"]

class ExchangeOrderViewSet(viewsets.ModelViewSet):
    queryset = ExchangeOrder.objects.all()
    serializer_class = ExchangeOrderSerializer
    filterset_fields = ["bot_id", "user_id", "type", "status"]
    search_fields = ["order_no", "address", "pay_txid", "payout_txid"]

class ExchangeBlacklistViewSet(viewsets.ModelViewSet):
    queryset = ExchangeBlacklist.objects.all()
    serializer_class = ExchangeBlacklistSerializer
    search_fields = ["address", "reason"]
