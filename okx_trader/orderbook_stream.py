from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Iterable, Optional

import aiohttp

from .orderbook import OrderBook


@dataclass
class OrderBookMessage:
    action: str
    data: Dict


class OrderBookStreamer:
    def __init__(self, instrument_id: str, depth: int = 400, proxy: str | None = None) -> None:
        self.instrument_id = instrument_id
        self.depth = depth
        self.orderbook = OrderBook(instrument_id, depth=depth)
        self.proxy = proxy
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None

    async def connect(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        self._ws = await self._session.ws_connect(
            "wss://ws.okx.com:8443/ws/v5/public",
            heartbeat=20,
            receive_timeout=60,
            proxy=self.proxy,
        )
        await self._subscribe()

    async def _subscribe(self) -> None:
        if not self._ws:
            raise RuntimeError("WebSocket not connected")
        payload = {
            "op": "subscribe",
            "args": [
                {"channel": "books-l2-tbt", "instId": self.instrument_id}
            ],
        }
        await self._ws.send_json(payload)

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()
        if self._session:
            await self._session.close()

    async def stream(self) -> AsyncIterator[OrderBookMessage]:
        if not self._ws:
            raise RuntimeError("WebSocket not connected")
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                action = data.get("action") or data.get("event") or "update"
                yield OrderBookMessage(action=action, data=data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

    def apply_message(self, message: OrderBookMessage) -> None:
        data = message.data.get("data", [])
        if not data:
            return
        payload = data[0]
        bids = payload.get("bids", [])
        asks = payload.get("asks", [])
        if message.action == "snapshot":
            self.orderbook.apply_snapshot(bids, asks)
        else:
            self.orderbook.apply_update(bids, asks)

    async def run_forever(self, handler) -> None:
        await self.connect()
        try:
            async for message in self.stream():
                self.apply_message(message)
                await handler(self.orderbook, message)
        finally:
            await self.close()
