from rest_framework import viewsets
from .models import Balance, RechargeConfig, RunningWater, Withdrawal
from .serializers import BalanceSerializer, RechargeConfigSerializer, RunningWaterSerializer, WithdrawalSerializer

class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all().order_by("-id")
    serializer_class = BalanceSerializer
    filterset_fields = ["bot_id", "user_id"]
    search_fields = ["user_id"]

class RunningWaterViewSet(viewsets.ModelViewSet):
    queryset = RunningWater.objects.all().order_by("-id")
    serializer_class = RunningWaterSerializer
    filterset_fields = ["bot_id", "user_id", "business_type", "token_type"]
    search_fields = ["user_id", "ref_no"]

class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all().order_by("-id")
    serializer_class = WithdrawalSerializer
    filterset_fields = ["status", "token_type", "user_id"]
    search_fields = ["user_id", "address", "txid"]

class RechargeConfigViewSet(viewsets.ModelViewSet):
    queryset = RechargeConfig.objects.all().order_by("-id")
    serializer_class = RechargeConfigSerializer
    filterset_fields = ["bot_id", "token_type", "enabled"]
    search_fields = ["address", "remark"]
