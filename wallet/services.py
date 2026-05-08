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
