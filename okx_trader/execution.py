from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

import aiohttp


@dataclass
class OrderRequest:
    instrument_id: str
    side: str
    size: Decimal
    price: Optional[Decimal] = None
    order_type: str = "limit"


class OkxRestClient:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        passphrase: str,
        base_url: str,
        proxy: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = base_url.rstrip("/")
        self.proxy = proxy

    def _sign(self, timestamp: str, method: str, path: str, body: str) -> str:
        message = f"{timestamp}{method}{path}{body}".encode()
        secret = self.secret_key.encode()
        signature = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    async def _request(self, method: str, path: str, payload: Optional[Dict] = None) -> Dict:
        body = json.dumps(payload or {})
        timestamp = str(int(aiohttp.helpers.utcnow().timestamp()))
        signature = self._sign(timestamp, method, path, body)
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                data=body,
                headers=headers,
                proxy=self.proxy,
            ) as resp:
                return await resp.json()

    async def get_positions(self, instrument_type: str = "SWAP") -> Dict:
        path = f"/api/v5/account/positions?instType={instrument_type}"
        return await self._request("GET", path)

    async def get_latest_ticker(self, instrument_id: str) -> Dict:
        path = f"/api/v5/market/ticker?instId={instrument_id}"
        return await self._request("GET", path)

    async def place_order(self, order: OrderRequest) -> Dict:
        payload = {
            "instId": order.instrument_id,
            "tdMode": "cross",
            "side": order.side,
            "ordType": order.order_type,
            "sz": str(order.size),
        }
        if order.price is not None:
            payload["px"] = str(order.price)
        return await self._request("POST", "/api/v5/trade/order", payload)


class ExecutionEngine:
    def __init__(self, client: OkxRestClient, dry_run: bool = True) -> None:
        self.client = client
        self.dry_run = dry_run

    async def execute(self, order: OrderRequest) -> Dict:
        if self.dry_run:
            return {
                "dry_run": True,
                "order": {
                    "instId": order.instrument_id,
                    "side": order.side,
                    "sz": str(order.size),
                    "px": str(order.price) if order.price is not None else None,
                },
            }
        return await self.client.place_order(order)
