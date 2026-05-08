from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AdvanceRecord, EnergyAddressConfig, EnergyAgentRecord, EnergyCommission, EnergyPlan, EnergyOrder
from .serializers import (
    AdvanceRecordSerializer,
    EnergyAddressConfigSerializer,
    EnergyAgentRecordSerializer,
    EnergyCommissionSerializer,
    EnergyPlanSerializer,
    EnergyOrderSerializer,
)
from .services import SohuEnergyService

class EnergyPlanViewSet(viewsets.ModelViewSet):
    queryset = EnergyPlan.objects.all()
    serializer_class = EnergyPlanSerializer
    filterset_fields = ["bot_id", "mode"]
    search_fields = ["name"]

class EnergyOrderViewSet(viewsets.ModelViewSet):
    queryset = EnergyOrder.objects.all()
    serializer_class = EnergyOrderSerializer
    filterset_fields = ["bot_id", "user_id", "status", "pay_type"]
    search_fields = ["order_no", "receiver_address", "pay_txid", "energy_txid", "platform_order_id"]

class EnergyCommissionViewSet(viewsets.ModelViewSet):
    queryset = EnergyCommission.objects.select_related("order").all()
    serializer_class = EnergyCommissionSerializer
    search_fields = ["order__order_no"]

class EnergyAgentRecordViewSet(viewsets.ModelViewSet):
    queryset = EnergyAgentRecord.objects.all()
    serializer_class = EnergyAgentRecordSerializer
    filterset_fields = ["bot_id", "agent_user_id", "user_id", "status"]
    search_fields = ["order_no", "receiver_address", "txid"]

class AdvanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRecord.objects.all()
    serializer_class = AdvanceRecordSerializer
    filterset_fields = ["bot_id", "user_id", "status", "token_type"]
    search_fields = ["user_id", "reason", "reviewed_by"]

class EnergyAddressConfigViewSet(viewsets.ModelViewSet):
    queryset = EnergyAddressConfig.objects.all()
    serializer_class = EnergyAddressConfigSerializer
    filterset_fields = ["bot_id", "mode", "enabled"]
    search_fields = ["address"]

class EnergyCallbackView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        return Response(SohuEnergyService().handle_callback(request.data))
