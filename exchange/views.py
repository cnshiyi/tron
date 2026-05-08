from rest_framework import viewsets
from .models import ExchangeBlacklist, ExchangeConfig, ExchangeOrder, ExchangeRecord
from .serializers import ExchangeBlacklistSerializer, ExchangeConfigSerializer, ExchangeOrderSerializer, ExchangeRecordSerializer

class ExchangeConfigViewSet(viewsets.ModelViewSet):
    queryset = ExchangeConfig.objects.all().order_by("-id")
    serializer_class = ExchangeConfigSerializer
    filterset_fields = ["bot_id", "auto_mode"]

class ExchangeOrderViewSet(viewsets.ModelViewSet):
    queryset = ExchangeOrder.objects.all().order_by("-id")
    serializer_class = ExchangeOrderSerializer
    filterset_fields = ["bot_id", "user_id", "type", "status"]
    search_fields = ["order_no", "address", "pay_txid", "payout_txid"]

class ExchangeBlacklistViewSet(viewsets.ModelViewSet):
    queryset = ExchangeBlacklist.objects.all().order_by("-id")
    serializer_class = ExchangeBlacklistSerializer
    search_fields = ["address", "reason"]

class ExchangeRecordViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRecord.objects.all().order_by("-id")
    serializer_class = ExchangeRecordSerializer
    filterset_fields = ["bot_id", "user_id", "from_token", "to_token", "status"]
    search_fields = ["order_no", "pay_txid", "payout_txid"]
