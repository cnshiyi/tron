from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncDate
from rest_framework.response import Response
from rest_framework.views import APIView

from bots.models import Bot, BotGroup
from energy.models import EnergyOrder, EnergyRecord
from exchange.models import ExchangeOrder, ExchangeRecord
from finance.models import Balance, RunningWater, Withdrawal
from membership.models import MemberCommission, MemberOrder, MemberRecharge
from tgusers.models import TgUser
from wallet.models import ChainTransaction, ListenAddress


def decimal_to_float(value):
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return float(value)
    return value


def sum_field(queryset, field):
    return decimal_to_float(queryset.aggregate(total=Coalesce(Sum(field), Decimal("0")))["total"])


def status_counts(queryset, field="status"):
    return list(queryset.values(field).annotate(count=Count("id")).order_by(field))


def daily_amount(queryset, amount_field, days=14):
    rows = (
        queryset.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"), amount=Coalesce(Sum(amount_field), Decimal("0")))
        .order_by("-day")[:days]
    )
    return [
        {"date": row["day"].isoformat() if row["day"] else "", "count": row["count"], "amount": decimal_to_float(row["amount"])}
        for row in reversed(rows)
    ]


class DashboardView(APIView):
    def get(self, request):
        return Response({
            "bots": Bot.objects.count(),
            "bot_groups": BotGroup.objects.count(),
            "users": TgUser.objects.count(),
            "blacklisted_users": TgUser.objects.filter(is_blacklisted=True).count(),
            "exchange_orders": ExchangeOrder.objects.count(),
            "energy_orders": EnergyOrder.objects.count(),
            "member_orders": MemberOrder.objects.count(),
            "balances": Balance.objects.count(),
            "listen_addresses": ListenAddress.objects.filter(enabled=True).count(),
            "chain_transactions": ChainTransaction.objects.count(),
            "pending_withdrawals": Withdrawal.objects.filter(status="pending").count(),
            "withdrawal_amount_pending": sum_field(Withdrawal.objects.filter(status="pending"), "amount"),
            "balance_usdt": sum_field(Balance.objects.all(), "usdt"),
            "balance_trx": sum_field(Balance.objects.all(), "trx"),
        })


class ReportOverviewView(APIView):
    def get(self, request):
        exchange_success = ExchangeOrder.objects.filter(status__in=["sent", "paid"])
        energy_success = EnergyOrder.objects.filter(status="success")
        member_success = MemberOrder.objects.filter(status__in=["paid", "activated"])
        withdrawal_paid = Withdrawal.objects.filter(status="paid")
        return Response({
            "summary": {
                "users": TgUser.objects.count(),
                "new_users": TgUser.objects.order_by("-id").count(),
                "bots": Bot.objects.count(),
                "groups": BotGroup.objects.count(),
                "exchange_order_count": ExchangeOrder.objects.count(),
                "exchange_amount": sum_field(exchange_success, "amount"),
                "exchange_return_amount": sum_field(exchange_success, "return_amount"),
                "exchange_profit_usdt": sum_field(exchange_success, "profit_usdt"),
                "energy_order_count": EnergyOrder.objects.count(),
                "energy_trx_amount": sum_field(energy_success, "trx_amount"),
                "energy_usdt_amount": sum_field(energy_success, "usdt_amount"),
                "member_order_count": MemberOrder.objects.count(),
                "member_amount": sum_field(member_success, "amount"),
                "member_recharge_amount": sum_field(MemberRecharge.objects.filter(status__in=["paid", "success"]), "amount"),
                "commission_amount": sum_field(MemberCommission.objects.filter(status__in=["paid", "settled"]), "amount"),
                "withdrawal_paid_amount": sum_field(withdrawal_paid, "amount"),
                "running_water_amount": sum_field(RunningWater.objects.all(), "amount"),
            },
            "status": {
                "exchange_orders": status_counts(ExchangeOrder.objects.all()),
                "exchange_records": status_counts(ExchangeRecord.objects.all()),
                "energy_orders": status_counts(EnergyOrder.objects.all()),
                "energy_records": status_counts(EnergyRecord.objects.all()),
                "member_orders": status_counts(MemberOrder.objects.all()),
                "member_recharges": status_counts(MemberRecharge.objects.all()),
                "withdrawals": status_counts(Withdrawal.objects.all()),
            },
            "daily": {
                "exchange": daily_amount(ExchangeOrder.objects.all(), "amount"),
                "energy": daily_amount(EnergyOrder.objects.all(), "trx_amount"),
                "member": daily_amount(MemberOrder.objects.all(), "amount"),
                "withdrawal": daily_amount(Withdrawal.objects.all(), "amount"),
            },
            "tokens": list(RunningWater.objects.values("token_type").annotate(count=Count("id"), amount=Coalesce(Sum("amount"), Decimal("0"))).order_by("token_type")),
        })
