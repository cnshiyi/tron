from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    AdvanceRecord,
    EnergyAddressConfig,
    EnergyAgentRecord,
    EnergyCommission,
    EnergyHourlyTime,
    EnergyHourlyTimePrice,
    EnergyIntelligentPlan,
    EnergyOrder,
    EnergyPenFlashEntry,
    EnergyPenPlan,
    EnergyPlan,
    EnergyRecord,
    NumberOfOrders,
)
from .serializers import (
    AdvanceRecordSerializer,
    EnergyAddressConfigSerializer,
    EnergyAgentRecordSerializer,
    EnergyCommissionSerializer,
    EnergyHourlyTimePriceSerializer,
    EnergyHourlyTimeSerializer,
    EnergyIntelligentPlanSerializer,
    EnergyOrderSerializer,
    EnergyPenFlashEntrySerializer,
    EnergyPenPlanSerializer,
    EnergyPlanSerializer,
    EnergyRecordSerializer,
    NumberOfOrdersSerializer,
)
from .services import SohuEnergyService

class EnergyPlanViewSet(viewsets.ModelViewSet):
    queryset = EnergyPlan.objects.all().order_by("sort", "id")
    serializer_class = EnergyPlanSerializer
    filterset_fields = ["bot_id", "mode"]
    search_fields = ["name"]

class EnergyOrderViewSet(viewsets.ModelViewSet):
    queryset = EnergyOrder.objects.all().order_by("-id")
    serializer_class = EnergyOrderSerializer
    filterset_fields = ["bot_id", "user_id", "status", "pay_type"]
    search_fields = ["order_no", "receiver_address", "pay_txid", "energy_txid", "platform_order_id"]

class EnergyCommissionViewSet(viewsets.ModelViewSet):
    queryset = EnergyCommission.objects.select_related("order").all().order_by("-id")
    serializer_class = EnergyCommissionSerializer
    search_fields = ["order__order_no"]

class EnergyAgentRecordViewSet(viewsets.ModelViewSet):
    queryset = EnergyAgentRecord.objects.all().order_by("-id")
    serializer_class = EnergyAgentRecordSerializer
    filterset_fields = ["bot_id", "agent_user_id", "user_id", "status"]
    search_fields = ["order_no", "receiver_address", "txid"]

class AdvanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRecord.objects.all().order_by("-id")
    serializer_class = AdvanceRecordSerializer
    filterset_fields = ["bot_id", "user_id", "status", "token_type"]
    search_fields = ["user_id", "reason", "reviewed_by"]

class EnergyAddressConfigViewSet(viewsets.ModelViewSet):
    queryset = EnergyAddressConfig.objects.all().order_by("-id")
    serializer_class = EnergyAddressConfigSerializer
    filterset_fields = ["bot_id", "mode", "enabled"]
    search_fields = ["address"]

class EnergyHourlyTimeViewSet(viewsets.ModelViewSet):
    queryset = EnergyHourlyTime.objects.all().order_by("sort", "id")
    serializer_class = EnergyHourlyTimeSerializer
    filterset_fields = ["bot_id", "enabled"]
    search_fields = ["name"]

class EnergyHourlyTimePriceViewSet(viewsets.ModelViewSet):
    queryset = EnergyHourlyTimePrice.objects.select_related("time").all().order_by("-id")
    serializer_class = EnergyHourlyTimePriceSerializer
    filterset_fields = ["bot_id", "time", "enabled"]

class EnergyPenPlanViewSet(viewsets.ModelViewSet):
    queryset = EnergyPenPlan.objects.all().order_by("sort", "id")
    serializer_class = EnergyPenPlanSerializer
    filterset_fields = ["bot_id", "enabled"]
    search_fields = ["name"]

class NumberOfOrdersViewSet(viewsets.ModelViewSet):
    queryset = NumberOfOrders.objects.all().order_by("-id")
    serializer_class = NumberOfOrdersSerializer
    filterset_fields = ["bot_id", "user_id"]
    search_fields = ["user_id", "source_order_no"]

class EnergyPenFlashEntryViewSet(viewsets.ModelViewSet):
    queryset = EnergyPenFlashEntry.objects.all().order_by("sort", "id")
    serializer_class = EnergyPenFlashEntrySerializer
    filterset_fields = ["bot_id", "enabled"]
    search_fields = ["title", "address"]

class EnergyIntelligentPlanViewSet(viewsets.ModelViewSet):
    queryset = EnergyIntelligentPlan.objects.all().order_by("sort", "id")
    serializer_class = EnergyIntelligentPlanSerializer
    filterset_fields = ["bot_id", "enabled", "strategy"]
    search_fields = ["name"]

class EnergyRecordViewSet(viewsets.ModelViewSet):
    queryset = EnergyRecord.objects.all().order_by("-id")
    serializer_class = EnergyRecordSerializer
    filterset_fields = ["bot_id", "user_id", "mode", "status"]
    search_fields = ["order_no", "receiver_address", "txid"]

class EnergyCallbackView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        return Response(SohuEnergyService().handle_callback(request.data))
