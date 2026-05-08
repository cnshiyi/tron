from decimal import Decimal

from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from exchange.models import ExchangeOrder
from finance.models import Balance, RunningWater
from membership.models import MemberRecharge
from .models import Address, ChainTransaction, ListenAddress
from .serializers import AddressSerializer, ChainTransactionSerializer, ListenAddressScanSerializer, ListenAddressSerializer
from .services import TronGridService


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by("-id")
    serializer_class = AddressSerializer
    filterset_fields = ["address_type", "allocated", "bot_id", "user_id"]
    search_fields = ["address", "username"]


class ChainTransactionViewSet(viewsets.ModelViewSet):
    queryset = ChainTransaction.objects.all().order_by("-id")
    serializer_class = ChainTransactionSerializer
    filterset_fields = ["token_type", "confirmed", "to_address", "from_address", "processed", "matched_business", "ref_no"]
    search_fields = ["txid", "from_address", "to_address", "ref_no"]

    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        tx = self.get_object()
        result = process_chain_transaction(tx, apply=True)
        return Response(result)


class ListenAddressViewSet(viewsets.ModelViewSet):
    queryset = ListenAddress.objects.all().order_by("-id")
    serializer_class = ListenAddressSerializer
    filterset_fields = ["bot_id", "token_type", "enabled"]
    search_fields = ["address", "label"]

    @action(detail=True, methods=["post"], url_path="scan")
    def scan(self, request, pk=None):
        serializer = ListenAddressScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listen = self.get_object()
        result = scan_listen_address(listen, **serializer.validated_data)
        return Response(result)

    @action(detail=False, methods=["post"], url_path="scan-enabled")
    def scan_enabled(self, request):
        serializer = ListenAddressScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = [scan_listen_address(item, **serializer.validated_data) for item in ListenAddress.objects.filter(enabled=True).order_by("id")]
        return Response({"count": len(results), "results": results})


class TransactionProbeView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, address: str):
        return Response(TronGridService().account_overview(address))


def scan_listen_address(listen: ListenAddress, apply: bool = False, limit: int = 20) -> dict:
    service = TronGridService()
    created = []
    skipped = []
    processed = []
    transfers = service.list_trc20_transactions(listen.address, limit=limit) if listen.token_type.lower() == "usdt" else []
    for raw in transfers:
        item = service.parse_usdt_transfer(raw)
        if not item["txid"] or item["to_address"] != listen.address:
            continue
        if item["amount"] < listen.min_amount:
            skipped.append({"txid": item["txid"], "reason": "below_min_amount", "amount": str(item["amount"])})
            continue
        tx, was_created = ChainTransaction.objects.get_or_create(
            txid=item["txid"],
            defaults={**item, "listen_address": listen.address},
        )
        if was_created:
            created.append(tx.txid)
        if apply:
            processed.append(process_chain_transaction(tx, apply=True))
        if was_created or apply:
            listen.last_scanned_txid = tx.txid
    if created or processed:
        listen.save(update_fields=["last_scanned_txid", "updated_at"])
    return {"listen_address": listen.address, "created": created, "created_count": len(created), "skipped": skipped, "processed": processed, "apply": apply}


@transaction.atomic
def process_chain_transaction(tx: ChainTransaction, apply: bool = True) -> dict:
    if tx.processed:
        return {"ok": True, "already_processed": True, "txid": tx.txid, "matched_business": tx.matched_business, "ref_no": tx.ref_no}
    if tx.token_type != "usdt" or not tx.confirmed:
        return {"ok": False, "txid": tx.txid, "reason": "unsupported_or_unconfirmed"}

    # 1) 会员充值：按 txid 或金额/地址匹配待支付记录
    recharge = MemberRecharge.objects.filter(txid=tx.txid).first() or MemberRecharge.objects.filter(status="pending", token_type="usdt", amount=tx.amount).order_by("id").first()
    if recharge:
        recharge.status = "paid"
        recharge.txid = tx.txid
        recharge.save(update_fields=["status", "txid", "updated_at"])
        balance, _ = Balance.objects.get_or_create(user_id=recharge.user_id, defaults={"bot_id": recharge.bot_id})
        before = balance.usdt
        after = before + recharge.amount
        balance.usdt = after
        if recharge.bot_id and not balance.bot_id:
            balance.bot_id = recharge.bot_id
        balance.save(update_fields=["usdt", "bot_id", "updated_at"])
        RunningWater.objects.create(user_id=recharge.user_id, bot_id=recharge.bot_id, business_type="chain_member_recharge", amount=recharge.amount, token_type="usdt", before_balance=before, after_balance=after, ref_no=recharge.order_no)
        tx.processed = True
        tx.matched_business = "member_recharge"
        tx.ref_no = recharge.order_no
        tx.save(update_fields=["processed", "matched_business", "ref_no", "updated_at"])
        return {"ok": True, "txid": tx.txid, "matched_business": "member_recharge", "ref_no": recharge.order_no}

    # 2) 兑换订单：按支付 Hash 或支付金额匹配待支付订单
    order = ExchangeOrder.objects.filter(pay_txid=tx.txid).first() or ExchangeOrder.objects.filter(status="pending", amount=tx.amount).order_by("id").first()
    if order:
        order.status = "paid"
        order.pay_txid = tx.txid
        order.save(update_fields=["status", "pay_txid", "updated_at"])
        tx.processed = True
        tx.matched_business = "exchange_order"
        tx.ref_no = order.order_no
        tx.save(update_fields=["processed", "matched_business", "ref_no", "updated_at"])
        return {"ok": True, "txid": tx.txid, "matched_business": "exchange_order", "ref_no": order.order_no}

    tx.processed = True
    tx.matched_business = "unmatched"
    tx.save(update_fields=["processed", "matched_business", "updated_at"])
    return {"ok": True, "txid": tx.txid, "matched_business": "unmatched", "ref_no": ""}
