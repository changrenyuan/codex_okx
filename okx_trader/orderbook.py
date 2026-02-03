from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple
import zlib

from .utils import to_decimal


@dataclass
class BookSide:
    side: str
    levels: Dict[Decimal, Decimal] = field(default_factory=dict)
    depth: int = 400

    def update(self, price: Decimal, size: Decimal) -> None:
        if size == 0:
            self.levels.pop(price, None)
        else:
            self.levels[price] = size

    def top_levels(self) -> List[Tuple[Decimal, Decimal]]:
        if self.side == "bids":
            sorted_prices = sorted(self.levels.keys(), reverse=True)
        else:
            sorted_prices = sorted(self.levels.keys())
        trimmed = sorted_prices[: self.depth]
        return [(price, self.levels[price]) for price in trimmed]


@dataclass
class OrderBook:
    instrument_id: str
    depth: int = 400
    bids: BookSide = field(init=False)
    asks: BookSide = field(init=False)

    def __post_init__(self) -> None:
        self.bids = BookSide("bids", depth=self.depth)
        self.asks = BookSide("asks", depth=self.depth)

    def apply_snapshot(self, bids: Iterable[Iterable[str]], asks: Iterable[Iterable[str]]) -> None:
        self.bids.levels.clear()
        self.asks.levels.clear()
        for price, size, *_ in bids:
            self.bids.update(to_decimal(price), to_decimal(size))
        for price, size, *_ in asks:
            self.asks.update(to_decimal(price), to_decimal(size))

    def apply_update(self, bids: Iterable[Iterable[str]], asks: Iterable[Iterable[str]]) -> None:
        for price, size, *_ in bids:
            self.bids.update(to_decimal(price), to_decimal(size))
        for price, size, *_ in asks:
            self.asks.update(to_decimal(price), to_decimal(size))

    def top_levels(self) -> Tuple[List[Tuple[Decimal, Decimal]], List[Tuple[Decimal, Decimal]]]:
        return self.bids.top_levels(), self.asks.top_levels()

    def checksum(self, depth: int = 25) -> int:
        bids = self.bids.top_levels()[:depth]
        asks = self.asks.top_levels()[:depth]
        checksum_str = ":".join(
            [
                *[f"{price}:{size}" for price, size in bids],
                *[f"{price}:{size}" for price, size in asks],
            ]
        )
        return zlib.crc32(checksum_str.encode())
