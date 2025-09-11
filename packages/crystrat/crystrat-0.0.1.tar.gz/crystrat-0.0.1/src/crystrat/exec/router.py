from __future__ import annotations

import asyncio
from typing import Optional

from ..infra.event_bus import EventBus
from ..infra.metrics import METRICS
from ..infra.config import AppConfig
from .models import OrderRequest, OrderStatus
from .local_oms import LocalOMS
from .paper_broker import PaperBroker
from .risk import RiskEngine, RiskLimits


class ExecRouter:
    def __init__(self, cfg: AppConfig, bus: EventBus):
        self.cfg = cfg
        self.bus = bus
        self.oms = LocalOMS(bus)
        self.risk = RiskEngine(
            RiskLimits(
                max_order_notional=None,
                max_qty_per_order=None,
            )
        )
        self._broker = PaperBroker(bus, self.oms)
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        await self._broker.start()

    async def stop(self) -> None:
        await self._broker.stop()

    async def submit(self, req: OrderRequest):
        # Create local order (idempotent)
        order = await self.oms.create(req)
        # Risk check using best available price (PaperBroker holds top-of-book)
        ref_price = None
        ok, reason = self.risk.check(req, ref_price)
        if not ok:
            order.status = OrderStatus.REJECTED
            await self.bus.publish("exec.order", order)
            await METRICS.inc("order_rejected", 1)
            return order
        # Route to paper broker for now (live routing can be plugged later)
        await METRICS.inc("order_submitted", 1)
        return await self._broker.place(order)

    async def cancel(self, client_id: str):
        await METRICS.inc("order_cancel", 1)
        return await self._broker.cancel(client_id)

