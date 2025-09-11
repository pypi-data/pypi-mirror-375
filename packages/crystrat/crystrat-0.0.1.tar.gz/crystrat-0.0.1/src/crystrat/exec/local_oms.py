from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional

from ..infra.event_bus import EventBus
from .models import Order, OrderRequest, OrderStatus, Fill


class LocalOMS:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self._orders: Dict[str, Order] = {}
        self._counter = 0

    def next_client_id(self) -> str:
        self._counter += 1
        return f"cid-{int(time.time()*1000)}-{self._counter}"

    async def create(self, req: OrderRequest) -> Order:
        cid = req.client_id or self.next_client_id()
        if cid in self._orders:
            # idempotent return existing
            return self._orders[cid]
        order = Order(
            symbol=req.symbol.replace("-", "").upper(),
            side=req.side,
            type=req.type,
            qty=req.qty,
            tif=req.tif,
            client_id=cid,
            price=req.price,
        )
        self._orders[cid] = order
        await self.bus.publish("exec.order", order)
        return order

    async def update_fill(self, cid: str, qty: float, price: float, ts: float | None = None) -> Order:
        o = self._orders[cid]
        prev = o.filled_qty
        new_filled = prev + qty
        # new avg price
        if new_filled > 0:
            o.avg_px = (o.avg_px * prev + price * qty) / new_filled
        o.filled_qty = new_filled
        o.status = OrderStatus.FILLED if abs(o.filled_qty - o.qty) < 1e-12 else OrderStatus.PARTIALLY_FILLED
        await self.bus.publish("exec.fill", Fill(client_id=cid, symbol=o.symbol, qty=qty, price=price, ts=ts or time.time()))
        await self.bus.publish("exec.order", o)
        return o

    async def cancel(self, cid: str) -> Optional[Order]:
        o = self._orders.get(cid)
        if not o:
            return None
        if o.status in (OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED):
            return o
        o.status = OrderStatus.CANCELED
        await self.bus.publish("exec.order", o)
        return o

    def get(self, cid: str) -> Optional[Order]:
        return self._orders.get(cid)

