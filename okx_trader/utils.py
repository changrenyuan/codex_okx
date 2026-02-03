from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


def to_decimal(value: str | float | int) -> Decimal:
    return Decimal(str(value))


def quantize(value: Decimal, precision: str = "0.00000001") -> Decimal:
    return value.quantize(Decimal(precision), rounding=ROUND_HALF_UP)


def chunks(seq: Iterable, size: int):
    chunk = []
    for item in seq:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
