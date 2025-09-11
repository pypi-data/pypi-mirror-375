from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(slots=True)
class L2Book:
    symbol: str
    ts: float  # epoch seconds
    bids: List[Tuple[float, float]]  # sorted desc by price
    asks: List[Tuple[float, float]]  # sorted asc by price


@dataclass(slots=True)
class TopOfBook:
    symbol: str
    ts: float
    bid_px: float
    bid_sz: float
    ask_px: float
    ask_sz: float

