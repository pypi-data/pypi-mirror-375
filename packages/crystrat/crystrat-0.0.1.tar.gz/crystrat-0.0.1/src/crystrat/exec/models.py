from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class OrderRequest(BaseModel):
    symbol: str
    side: Side
    type: OrderType
    qty: float = Field(gt=0)
    price: Optional[float] = Field(default=None)
    tif: TimeInForce = TimeInForce.GTC
    client_id: Optional[str] = None
    reduce_only: bool = False
    post_only: bool = False

    @field_validator("price")
    @classmethod
    def _price_positive(cls, v, info):
        if info.data.get("type") == OrderType.LIMIT and (v is None or v <= 0):
            raise ValueError("Limit orders require positive price")
        return v


@dataclass(slots=True)
class Order:
    symbol: str
    side: Side
    type: OrderType
    qty: float
    tif: TimeInForce
    client_id: str
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.NEW
    filled_qty: float = 0.0
    avg_px: float = 0.0


@dataclass(slots=True)
class Fill:
    client_id: str
    symbol: str
    qty: float
    price: float
    ts: float

