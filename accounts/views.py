from rest_framework.views import APIView
from rest_framework.response import Response
from bots.models import Bot
from exchange.models import ExchangeOrder
from energy.models import EnergyOrder
from finance.models import Balance, Withdrawal

class DashboardView(APIView):
    def get(self, request):
        return Response({
            "bots": Bot.objects.count(),
            "exchange_orders": ExchangeOrder.objects.count(),
            "energy_orders": EnergyOrder.objects.count(),
            "balances": Balance.objects.count(),
            "pending_withdrawals": Withdrawal.objects.filter(status="pending").count(),
        })
