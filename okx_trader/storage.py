from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, List
from collections import deque


@dataclass
class StorageManager:
    hot_capacity: int = 1000
    hot_storage: Deque[Any] = field(init=False)

    def __post_init__(self) -> None:
        self.hot_storage = deque(maxlen=self.hot_capacity)

    def write_hot(self, record: Any) -> None:
        self.hot_storage.append({"ts": datetime.utcnow().isoformat(), "data": record})

    def read_hot(self) -> List[Any]:
        return list(self.hot_storage)

    def write_warm(self, record: Any) -> None:
        raise NotImplementedError("Warm storage (Redis) not configured.")

    def write_cold(self, record: Any) -> None:
        raise NotImplementedError("Cold storage (Parquet) not configured.")
