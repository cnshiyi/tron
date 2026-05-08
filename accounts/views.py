from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
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


def apply_report_filters(queryset, request, bot_field="bot_id"):
    bot_id = request.query_params.get("bot_id")
    days = int(request.query_params.get("days") or 14)
    days = max(1, min(days, 365))
    since = timezone.now() - timedelta(days=days)
    queryset = queryset.filter(created_at__gte=since)
    if bot_id and bot_field:
        queryset = queryset.filter(**{bot_field: bot_id})
    return queryset, days, since


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
        exchange_orders, days, since = apply_report_filters(ExchangeOrder.objects.all(), request)
        exchange_records, _, _ = apply_report_filters(ExchangeRecord.objects.all(), request)
        energy_orders, _, _ = apply_report_filters(EnergyOrder.objects.all(), request)
        energy_records, _, _ = apply_report_filters(EnergyRecord.objects.all(), request)
        member_orders, _, _ = apply_report_filters(MemberOrder.objects.all(), request, bot_field=None)
        member_recharges, _, _ = apply_report_filters(MemberRecharge.objects.all(), request)
        member_commissions, _, _ = apply_report_filters(MemberCommission.objects.all(), request)
        withdrawals, _, _ = apply_report_filters(Withdrawal.objects.all(), request, bot_field=None)
        running_water, _, _ = apply_report_filters(RunningWater.objects.all(), request)
        users = TgUser.objects.filter(created_at__gte=since)
        if request.query_params.get("bot_id"):
            users = users.filter(bot_id=request.query_params["bot_id"])
        exchange_success = exchange_orders.filter(status__in=["sent", "paid"])
        energy_success = energy_orders.filter(status="success")
        member_success = member_orders.filter(status__in=["paid", "activated"])
        withdrawal_paid = withdrawals.filter(status="paid")
        return Response({
            "filters": {"days": days, "bot_id": request.query_params.get("bot_id", ""), "since": since.isoformat()},
            "summary": {
                "users": TgUser.objects.count(),
                "new_users": users.count(),
                "bots": Bot.objects.count(),
                "groups": BotGroup.objects.count(),
                "exchange_order_count": exchange_orders.count(),
                "exchange_amount": sum_field(exchange_success, "amount"),
                "exchange_return_amount": sum_field(exchange_success, "return_amount"),
                "exchange_profit_usdt": sum_field(exchange_success, "profit_usdt"),
                "energy_order_count": energy_orders.count(),
                "energy_trx_amount": sum_field(energy_success, "trx_amount"),
                "energy_usdt_amount": sum_field(energy_success, "usdt_amount"),
                "member_order_count": member_orders.count(),
                "member_amount": sum_field(member_success, "amount"),
                "member_recharge_amount": sum_field(member_recharges.filter(status__in=["paid", "success"]), "amount"),
                "commission_amount": sum_field(member_commissions.filter(status__in=["paid", "settled"]), "amount"),
                "withdrawal_paid_amount": sum_field(withdrawal_paid, "amount"),
                "running_water_amount": sum_field(running_water, "amount"),
            },
            "status": {
                "exchange_orders": status_counts(exchange_orders),
                "exchange_records": status_counts(exchange_records),
                "energy_orders": status_counts(energy_orders),
                "energy_records": status_counts(energy_records),
                "member_orders": status_counts(member_orders),
                "member_recharges": status_counts(member_recharges),
                "withdrawals": status_counts(withdrawals),
            },
            "daily": {
                "exchange": daily_amount(exchange_orders, "amount", days),
                "energy": daily_amount(energy_orders, "trx_amount", days),
                "member": daily_amount(member_orders, "amount", days),
                "withdrawal": daily_amount(withdrawals, "amount", days),
            },
            "tokens": list(running_water.values("token_type").annotate(count=Count("id"), amount=Coalesce(Sum("amount"), Decimal("0"))).order_by("token_type")),
        })
