from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Tuple

from .orderbook import OrderBook


@dataclass
class FeatureSnapshot:
    ofi: Decimal
    wmp: Decimal
    liquidity_vacuum: Decimal
    bid_pressure: Decimal
    ask_pressure: Decimal


class FeatureEngine:
    def __init__(self, depth: int = 25) -> None:
        self.depth = depth
        self._prev_bids: List[Tuple[Decimal, Decimal]] = []
        self._prev_asks: List[Tuple[Decimal, Decimal]] = []

    def compute(self, orderbook: OrderBook) -> FeatureSnapshot:
        bids, asks = orderbook.top_levels()
        bids = bids[: self.depth]
        asks = asks[: self.depth]

        ofi = self._order_flow_imbalance(bids, asks)
        wmp = self._weighted_market_pressure(bids, asks)
        liquidity_vacuum = self._liquidity_vacuum(bids, asks)
        bid_pressure = sum(size for _, size in bids)
        ask_pressure = sum(size for _, size in asks)

        self._prev_bids = bids
        self._prev_asks = asks

        return FeatureSnapshot(
            ofi=ofi,
            wmp=wmp,
            liquidity_vacuum=liquidity_vacuum,
            bid_pressure=bid_pressure,
            ask_pressure=ask_pressure,
        )

    def _order_flow_imbalance(
        self,
        bids: List[Tuple[Decimal, Decimal]],
        asks: List[Tuple[Decimal, Decimal]],
    ) -> Decimal:
        def delta(prev, current):
            prev_map = {price: size for price, size in prev}
            current_map = {price: size for price, size in current}
            total = Decimal("0")
            for price, size in current_map.items():
                total += size - prev_map.get(price, Decimal("0"))
            return total

        bid_delta = delta(self._prev_bids, bids)
        ask_delta = delta(self._prev_asks, asks)
        return bid_delta - ask_delta

    def _weighted_market_pressure(
        self,
        bids: List[Tuple[Decimal, Decimal]],
        asks: List[Tuple[Decimal, Decimal]],
    ) -> Decimal:
        def weighted(side: List[Tuple[Decimal, Decimal]]) -> Decimal:
            total = Decimal("0")
            for idx, (_, size) in enumerate(side, start=1):
                weight = Decimal(str(self.depth - idx + 1)) / Decimal(str(self.depth))
                total += size * weight
            return total

        return weighted(bids) - weighted(asks)

    def _liquidity_vacuum(
        self,
        bids: List[Tuple[Decimal, Decimal]],
        asks: List[Tuple[Decimal, Decimal]],
    ) -> Decimal:
        if not bids or not asks:
            return Decimal("0")
        bid_depth = sum(size for _, size in bids)
        ask_depth = sum(size for _, size in asks)
        if bid_depth + ask_depth == 0:
            return Decimal("0")
        return (bid_depth - ask_depth) / (bid_depth + ask_depth)
