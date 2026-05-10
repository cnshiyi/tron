from datetime import timedelta
from decimal import Decimal
import re

from django.conf import settings
from django.utils import timezone
import httpx
from tronpy import Tron
from tronpy.keys import PrivateKey

from .models import EnergyOrder, StakingAccount, StakingOrder, StakingTransaction

SUN = 1_000_000


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

    def delegate_order(self, order: EnergyOrder, dry_run: bool = True, mode: str = "smart") -> dict:
        payload = {
            "receiverAddress": order.receiver_address,
            "amount": order.energy_amount,
            "times": getattr(order.plan, "number_of_times", 0) if order.plan else 0,
            "orderNo": order.order_no,
            "mode": mode,
        }
        if dry_run or not getattr(settings, "SOHU_SEND_ENABLED", False):
            return {"ok": True, "dry_run": True, "platform_order_id": f"dry-{order.order_no}", "payload": payload}
        try:
            if mode == "times":
                data = self.delegate_times(order.receiver_address, payload["times"] or 1, order.order_no)
            else:
                data = self.delegate_smart(order.receiver_address, order.energy_amount, order.order_no)
            return {"ok": bool(data.get("ok", True)), "data": data, "platform_order_id": str(data.get("orderId") or data.get("platformOrderId") or data.get("data", {}).get("orderId") or "")}
        except Exception as exc:  # pragma: no cover - network protection
            return {"ok": False, "error": str(exc), "payload": payload}


