from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class RiskState:
    daily_loss: Decimal = Decimal("0")
    max_daily_loss: Decimal = Decimal("0.05")
    max_position_size: Decimal = Decimal("1000")
    max_latency_ms: int = 500
    current_position: Decimal = Decimal("0")
    last_latency_ms: Optional[int] = None


class RiskManager:
    def __init__(
        self,
        max_daily_loss: float,
        max_position_size: float,
        max_latency_ms: int,
    ) -> None:
        self.state = RiskState(
            max_daily_loss=Decimal(str(max_daily_loss)),
            max_position_size=Decimal(str(max_position_size)),
            max_latency_ms=max_latency_ms,
        )

    def update_latency(self, latency_ms: int) -> None:
        self.state.last_latency_ms = latency_ms

    def update_pnl(self, daily_loss: Decimal) -> None:
        self.state.daily_loss = daily_loss

    def update_position(self, position: Decimal) -> None:
        self.state.current_position = position

    def is_trading_allowed(self) -> bool:
        if self.state.daily_loss >= self.state.max_daily_loss:
            return False
        if abs(self.state.current_position) >= self.state.max_position_size:
            return False
        if self.state.last_latency_ms is not None and self.state.last_latency_ms > self.state.max_latency_ms:
            return False
        return True
