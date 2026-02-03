from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from .features import FeatureSnapshot
from .orderbook import OrderBook


@dataclass
class OrderSignal:
    side: str
    size: Decimal
    price: Decimal
    reason: str


class StrategyEngine:
    def __init__(
        self,
        enable_liquidation_hunting: bool,
        enable_funding_arbitrage: bool,
        enable_market_making: bool,
    ) -> None:
        self.enable_liquidation_hunting = enable_liquidation_hunting
        self.enable_funding_arbitrage = enable_funding_arbitrage
        self.enable_market_making = enable_market_making

    def generate_signals(self, orderbook: OrderBook, features: FeatureSnapshot) -> List[OrderSignal]:
        signals: List[OrderSignal] = []
        bids, asks = orderbook.top_levels()
        if not bids or not asks:
            return signals
        best_bid_price, _ = bids[0]
        best_ask_price, _ = asks[0]
        mid_price = (best_bid_price + best_ask_price) / 2

        if self.enable_liquidation_hunting and abs(features.ofi) > Decimal("50"):
            side = "buy" if features.ofi > 0 else "sell"
            signals.append(
                OrderSignal(
                    side=side,
                    size=Decimal("1"),
                    price=mid_price,
                    reason="liquidation_hunting",
                )
            )

        if self.enable_market_making:
            spread = best_ask_price - best_bid_price
            if spread > Decimal("0"):
                signals.append(
                    OrderSignal(
                        side="buy",
                        size=Decimal("0.5"),
                        price=best_bid_price,
                        reason="market_making_bid",
                    )
                )
                signals.append(
                    OrderSignal(
                        side="sell",
                        size=Decimal("0.5"),
                        price=best_ask_price,
                        reason="market_making_ask",
                    )
                )

        if self.enable_funding_arbitrage and features.wmp > Decimal("0"):
            signals.append(
                OrderSignal(
                    side="buy",
                    size=Decimal("0.3"),
                    price=best_bid_price,
                    reason="funding_arbitrage",
                )
            )

        return signals
