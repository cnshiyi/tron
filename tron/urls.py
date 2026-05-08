from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import DashboardView
from bots.views import BotViewSet, PromotionViewSet, telegram_webhook
from wallet.views import AddressViewSet, TransactionProbeView
from exchange.views import ExchangeConfigViewSet, ExchangeOrderViewSet, ExchangeBlacklistViewSet
from energy.views import EnergyPlanViewSet, EnergyOrderViewSet, EnergyCallbackView
from membership.views import MemberGoodsViewSet, MemberOrderViewSet
from finance.views import BalanceViewSet, WithdrawalViewSet, RunningWaterViewSet

router = DefaultRouter()
router.register(r"bots", BotViewSet)
router.register(r"promotions", PromotionViewSet)
router.register(r"addresses", AddressViewSet)
router.register(r"exchange/configs", ExchangeConfigViewSet)
router.register(r"exchange/orders", ExchangeOrderViewSet)
router.register(r"exchange/blacklist", ExchangeBlacklistViewSet)
router.register(r"energy/plans", EnergyPlanViewSet)
router.register(r"energy/orders", EnergyOrderViewSet)
router.register(r"membership/goods", MemberGoodsViewSet)
router.register(r"membership/orders", MemberOrderViewSet)
router.register(r"finance/balances", BalanceViewSet)
router.register(r"finance/withdrawals", WithdrawalViewSet)
router.register(r"finance/running-water", RunningWaterViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/wallet/probe/<str:address>/", TransactionProbeView.as_view(), name="wallet-probe"),
    path("api/energy/callback/", EnergyCallbackView.as_view(), name="energy-callback"),
    path("api/telegram/webhook/<str:bot_id>/", telegram_webhook, name="telegram-webhook"),
    path("api/", include(router.urls)),
]
