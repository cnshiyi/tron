from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.auth_views import codes, login, logout, refresh, user_info
from accounts.views import DashboardView, ReportOverviewView
from bots.views import BotGroupViewSet, BotViewSet, BroadcastLogViewSet, PromotionViewSet, telegram_webhook
from wallet.views import AddressViewSet, ChainTransactionViewSet, ListenAddressViewSet, TransactionProbeView
from exchange.views import ExchangeBlacklistViewSet, ExchangeConfigViewSet, ExchangeOrderViewSet, ExchangeRecordViewSet
from energy.views import (
    AdvanceRecordViewSet,
    EnergyAddressConfigViewSet,
    EnergyAgentRecordViewSet,
    EnergyCallbackView,
    EnergyCommissionViewSet,
    EnergyHourlyTimePriceViewSet,
    EnergyHourlyTimeViewSet,
    EnergyIntelligentPlanViewSet,
    EnergyOrderViewSet,
    EnergyPenFlashEntryViewSet,
    EnergyPenPlanViewSet,
    EnergyPlanViewSet,
    EnergyRecordViewSet,
    NumberOfOrdersViewSet,
    StakingAccountViewSet,
    StakingOrderViewSet,
    StakingTransactionViewSet,
)
from membership.views import (
    MemberActivityViewSet,
    MemberCommissionViewSet,
    MemberGoodsViewSet,
    MemberOrderViewSet,
    MemberRechargeViewSet,
)
from finance.views import BalanceViewSet, RechargeConfigViewSet, WithdrawalViewSet, RunningWaterViewSet
from tgusers.views import TgUserViewSet, UserTopViewSet
from configcenter.views import TextConfigViewSet, ui_text

router = DefaultRouter()
router.register(r"bots", BotViewSet)
router.register(r"promotions", PromotionViewSet)
router.register(r"bot-groups", BotGroupViewSet)
router.register(r"broadcast-logs", BroadcastLogViewSet)
router.register(r"users", TgUserViewSet)
router.register(r"user-tops", UserTopViewSet)
router.register(r"addresses", AddressViewSet)
router.register(r"listen-addresses", ListenAddressViewSet)
router.register(r"transactions", ChainTransactionViewSet)
router.register(r"exchange/configs", ExchangeConfigViewSet)
router.register(r"exchange/orders", ExchangeOrderViewSet)
router.register(r"exchange/records", ExchangeRecordViewSet)
router.register(r"exchange/blacklist", ExchangeBlacklistViewSet)
router.register(r"energy/plans", EnergyPlanViewSet)
router.register(r"energy/orders", EnergyOrderViewSet)
router.register(r"energy/commissions", EnergyCommissionViewSet)
router.register(r"energy/agent-records", EnergyAgentRecordViewSet)
router.register(r"energy/advance-records", AdvanceRecordViewSet)
router.register(r"energy/address-configs", EnergyAddressConfigViewSet)
router.register(r"energy/hourly-times", EnergyHourlyTimeViewSet)
router.register(r"energy/hourly-time-prices", EnergyHourlyTimePriceViewSet)
router.register(r"energy/pen-plans", EnergyPenPlanViewSet)
router.register(r"energy/number-of-orders", NumberOfOrdersViewSet)
router.register(r"energy/pen-flash-entries", EnergyPenFlashEntryViewSet)
router.register(r"energy/intelligent-plans", EnergyIntelligentPlanViewSet)
router.register(r"energy/records", EnergyRecordViewSet)
router.register(r"staking/accounts", StakingAccountViewSet)
router.register(r"staking/orders", StakingOrderViewSet)
router.register(r"staking/transactions", StakingTransactionViewSet)
router.register(r"membership/goods", MemberGoodsViewSet)
router.register(r"membership/orders", MemberOrderViewSet)
router.register(r"membership/recharges", MemberRechargeViewSet)
router.register(r"membership/activities", MemberActivityViewSet)
router.register(r"membership/commissions", MemberCommissionViewSet)
router.register(r"finance/balances", BalanceViewSet)
router.register(r"finance/withdrawals", WithdrawalViewSet)
router.register(r"finance/running-water", RunningWaterViewSet)
router.register(r"finance/recharge-configs", RechargeConfigViewSet)
router.register(r"text-configs", TextConfigViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login", login, name="auth-login"),
    path("api/auth/refresh", refresh, name="auth-refresh"),
    path("api/auth/logout", logout, name="auth-logout"),
    path("api/auth/codes", codes, name="auth-codes"),
    path("api/user/info", user_info, name="user-info"),
    path("api/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/reports/overview/", ReportOverviewView.as_view(), name="reports-overview"),
    path("api/ui-text/", ui_text, name="ui-text"),
    path("api/wallet/probe/<str:address>/", TransactionProbeView.as_view(), name="wallet-probe"),
    path("api/energy/callback/", EnergyCallbackView.as_view(), name="energy-callback"),
    path("api/telegram/webhook/<str:bot_id>/", telegram_webhook, name="telegram-webhook"),
    path("api/", include(router.urls)),
]
