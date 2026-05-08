from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from finance.models import Balance, RunningWater
from tgusers.models import TgUser
from .models import MemberActivity, MemberCommission, MemberGoods, MemberOrder, MemberRecharge
from .serializers import (
    MemberActivitySerializer,
    MemberCommissionSerializer,
    MemberCommissionSettleSerializer,
    MemberGoodsSerializer,
    MemberOrderSerializer,
    MemberRechargeSerializer,
    MemberTxidSerializer,
)


class MemberGoodsViewSet(viewsets.ModelViewSet):
    queryset = MemberGoods.objects.all().order_by("id")
    serializer_class = MemberGoodsSerializer
    search_fields = ["name"]


class MemberOrderViewSet(viewsets.ModelViewSet):
    queryset = MemberOrder.objects.select_related("goods").all().order_by("-id")
    serializer_class = MemberOrderSerializer
    filterset_fields = ["user_id", "target_user_id", "status", "pay_type"]
    search_fields = ["order_no", "txid"]

    def _set_status(self, status_value: str, txid: str = ""):
        order = self.get_object()
        order.status = status_value
        if txid:
            order.txid = txid
        order.save(update_fields=["status", "txid", "updated_at"])
        return order

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        serializer = MemberTxidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self._set_status("paid", serializer.validated_data.get("txid", ""))
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self._set_status("cancelled")
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="activate")
    @transaction.atomic
    def activate(self, request, pk=None):
        order = self.get_object()
        target_user_id = order.target_user_id or order.user_id
        user, _ = TgUser.objects.get_or_create(user_id=target_user_id, defaults={"bot_id": "", "inviter_id": ""})
        now = timezone.now()
        base = user.member_expire_at if user.member_expire_at and user.member_expire_at > now else now
        user.member_level = order.goods.name
        user.member_expire_at = base + timezone.timedelta(days=order.goods.duration_days)
        user.total_consumption = (user.total_consumption or Decimal("0")) + order.amount
        user.save(update_fields=["member_level", "member_expire_at", "total_consumption", "updated_at"])
        order.status = "activated"
        order.save(update_fields=["status", "updated_at"])

        inviter_id = user.inviter_id
        commission = None
        if inviter_id and inviter_id != user.user_id:
            commission_amount = (order.amount * Decimal("0.10")).quantize(Decimal("0.00000001"))
            commission, _ = MemberCommission.objects.update_or_create(
                source_order_no=order.order_no,
                inviter_id=inviter_id,
                defaults={
                    "user_id": user.user_id,
                    "bot_id": user.bot_id,
                    "amount": commission_amount,
                    "token_type": order.pay_type or "usdt",
                    "status": "pending",
                },
            )
        return Response({"order": self.get_serializer(order).data, "user_id": user.user_id, "member_expire_at": user.member_expire_at, "commission_id": getattr(commission, "id", None)})


class MemberRechargeViewSet(viewsets.ModelViewSet):
    queryset = MemberRecharge.objects.all().order_by("-id")
    serializer_class = MemberRechargeSerializer
    filterset_fields = ["bot_id", "user_id", "status", "token_type"]
    search_fields = ["order_no", "txid"]

    @action(detail=True, methods=["post"], url_path="mark-paid")
    @transaction.atomic
    def mark_paid(self, request, pk=None):
        serializer = MemberTxidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recharge = self.get_object()
        if serializer.validated_data.get("txid"):
            recharge.txid = serializer.validated_data["txid"]
        recharge.status = "paid"
        recharge.save(update_fields=["status", "txid", "updated_at"])

        balance, _ = Balance.objects.get_or_create(user_id=recharge.user_id, defaults={"bot_id": recharge.bot_id})
        field = recharge.token_type if recharge.token_type in {"trx", "usdt", "integral"} else "usdt"
        before = getattr(balance, field)
        after = before + recharge.amount
        setattr(balance, field, after)
        if recharge.bot_id and not balance.bot_id:
            balance.bot_id = recharge.bot_id
        balance.save(update_fields=[field, "bot_id", "updated_at"])
        RunningWater.objects.create(
            user_id=recharge.user_id,
            bot_id=recharge.bot_id,
            business_type="member_recharge",
            amount=recharge.amount,
            token_type=field,
            before_balance=before,
            after_balance=after,
            ref_no=recharge.order_no,
        )
        return Response(self.get_serializer(recharge).data)


class MemberActivityViewSet(viewsets.ModelViewSet):
    queryset = MemberActivity.objects.all().order_by("-id")
    serializer_class = MemberActivitySerializer
    filterset_fields = ["bot_id", "activity_type", "enabled"]
    search_fields = ["title", "rule"]


class MemberCommissionViewSet(viewsets.ModelViewSet):
    queryset = MemberCommission.objects.all().order_by("-id")
    serializer_class = MemberCommissionSerializer
    filterset_fields = ["bot_id", "user_id", "inviter_id", "status", "token_type"]
    search_fields = ["source_order_no"]

    @action(detail=True, methods=["post"], url_path="settle")
    @transaction.atomic
    def settle(self, request, pk=None):
        serializer = MemberCommissionSettleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commission = self.get_object()
        if commission.status == "settled":
            return Response(self.get_serializer(commission).data)
        balance, _ = Balance.objects.get_or_create(user_id=commission.inviter_id, defaults={"bot_id": commission.bot_id})
        field = commission.token_type if commission.token_type in {"trx", "usdt", "integral"} else "usdt"
        before = getattr(balance, field)
        after = before + commission.amount
        setattr(balance, field, after)
        if commission.bot_id and not balance.bot_id:
            balance.bot_id = commission.bot_id
        balance.save(update_fields=[field, "bot_id", "updated_at"])
        RunningWater.objects.create(
            user_id=commission.inviter_id,
            bot_id=commission.bot_id,
            business_type="member_commission",
            amount=commission.amount,
            token_type=field,
            before_balance=before,
            after_balance=after,
            ref_no=commission.source_order_no,
        )
        commission.status = "settled"
        commission.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(commission).data)
