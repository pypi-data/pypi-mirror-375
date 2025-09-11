from __future__ import annotations

import asyncio
from typing import Dict, List

from ..infra.event_bus import EventBus
from ..models.orderbook import TopOfBook
from .models import Order, OrderRequest, OrderType, Side, TimeInForce


class PaperBroker:
    """Simple paper broker: fills orders at top-of-book.

    - MARKET: immediate full fill at best price.
    - LIMIT: fill if crossing/top satisfies; IOC/FOK cancel if not immediately fillable; GTC stays pending and fills when market crosses.
    """

    def __init__(self, bus: EventBus, oms, *, monitor_interval: float = 0.0):
        self.bus = bus
        self.oms = oms
        self._top: Dict[str, TopOfBook] = {}
        self._pending: Dict[str, Order] = {}
        self._tasks: List[asyncio.Task] = []
        self._monitor_interval = monitor_interval

    async def start(self) -> None:
        sub = await self.bus.subscribe("md.top")
        self._tasks.append(asyncio.create_task(self._on_top(sub), name="paper-top"))
        if self._monitor_interval > 0:
            self._tasks.append(asyncio.create_task(self._monitor(), name="paper-monitor"))

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def place(self, order: Order) -> Order:
        top = self._top.get(order.symbol)
        if order.type == OrderType.MARKET:
            if top:
                px = top.ask_px if order.side == Side.BUY else top.bid_px
                await self.oms.update_fill(order.client_id, order.qty, px)
            else:
                # no top-of-book yet; leave pending until we receive one
                self._pending[order.client_id] = order
            return self.oms.get(order.client_id)
        else:
            # LIMIT
            if top and self._can_fill_limit(order, top):
                px = top.ask_px if order.side == Side.BUY else top.bid_px
                await self.oms.update_fill(order.client_id, order.qty, px)
                return self.oms.get(order.client_id)
            # not fillable now
            if order.tif in (TimeInForce.IOC, TimeInForce.FOK):
                await self.oms.cancel(order.client_id)
            else:
                self._pending[order.client_id] = order
            return self.oms.get(order.client_id)

    async def cancel(self, client_id: str):
        self._pending.pop(client_id, None)
        return await self.oms.cancel(client_id)

    def _can_fill_limit(self, order: Order, top: TopOfBook) -> bool:
        if order.side == Side.BUY:
            return order.price is not None and top.ask_px <= order.price
        else:
            return order.price is not None and top.bid_px >= order.price

    async def _on_top(self, sub):
        async for evt in sub:
            if evt is StopAsyncIteration:
                break
            top: TopOfBook = evt.payload
            self._top[top.symbol] = top
            # try to fill any pending orders for this symbol
            to_fill = [o for o in list(self._pending.values()) if o.symbol == top.symbol]
            for o in to_fill:
                if o.type == OrderType.MARKET or self._can_fill_limit(o, top):
                    px = top.ask_px if o.side == Side.BUY else top.bid_px
                    await self.oms.update_fill(o.client_id, o.qty, px, ts=top.ts)
                    self._pending.pop(o.client_id, None)

    async def _monitor(self):
        while True:
            await asyncio.sleep(self._monitor_interval)
            # could implement timeouts or other policies later
            pass

