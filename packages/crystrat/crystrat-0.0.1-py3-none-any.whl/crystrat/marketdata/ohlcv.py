from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import asdict
from typing import Dict, Iterable

from ..infra.event_bus import EventBus
from ..models.base import Tick, Bar
from ..infra.metrics import METRICS


log = logging.getLogger(__name__)


def _parse_tf(tf: str) -> int:
    tf = tf.strip().lower()
    if tf.endswith("ms"):
        # floor to seconds aggregator by treating <1s as 1s
        return 1
    if tf.endswith("s"):
        return int(tf[:-1])
    if tf.endswith("m"):
        return int(tf[:-1]) * 60
    if tf.endswith("h"):
        return int(tf[:-1]) * 3600
    if tf.endswith("d"):
        return int(tf[:-1]) * 86400
    raise ValueError(f"Unsupported timeframe: {tf}")


class OhlcvAggregator:
    """Aggregates trade ticks (md.trade) into OHLCV bars per timeframe.

    Publishes bars on topics: md.bar.<tf>
    """

    def __init__(self, bus: EventBus, symbols: Iterable[str], timeframes: Iterable[str]):
        self.bus = bus
        self.symbols = set(s.replace("-", "").upper() for s in symbols)
        self.frames = {tf: _parse_tf(tf) for tf in timeframes}
        self._tasks: list[asyncio.Task] = []
        # state[(symbol, tf)] -> current Bar
        self._state: Dict[tuple[str, str], Bar] = {}

    async def start(self) -> None:
        sub = await self.bus.subscribe("md.trade")
        self._tasks.append(asyncio.create_task(self._consume(sub), name="ohlcv-consumer"))

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _consume(self, sub) -> None:
        async for evt in sub:
            if evt is StopAsyncIteration:
                break
            tick = evt.payload
            if not isinstance(tick, Tick):
                continue
            sym = tick.symbol.replace("-", "").upper()
            if self.symbols and sym not in self.symbols:
                continue
            for tf, secs in self.frames.items():
                bucket = int(tick.ts) - (int(tick.ts) % secs)
                key = (sym, tf)
                cur = self._state.get(key)
                if cur is None or bucket != int(cur.ts):
                    # flush previous
                    if cur is not None:
                        await self._publish(tf, cur)
                    self._state[key] = Bar(
                        symbol=sym, tf=tf, ts=float(bucket), o=tick.price, h=tick.price,
                        l=tick.price, c=tick.price, v=abs(tick.size), n=1,
                    )
                else:
                    cur.c = tick.price
                    cur.h = max(cur.h, tick.price)
                    cur.l = min(cur.l, tick.price)
                    cur.v += abs(tick.size)
                    cur.n += 1

    async def _publish(self, tf: str, bar: Bar) -> None:
        await self.bus.publish(f"md.bar.{tf}", bar)
        await METRICS.inc("bars_emitted", 1)
