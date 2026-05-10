from decimal import Decimal

from django.test import TestCase
from tronpy.keys import PrivateKey

from energy.models import EnergyOrder, StakingAccount, StakingOrder
from energy.services import TronStakingService


class FakeTransaction:
    def __init__(self):
        self.txid = "fake-txid"
        self.permission_id_value = None
        self.signatures = []
        self.broadcasted = False

    def sign(self, private_key):
        self.signatures.append(private_key.public_key.to_base58check_address())
        return self

    def broadcast(self):
        self.broadcasted = True
        return {"result": True, "txid": self.txid}

    def to_json(self):
        return {
            "txID": self.txid,
            "raw_data": {"contract": [{"Permission_id": self.permission_id_value}]},
            "signature": self.signatures,
        }


class FakeBuilder:
    def __init__(self, operation, calls):
        self.operation = operation
        self.calls = calls
        self.transaction = FakeTransaction()

    def permission_id(self, value):
        self.transaction.permission_id_value = value
        return self

    def build(self):
        self.calls.append((self.operation, self.transaction.permission_id_value))
        return self.transaction


class FakeTrx:
    def __init__(self):
        self.calls = []

    def freeze_balance(self, owner, amount, resource="ENERGY"):
        self.calls.append(("freeze_balance", owner, amount, resource))
        return FakeBuilder("freeze", self.calls)

    def unfreeze_balance(self, owner, resource="ENERGY", *, unfreeze_balance):
        self.calls.append(("unfreeze_balance", owner, unfreeze_balance, resource))
        return FakeBuilder("unfreeze", self.calls)

    def delegate_resource(self, owner, receiver, balance, resource="ENERGY", lock=False, lock_period=None):
        self.calls.append(("delegate_resource", owner, receiver, balance, resource, lock, lock_period))
        return FakeBuilder("delegate", self.calls)

    def undelegate_resource(self, owner, receiver, balance, resource="ENERGY"):
        self.calls.append(("undelegate_resource", owner, receiver, balance, resource))
        return FakeBuilder("undelegate", self.calls)


class FakeClient:
    def __init__(self):
        self.trx = FakeTrx()


