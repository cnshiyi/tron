from django.conf import settings

from .models import Withdrawal


class WithdrawalPayoutService:
    """Safe payout adapter. Defaults to dry-run; real signing must be explicitly enabled."""

    def build_payload(self, withdrawal: Withdrawal) -> dict:
        return {
            "to_address": withdrawal.address,
            "amount": str(withdrawal.amount),
            "token_type": withdrawal.token_type,
            "withdrawal_id": withdrawal.id,
            "user_id": withdrawal.user_id,
        }

    def payout(self, withdrawal: Withdrawal, dry_run: bool = True) -> dict:
        payload = self.build_payload(withdrawal)
        if dry_run or not getattr(settings, "WITHDRAWAL_PAYOUT_ENABLED", False):
            return {"ok": True, "dry_run": True, "txid": f"dry-withdrawal-{withdrawal.id}", "payload": payload}

        # Deliberately conservative: real chain signing is only allowed when the operator
        # has explicitly configured the private key strategy. This avoids accidental fund movement.
        private_key = getattr(settings, "WITHDRAWAL_PRIVATE_KEY", "")
        if not private_key:
            return {"ok": False, "error": "WITHDRAWAL_PRIVATE_KEY is required for real payout", "payload": payload}

        # Real TRX/TRC20 signing should be wired here after confirming hot-wallet policy,
        # address whitelist and multi-signature requirements.
        return {"ok": False, "error": "real payout signing is not enabled in this scaffold", "payload": payload}
