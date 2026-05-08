from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExchangeBlacklist, ExchangeConfig, ExchangeOrder, ExchangeRecord
from .serializers import ExchangeBlacklistSerializer, ExchangeConfigSerializer, ExchangeOrderSerializer, ExchangeRecordSerializer

class ExchangeConfigViewSet(viewsets.ModelViewSet):
    queryset = ExchangeConfig.objects.all().order_by("-id")
    serializer_class = ExchangeConfigSerializer
    filterset_fields = ["bot_id", "auto_mode"]

class ExchangeOrderViewSet(viewsets.ModelViewSet):
    queryset = ExchangeOrder.objects.all().order_by("-id")
    serializer_class = ExchangeOrderSerializer
    filterset_fields = ["bot_id", "user_id", "type", "status"]
    search_fields = ["order_no", "address", "pay_txid", "payout_txid"]

    def _update_order(self, status_value: str, txid_field: str = "", txid: str = ""):
        order = self.get_object()
        order.status = status_value
        update_fields = ["status", "updated_at"]
        if txid_field and txid:
            setattr(order, txid_field, txid)
            update_fields.append(txid_field)
        order.save(update_fields=update_fields)
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        return self._update_order("paid", "pay_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="mark-sent")
    def mark_sent(self, request, pk=None):
        return self._update_order("sent", "payout_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        return self._update_order("failed")

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        return self._update_order("cancelled")

class ExchangeBlacklistViewSet(viewsets.ModelViewSet):
    queryset = ExchangeBlacklist.objects.all().order_by("-id")
    serializer_class = ExchangeBlacklistSerializer
    search_fields = ["address", "reason"]

class ExchangeRecordViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRecord.objects.all().order_by("-id")
    serializer_class = ExchangeRecordSerializer
    filterset_fields = ["bot_id", "user_id", "from_token", "to_token", "status"]
    search_fields = ["order_no", "pay_txid", "payout_txid"]

    def _update_record(self, status_value: str, txid_field: str = "", txid: str = ""):
        record = self.get_object()
        record.status = status_value
        update_fields = ["status", "updated_at"]
        if txid_field and txid:
            setattr(record, txid_field, txid)
            update_fields.append(txid_field)
        record.save(update_fields=update_fields)
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        return self._update_record("paid", "pay_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="mark-sent")
    def mark_sent(self, request, pk=None):
        return self._update_record("sent", "payout_txid", request.data.get("txid", ""))

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        return self._update_record("failed")
