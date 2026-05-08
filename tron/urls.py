from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.auth_views import codes, login, logout, refresh, user_info
from accounts.views import DashboardView
from bots.views import BotGroupViewSet, BotViewSet, PromotionViewSet, telegram_webhook
from wallet.views import AddressViewSet, ChainTransactionViewSet, ListenAddressViewSet, TransactionProbeView
from exchange.views import ExchangeConfigViewSet, ExchangeOrderViewSet, ExchangeBlacklistViewSet
from energy.views import (
    AdvanceRecordViewSet,
    EnergyAddressConfigViewSet,
    EnergyAgentRecordViewSet,
    EnergyCallbackView,
    EnergyCommissionViewSet,
    EnergyOrderViewSet,
    EnergyPlanViewSet,
)
from membership.views import (
    MemberActivityViewSet,
    MemberCommissionViewSet,
    MemberGoodsViewSet,
    MemberOrderViewSet,
    MemberRechargeViewSet,
)
from finance.views import BalanceViewSet, WithdrawalViewSet, RunningWaterViewSet
from tgusers.views import TgUserViewSet, UserTopViewSet

router = DefaultRouter()
router.register(r"bots", BotViewSet)
router.register(r"promotions", PromotionViewSet)
router.register(r"bot-groups", BotGroupViewSet)
router.register(r"users", TgUserViewSet)
router.register(r"user-tops", UserTopViewSet)
router.register(r"addresses", AddressViewSet)
router.register(r"listen-addresses", ListenAddressViewSet)
router.register(r"transactions", ChainTransactionViewSet)
router.register(r"exchange/configs", ExchangeConfigViewSet)
router.register(r"exchange/orders", ExchangeOrderViewSet)
router.register(r"exchange/blacklist", ExchangeBlacklistViewSet)
router.register(r"energy/plans", EnergyPlanViewSet)
router.register(r"energy/orders", EnergyOrderViewSet)
router.register(r"energy/commissions", EnergyCommissionViewSet)
router.register(r"energy/agent-records", EnergyAgentRecordViewSet)
router.register(r"energy/advance-records", AdvanceRecordViewSet)
router.register(r"energy/address-configs", EnergyAddressConfigViewSet)
router.register(r"membership/goods", MemberGoodsViewSet)
router.register(r"membership/orders", MemberOrderViewSet)
router.register(r"membership/recharges", MemberRechargeViewSet)
router.register(r"membership/activities", MemberActivityViewSet)
router.register(r"membership/commissions", MemberCommissionViewSet)
router.register(r"finance/balances", BalanceViewSet)
router.register(r"finance/withdrawals", WithdrawalViewSet)
router.register(r"finance/running-water", RunningWaterViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login", login, name="auth-login"),
    path("api/auth/refresh", refresh, name="auth-refresh"),
    path("api/auth/logout", logout, name="auth-logout"),
    path("api/auth/codes", codes, name="auth-codes"),
    path("api/user/info", user_info, name="user-info"),
    path("api/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/wallet/probe/<str:address>/", TransactionProbeView.as_view(), name="wallet-probe"),
    path("api/energy/callback/", EnergyCallbackView.as_view(), name="energy-callback"),
    path("api/telegram/webhook/<str:bot_id>/", telegram_webhook, name="telegram-webhook"),
    path("api/", include(router.urls)),
]