class TronStakingService:
    """TRON 原生质押、委托、回收服务。

    多签处理方式：
    1. StakingAccount.permission_id > 0 时调用 builder.permission_id(permission_id)。
    2. 主私钥 private_key_encrypted + multisig_private_keys 逐个签同一笔交易。
    3. required_signature_count 用来防止本系统漏签；链上权重仍由 TRON 节点校验。
    """

    def __init__(self, client=None):
        self.client = client or Tron(network=getattr(settings, "TRON_NETWORK", "nile"))

    def _private_keys(self, account: StakingAccount) -> list[PrivateKey]:
        raw = "\n".join([account.private_key_encrypted or "", account.multisig_private_keys or ""])
        values = [x.strip() for x in re.split(r"[\s,;]+", raw) if x.strip()]
        keys = []
        for value in values:
            value = value[2:] if value.startswith("0x") else value
            keys.append(PrivateKey(bytes.fromhex(value)))
        return keys

    def _build_sign_broadcast(
        self,
        builder,
        account: StakingAccount,
        operation: str,
        amount_sun: int,
        receiver_address: str = "",
        staking_order: StakingOrder | None = None,
        broadcast: bool = False,
    ) -> dict:
        if account.permission_id:
            builder = builder.permission_id(account.permission_id)
        tx = builder.build()
        keys = self._private_keys(account)
        if len(keys) < account.required_signature_count:
            raise ValueError(f"签名私钥不足：需要 {account.required_signature_count} 个，当前 {len(keys)} 个")
        for key in keys[: account.required_signature_count]:
            tx = tx.sign(key)
        raw = tx.to_json()
        result = {}
        status = "signed"
        if broadcast:
            result = tx.broadcast()
            status = "broadcasted" if (not isinstance(result, dict) or result.get("result", True)) else "failed"
        tx_record = StakingTransaction.objects.create(
            account=account,
            staking_order=staking_order,
            operation=operation,
            resource=account.resource,
            amount_sun=amount_sun,
            receiver_address=receiver_address,
            permission_id=account.permission_id,
            signature_count=len(raw.get("signature") or []),
            txid=raw.get("txID", ""),
            status=status,
            broadcast_result=result if isinstance(result, dict) else {"result": str(result)},
            raw_transaction=raw,
        )
        return {
            "ok": status != "failed",
            "txid": tx_record.txid,
            "status": status,
            "permission_id": tx_record.permission_id,
            "signature_count": tx_record.signature_count,
            "transaction_id": tx_record.id,
            "raw_transaction": raw,
            "broadcast_result": tx_record.broadcast_result,
        }

    def select_account(self, balance_sun: int, energy_amount: int = 0, bot_id: str = "") -> StakingAccount:
        qs = StakingAccount.objects.filter(enabled=True)
        if bot_id:
            qs = qs.filter(bot_id__in=["", bot_id])
        for account in qs.order_by("-max_delegable_sun", "id"):
            if account.available_balance_sun >= balance_sun and (not energy_amount or account.available_energy >= energy_amount):
                return account
        raise ValueError("没有可用的质押账户或可委托额度不足")

    def sync_account(self, account: StakingAccount) -> dict:
        payload = {
            "account": self.client.get_account(account.address),
            "resource": self.client.get_account_resource(account.address),
        }
        resource = payload["resource"] or {}
        account.last_sync_payload = payload
        account.max_energy = int(resource.get("EnergyLimit") or account.max_energy or 0)
        account.used_energy = int(resource.get("EnergyUsed") or account.used_energy or 0)
        account.save(update_fields=["last_sync_payload", "max_energy", "used_energy", "updated_at"])
        return payload

    def stake_trx(self, account: StakingAccount, amount_sun: int, broadcast: bool = False) -> dict:
        builder = self.client.trx.freeze_balance(account.address, int(amount_sun), account.resource)
        result = self._build_sign_broadcast(builder, account, "stake", int(amount_sun), broadcast=broadcast)
        if result["ok"] and broadcast:
            account.frozen_balance_sun += int(amount_sun)
            account.max_delegable_sun += int(amount_sun)
            account.save(update_fields=["frozen_balance_sun", "max_delegable_sun", "updated_at"])
        return result

    def unstake_trx(self, account: StakingAccount, amount_sun: int, broadcast: bool = False) -> dict:
        builder = self.client.trx.unfreeze_balance(account.address, account.resource, unfreeze_balance=int(amount_sun))
        result = self._build_sign_broadcast(builder, account, "unstake", int(amount_sun), broadcast=broadcast)
        if result["ok"] and broadcast:
            account.frozen_balance_sun = max(0, account.frozen_balance_sun - int(amount_sun))
            account.max_delegable_sun = max(0, account.max_delegable_sun - int(amount_sun))
            account.save(update_fields=["frozen_balance_sun", "max_delegable_sun", "updated_at"])
        return result

    def delegate_resource(
        self,
        account: StakingAccount,
        receiver_address: str,
        balance_sun: int,
        energy_amount: int = 0,
        order_no: str = "",
        lock: bool = False,
        lock_period: int | None = None,
        broadcast: bool = False,
        staking_order: StakingOrder | None = None,
    ) -> dict:
        balance_sun = int(balance_sun)
        if account.available_balance_sun < balance_sun:
            raise ValueError("质押账户可委托 SUN 不足")
        if energy_amount and account.available_energy < int(energy_amount):
            raise ValueError("质押账户可用能量不足")
        builder = self.client.trx.delegate_resource(account.address, receiver_address, balance_sun, account.resource, lock=lock, lock_period=lock_period)
        result = self._build_sign_broadcast(builder, account, "delegate", balance_sun, receiver_address, staking_order, broadcast)
        if result["ok"] and broadcast:
            account.delegated_balance_sun += balance_sun
            account.used_energy += int(energy_amount or 0)
            account.save(update_fields=["delegated_balance_sun", "used_energy", "updated_at"])
        return {**result, "order_no": order_no}

    def undelegate_resource(self, staking_order: StakingOrder, broadcast: bool = False) -> dict:
        if not staking_order.account:
            raise ValueError("质押订单没有绑定质押账户")
        account = staking_order.account
        builder = self.client.trx.undelegate_resource(account.address, staking_order.receiver_address, int(staking_order.delegate_balance_sun), staking_order.resource)
        result = self._build_sign_broadcast(builder, account, "undelegate", int(staking_order.delegate_balance_sun), staking_order.receiver_address, staking_order, broadcast)
        if result["ok"] and broadcast:
            account.delegated_balance_sun = max(0, account.delegated_balance_sun - int(staking_order.delegate_balance_sun))
            account.used_energy = max(0, account.used_energy - int(staking_order.energy_amount or 0))
            account.save(update_fields=["delegated_balance_sun", "used_energy", "updated_at"])
        return result

    def delegate_energy_order(self, order: EnergyOrder, broadcast: bool = False, lock: bool = False, lock_period: int | None = None) -> dict:
        balance_sun = int(Decimal(order.trx_amount or 0) * SUN)
        if balance_sun <= 0:
            raise ValueError("能量订单 trx_amount 必须大于 0，用于换算委托 SUN")
        staking_order, _ = StakingOrder.objects.get_or_create(
            order_no=order.order_no,
            defaults={
                "energy_order": order,
                "receiver_address": order.receiver_address,
                "energy_amount": order.energy_amount,
                "delegate_balance_sun": balance_sun,
                "status": "pending",
            },
        )
        account = staking_order.account or self.select_account(balance_sun, order.energy_amount, order.bot_id)
        staking_order.account = account
        staking_order.receiver_address = order.receiver_address
        staking_order.energy_amount = order.energy_amount
        staking_order.delegate_balance_sun = balance_sun
        staking_order.lock = lock
        staking_order.lock_period = lock_period
        staking_order.status = "delegating" if broadcast else "pending"
        staking_order.save()
        result = self.delegate_resource(account, order.receiver_address, balance_sun, order.energy_amount, order.order_no, lock, lock_period, broadcast, staking_order)
        staking_order.delegate_txid = result.get("txid", "")
        staking_order.raw_payload = result
        if result.get("ok"):
            staking_order.status = "success" if broadcast else "pending"
            if broadcast:
                staking_order.expire_at = timezone.now() + timedelta(hours=int(order.plan.duration_hours if order.plan else 1))
        else:
            staking_order.status = "failed"
        staking_order.error_message = result.get("error", "")
        staking_order.save(update_fields=["delegate_txid", "raw_payload", "status", "expire_at", "error_message", "updated_at"])
        if result.get("ok"):
            order.status = "success" if broadcast else order.status
        else:
            order.status = "failed"
        order.energy_txid = result.get("txid", order.energy_txid)
        order.platform_order_id = f"staking:{staking_order.order_no}"
        order.callback_payload = {**(order.callback_payload or {}), "staking_delegate": result}
        order.save(update_fields=["status", "energy_txid", "platform_order_id", "callback_payload", "updated_at"])
        return {**result, "staking_order_id": staking_order.id}

    def reclaim_order(self, staking_order: StakingOrder, broadcast: bool = False) -> dict:
        if staking_order.status not in {"success", "reclaiming"}:
            raise ValueError("只有已委托成功的质押订单可以回收")
        staking_order.status = "reclaiming"
        staking_order.save(update_fields=["status", "updated_at"])
        result = self.undelegate_resource(staking_order, broadcast=broadcast)
        staking_order.undelegate_txid = result.get("txid", "")
        staking_order.raw_payload = {**(staking_order.raw_payload or {}), "reclaim": result}
        staking_order.status = "reclaimed" if result.get("ok") else "failed"
        staking_order.error_message = result.get("error", "")
        staking_order.save(update_fields=["undelegate_txid", "raw_payload", "status", "error_message", "updated_at"])
        return {**result, "staking_order_id": staking_order.id}

    def reclaim_due_orders(self, broadcast: bool = False, now=None, limit: int = 100) -> dict:
        now = now or timezone.now()
        qs = StakingOrder.objects.select_related("account").filter(
            status="success",
            expire_at__isnull=False,
            expire_at__lte=now,
            account__auto_reclaim=True,
            account__enabled=True,
        ).order_by("expire_at", "id")[: int(limit)]
        results = []
        for order in qs:
            try:
                results.append({"order_no": order.order_no, **self.reclaim_order(order, broadcast=broadcast)})
            except Exception as exc:  # pragma: no cover - defensive batch isolation
                order.status = "failed"
                order.error_message = str(exc)
                order.save(update_fields=["status", "error_message", "updated_at"])
                results.append({"order_no": order.order_no, "ok": False, "error": str(exc)})
        return {"ok": True, "total": len(results), "results": results}
