from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from ..infra.event_bus import EventBus
from ..infra.config import AppConfig
from ..connect.crypto_com.ws_market import CryptoComMarketWS
from ..connect.crypto_com.orderbook_service import CryptoComOrderBook
from .ohlcv import OhlcvAggregator
from ..infra.metrics import METRICS


log = logging.getLogger(__name__)


class MarketDataRuntime:
    """Wires selected exchange market data sources to the event bus."""

    def __init__(self, cfg: AppConfig, bus: EventBus):
        self.cfg = cfg
        self.bus = bus
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        if any(e.lower() in {"cryptocom", "crypto_com", "crypto.com"} for e in self.cfg.exchanges):
            md = CryptoComMarketWS(symbols=self.cfg.symbols, bus=self.bus)
            self._tasks.append(asyncio.create_task(md.start(), name="cryptocom-md"))
            ob = CryptoComOrderBook(symbols=self.cfg.symbols, bus=self.bus, depth=self.cfg.book_depth)
            self._tasks.append(asyncio.create_task(ob.start(), name="cryptocom-ob"))
        if not self._tasks:
            log.info("No market data sources configured")
        # OHLCV aggregator from trade ticks
        if self.cfg.bar_intervals:
            agg = OhlcvAggregator(self.bus, self.cfg.symbols, self.cfg.bar_intervals)
            self._tasks.append(asyncio.create_task(agg.start(), name="ohlcv-agg"))
        # Periodic metrics log
        self._tasks.append(asyncio.create_task(self._log_metrics_task(), name="metrics-log"))

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _log_metrics_task(self) -> None:
        import logging
        log = logging.getLogger(__name__)
        while True:
            await asyncio.sleep(30)
            snap = await METRICS.snapshot()
            # include bus drop counter
            snap["bus_dropped"] = getattr(self.bus, "dropped", 0)
            log.info("Metrics", extra=snap)