class StakingServiceTests(TestCase):
    def setUp(self):
        self.primary = PrivateKey(bytes.fromhex("1" * 64))
        self.secondary = PrivateKey(bytes.fromhex("2" * 64))
        self.account = StakingAccount.objects.create(
            name="multi-sig-1",
            address=self.primary.public_key.to_base58check_address(),
            private_key_encrypted=self.primary.hex(),
            multisig_private_keys=self.secondary.hex(),
            permission_id=2,
            required_signature_count=2,
            frozen_balance_sun=10_000_000,
            max_delegable_sun=8_000_000,
            delegated_balance_sun=0,
            max_energy=100_000,
            used_energy=0,
        )

    def test_multisig_delegate_uses_permission_id_and_multiple_signatures(self):
        client = FakeClient()
        service = TronStakingService(client=client)
        result = service.delegate_resource(
            self.account,
            receiver_address="TReceiverAddressxxxxx",
            balance_sun=3_000_000,
            energy_amount=32_000,
            order_no="E1001",
            broadcast=True,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["permission_id"], 2)
        self.assertEqual(result["signature_count"], 2)
        self.assertEqual(client.trx.calls[0], ("delegate_resource", self.account.address, "TReceiverAddressxxxxx", 3_000_000, "ENERGY", False, None))
        self.account.refresh_from_db()
        self.assertEqual(self.account.delegated_balance_sun, 3_000_000)
        self.assertEqual(self.account.used_energy, 32_000)

    def test_delegate_energy_order_creates_staking_order_and_updates_energy_order(self):
        order = EnergyOrder.objects.create(
            order_no="E1002",
            receiver_address="TReceiverAddressyyyyy",
            energy_amount=32_000,
            trx_amount=Decimal("3"),
            status="paid",
        )
        client = FakeClient()
        service = TronStakingService(client=client)

        result = service.delegate_energy_order(order, broadcast=True)

        self.assertTrue(result["ok"])
        order.refresh_from_db()
        self.assertEqual(order.status, "success")
        self.assertEqual(order.platform_order_id, "staking:E1002")
        staking_order = StakingOrder.objects.get(order_no="E1002")
        self.assertEqual(staking_order.account, self.account)
        self.assertEqual(staking_order.status, "success")
        self.assertIsNotNone(staking_order.expire_at)
        self.assertEqual(staking_order.delegate_balance_sun, 3_000_000)

    def test_reclaim_order_rejects_pending_delegate(self):
        staking_order = StakingOrder.objects.create(
            order_no="E1002P",
            account=self.account,
            receiver_address="TReceiverAddresspending",
            energy_amount=32_000,
            delegate_balance_sun=3_000_000,
            status="pending",
        )

        with self.assertRaisesMessage(ValueError, "只有已委托成功"):
            TronStakingService(client=FakeClient()).reclaim_order(staking_order, broadcast=True)

    def test_reclaim_order_undelegates_and_releases_inventory(self):
        staking_order = StakingOrder.objects.create(
            order_no="E1003",
            account=self.account,
            receiver_address="TReceiverAddresszzzzz",
            energy_amount=32_000,
            delegate_balance_sun=3_000_000,
            status="success",
        )
        self.account.delegated_balance_sun = 3_000_000
        self.account.used_energy = 32_000
        self.account.save(update_fields=["delegated_balance_sun", "used_energy"])

        result = TronStakingService(client=FakeClient()).reclaim_order(staking_order, broadcast=True)

        self.assertTrue(result["ok"])
        staking_order.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(staking_order.status, "reclaimed")
        self.assertEqual(self.account.delegated_balance_sun, 0)
        self.assertEqual(self.account.used_energy, 0)

    def test_dry_run_delegate_does_not_consume_inventory_or_mark_order_delegating(self):
        order = EnergyOrder.objects.create(
            order_no="E1004",
            receiver_address="TReceiverAddressdryrun",
            energy_amount=32_000,
            trx_amount=Decimal("3"),
            status="paid",
        )

        result = TronStakingService(client=FakeClient()).delegate_energy_order(order, broadcast=False)

        self.assertTrue(result["ok"])
        self.account.refresh_from_db()
        order.refresh_from_db()
        staking_order = StakingOrder.objects.get(order_no="E1004")
        self.assertEqual(self.account.delegated_balance_sun, 0)
        self.assertEqual(self.account.used_energy, 0)
        self.assertEqual(order.status, "paid")
        self.assertEqual(staking_order.status, "pending")
        self.assertEqual(staking_order.delegate_txid, result["txid"])

    def test_reclaim_due_orders_only_reclaims_success_expired_auto_reclaim_orders(self):
        from django.utils import timezone
        from datetime import timedelta

        due_order = StakingOrder.objects.create(
            order_no="E1005",
            account=self.account,
            receiver_address="TReceiverAddressdue",
            energy_amount=32_000,
            delegate_balance_sun=3_000_000,
            status="success",
            expire_at=timezone.now() - timedelta(minutes=1),
        )
        StakingOrder.objects.create(
            order_no="E1006",
            account=self.account,
            receiver_address="TReceiverAddressfuture",
            energy_amount=32_000,
            delegate_balance_sun=3_000_000,
            status="success",
            expire_at=timezone.now() + timedelta(hours=1),
        )
        self.account.delegated_balance_sun = 6_000_000
        self.account.used_energy = 64_000
        self.account.save(update_fields=["delegated_balance_sun", "used_energy"])

        result = TronStakingService(client=FakeClient()).reclaim_due_orders(broadcast=True)

        self.assertEqual(result["total"], 1)
        due_order.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(due_order.status, "reclaimed")
        self.assertEqual(self.account.delegated_balance_sun, 3_000_000)
        self.assertEqual(self.account.used_energy, 32_000)
