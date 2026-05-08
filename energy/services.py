from django.conf import settings
import httpx
from .models import EnergyOrder

class SohuEnergyService:
    """Python adapter for the sohu energy API used by the Java project."""

    def __init__(self):
        self.base = settings.SOHU_API_BASE_URL.rstrip("/")
        self.secret = settings.SOHU_API_SECRET

    def _headers(self):
        return {"Content-Type": "application/json", "X-API-SECRET": self.secret} if self.secret else {"Content-Type": "application/json"}

    def get_price(self) -> dict:
        return httpx.get(f"{self.base}/delegate/energy/getPrice", headers=self._headers(), timeout=20).json()

    def delegate_smart(self, receiver_address: str, amount: int, order_no: str) -> dict:
        payload = {"receiverAddress": receiver_address, "amount": amount, "orderNo": order_no}
        return httpx.post(f"{self.base}/delegate/energy/smart", json=payload, headers=self._headers(), timeout=30).json()

    def delegate_times(self, receiver_address: str, times: int, order_no: str) -> dict:
        payload = {"receiverAddress": receiver_address, "times": times, "orderNo": order_no}
        return httpx.post(f"{self.base}/delegate/energy/times", json=payload, headers=self._headers(), timeout=30).json()

    def handle_callback(self, payload: dict) -> dict:
        order_no = str(payload.get("orderNo") or payload.get("order_no") or "")
        if not order_no:
            return {"ok": False, "error": "missing orderNo"}
        order = EnergyOrder.objects.filter(order_no=order_no).first()
        if not order:
            return {"ok": False, "error": "order not found"}
        order.callback_payload = payload
        status = str(payload.get("status", "")).lower()
        if status in {"success", "ok", "1"}:
            order.status = "success"
        elif status in {"failed", "fail", "0"}:
            order.status = "failed"
        order.energy_txid = payload.get("hash") or payload.get("txid") or order.energy_txid
        order.platform_order_id = payload.get("platformOrderId") or order.platform_order_id
        order.save(update_fields=["callback_payload", "status", "energy_txid", "platform_order_id", "updated_at"])
        return {"ok": True, "order_no": order_no, "status": order.status}
