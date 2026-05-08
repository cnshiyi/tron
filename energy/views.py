from rest_framework import viewsets
from rest_framework.decorators import action
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

    def _update_order(self, status_value: str, txid_field: str = "", txid: str = ""):
        order = self.get_object()
        order.status = status_value
        update_fields = ["status", "updated_at"]
        if txid_field and txid:
            setattr(order, txid_field, txid)
            update_fields.append(txid_field)
        platform_order_id = self.request.data.get("platform_order_id", "")
        if platform_order_id:
            order.platform_order_id = platform_order_id
            update_fields.append("platform_order_id")
        order.save(update_fields=update_fields)
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        return self._update_order("paid", "pay_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="delegating")
    def delegating(self, request, pk=None):
        return self._update_order("delegating")

    @action(detail=True, methods=["post"], url_path="success")
    def success(self, request, pk=None):
        return self._update_order("success", "energy_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        return self._update_order("failed")

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

    def _review(self, status_value: str):
        record = self.get_object()
        record.status = status_value
        record.reviewed_by = self.request.data.get("reviewed_by", record.reviewed_by or "admin")
        record.save(update_fields=["status", "reviewed_by", "updated_at"])
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        return self._review("approved")

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        return self._review("rejected")

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

    def _update_record(self, status_value: str, txid: str = ""):
        record = self.get_object()
        record.status = status_value
        update_fields = ["status", "updated_at"]
        if txid:
            record.txid = txid
            update_fields.append("txid")
        record.save(update_fields=update_fields)
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"], url_path="success")
    def success(self, request, pk=None):
        return self._update_record("success", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        return self._update_record("failed")

class EnergyCallbackView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        return Response(SohuEnergyService().handle_callback(request.data))
