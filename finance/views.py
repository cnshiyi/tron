from rest_framework import viewsets
from .models import Balance, Withdrawal, RunningWater
from .serializers import BalanceSerializer, WithdrawalSerializer, RunningWaterSerializer

class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    filterset_fields = ["user_id", "bot_id"]

class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    filterset_fields = ["user_id", "status", "token_type"]
    search_fields = ["address", "txid"]

class RunningWaterViewSet(viewsets.ModelViewSet):
    queryset = RunningWater.objects.all()
    serializer_class = RunningWaterSerializer
    filterset_fields = ["user_id", "bot_id", "business_type", "token_type"]
    search_fields = ["ref_no"]
