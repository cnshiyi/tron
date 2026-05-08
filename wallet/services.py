from decimal import Decimal
from django.conf import settings
import httpx

TRC20_USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

class TronGridService:
    def __init__(self):
        self.base_url = "https://api.trongrid.io"
        self.headers = {"TRON-PRO-API-KEY": settings.TRONGRID_API_KEY} if settings.TRONGRID_API_KEY else {}

    def account_overview(self, address: str) -> dict:
        with httpx.Client(timeout=15) as client:
            account = client.get(f"{self.base_url}/v1/accounts/{address}", headers=self.headers).json()
            trc20 = client.get(
                f"{self.base_url}/v1/accounts/{address}/transactions/trc20",
                params={"limit": 20, "only_confirmed": "true"},
                headers=self.headers,
            ).json()
        return {"address": address, "account": account, "trc20_transactions": trc20}

    def normalize_usdt_amount(self, raw_value: str | int) -> Decimal:
        return Decimal(str(raw_value)) / Decimal("1000000")


    def list_trc20_transactions(self, address: str, limit: int = 20) -> list[dict]:
        with httpx.Client(timeout=15) as client:
            data = client.get(
                f"{self.base_url}/v1/accounts/{address}/transactions/trc20",
                params={"limit": limit, "only_confirmed": "true", "contract_address": TRC20_USDT_CONTRACT},
                headers=self.headers,
            ).json()
        return data.get("data", [])

    def parse_usdt_transfer(self, item: dict) -> dict:
        return {
            "txid": item.get("transaction_id") or item.get("txID") or "",
            "from_address": item.get("from") or item.get("from_address") or "",
            "to_address": item.get("to") or item.get("to_address") or "",
            "amount": self.normalize_usdt_amount(item.get("value", 0)),
            "token_type": "usdt",
            "confirmed": True,
            "raw": item,
        }
