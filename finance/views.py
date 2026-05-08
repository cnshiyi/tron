from decimal import Decimal
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Balance, RechargeConfig, RunningWater, Withdrawal
from .serializers import (
    BalanceAdjustSerializer,
    BalanceSerializer,
    RechargeConfigSerializer,
    RunningWaterSerializer,
    WithdrawalPaidSerializer,
    WithdrawalReviewSerializer,
    WithdrawalSerializer,
)

class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all().order_by("-id")
    serializer_class = BalanceSerializer
    filterset_fields = ["bot_id", "user_id"]
    search_fields = ["user_id"]

    @action(detail=True, methods=["post"], url_path="adjust")
    @transaction.atomic
    def adjust(self, request, pk=None):
        balance = self.get_object()
        serializer = BalanceAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token_type = data["token_type"]
        amount = data["amount"]
        before = getattr(balance, token_type)
        after = before + amount
        if after < Decimal("0"):
            return Response({"detail": "余额不能小于0"}, status=status.HTTP_400_BAD_REQUEST)
        setattr(balance, token_type, after)
        balance.save(update_fields=[token_type, "updated_at"])
        RunningWater.objects.create(
            user_id=balance.user_id,
            bot_id=balance.bot_id,
            business_type=data["business_type"],
            amount=amount,
            token_type=token_type,
            before_balance=before,
            after_balance=after,
            ref_no=data.get("ref_no", ""),
        )
        return Response(self.get_serializer(balance).data)

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

    def _set_status(self, status_value: str, reviewed_by: str = "admin", txid: str = ""):
        withdrawal = self.get_object()
        withdrawal.status = status_value
        withdrawal.reviewed_by = reviewed_by or withdrawal.reviewed_by or "admin"
        if txid:
            withdrawal.txid = txid
        withdrawal.save(update_fields=["status", "reviewed_by", "txid", "updated_at"])
        return Response(self.get_serializer(withdrawal).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = WithdrawalReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._set_status("approved", serializer.validated_data.get("reviewed_by", "admin"))

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        serializer = WithdrawalReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._set_status("rejected", serializer.validated_data.get("reviewed_by", "admin"))

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        serializer = WithdrawalPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._set_status("paid", serializer.validated_data.get("reviewed_by", "admin"), serializer.validated_data["txid"])

class RechargeConfigViewSet(viewsets.ModelViewSet):
    queryset = RechargeConfig.objects.all().order_by("-id")
    serializer_class = RechargeConfigSerializer
    filterset_fields = ["bot_id", "token_type", "enabled"]
    search_fields = ["address", "remark"]
