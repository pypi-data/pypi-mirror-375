from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class Tick:
    symbol: str
    ts: float  # epoch seconds
    price: float
    size: float
    raw: Optional[Any] = None


@dataclass(slots=True)
class Bar:
    symbol: str
    tf: str         # timeframe label like "1s", "1m"
    ts: float       # start time (epoch seconds)
    o: float
    h: float
    l: float
    c: float
    v: float
    n: int = 0      # trade count
