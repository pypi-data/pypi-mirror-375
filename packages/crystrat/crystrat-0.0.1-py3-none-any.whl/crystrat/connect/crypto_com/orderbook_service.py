from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Dict, Iterable, List, Optional, Tuple

import aiohttp

from .constants import REST_BASE, WS_MARKET, to_instrument
from ...models.orderbook import L2Book, TopOfBook
from ...infra.event_bus import EventBus
from ...infra.metrics import METRICS


log = logging.getLogger(__name__)


class _BookState:
    __slots__ = ("bids", "asks")

    def __init__(self):
        self.bids: Dict[float, float] = {}
        self.asks: Dict[float, float] = {}


class CryptoComOrderBook:
    """Maintains L2 orderbooks for instruments using REST snapshot + WS diffs.

    Publishes:
    - md.book: L2Book
    - md.top: TopOfBook
    """

    def __init__(self, symbols: Iterable[str], bus: EventBus, *, depth: int = 50, reconnect_delay: float = 3.0):
        self.instruments: List[str] = [to_instrument(s) for s in symbols]
        self.bus = bus
        self.depth = depth
        self.reconnect_delay = reconnect_delay
        self._stop = asyncio.Event()
        self._session: Optional[aiohttp.ClientSession] = None
        self._books: Dict[str, _BookState] = {ins: _BookState() for ins in self.instruments}
        self._last_ts: Dict[str, float] = {ins: 0.0 for ins in self.instruments}
        self._tasks: list[asyncio.Task] = []
        self._stale_sec = 15.0

    async def start(self) -> None:
        self._stop.clear()
        self._session = aiohttp.ClientSession()
        # Snapshot bootstrap
        await self._bootstrap_snapshots()
        # Start stale monitor
        self._tasks.append(asyncio.create_task(self._monitor_stale(), name="ob-stale"))
        # WS loop
        while not self._stop.is_set():
            try:
                await self._run_ws()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.warning("OrderBook WS error; reconnecting", exc_info=e)
                await asyncio.sleep(self.reconnect_delay)
                await self._bootstrap_snapshots()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self._cleanup()

    async def stop(self) -> None:
        self._stop.set()

    async def _cleanup(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _bootstrap_snapshots(self) -> None:
        assert self._session is not None
        timeout = aiohttp.ClientTimeout(total=10)
        for ins in self.instruments:
            url = f"{REST_BASE}/public/get-book"
            params = {"instrument_name": ins, "depth": max(10, self.depth)}
            try:
                async with self._session.get(url, params=params, timeout=timeout) as r:
                    r.raise_for_status()
                    data = await r.json()
            except Exception:
                log.warning("Failed snapshot fetch", extra={"instrument": ins})
                continue
            try:
                items = (data.get("result") or {}).get("data") or []
                if not items:
                    continue
                book = items[0]
                bids = book.get("bids", [])
                asks = book.get("asks", [])
                st = self._books[ins]
                st.bids.clear(); st.asks.clear()
                for p, q, *_ in bids:
                    pf, qf = float(p), float(q)
                    if qf > 0:
                        st.bids[pf] = qf
                for p, q, *_ in asks:
                    pf, qf = float(p), float(q)
                    if qf > 0:
                        st.asks[pf] = qf
                await METRICS.inc("book_snapshots", 1)
                await self._publish(ins, time.time())
            except Exception as e:
                log.debug("Snapshot parse failed", exc_info=e)

    async def _run_ws(self) -> None:
        assert self._session is not None
        timeout = aiohttp.ClientTimeout(total=None, sock_read=60)
        async with self._session.ws_connect(WS_MARKET, heartbeat=20, timeout=timeout) as ws:
            log.info("Connected to Crypto.com market WS (book)")
            channels = [f"book.{ins}" for ins in self.instruments]
            sub_msg = {"id": 2, "method": "subscribe", "params": {"channels": channels}}
            await ws.send_json(sub_msg)
            log.info("Subscribed", extra={"channels": channels})

            async for msg in ws:
                if self._stop.is_set():
                    break
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(msg.json())
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.error("OrderBook WebSocket error: %s", msg.data)
                    break
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                    break

    async def _handle_message(self, data):
        try:
            if not isinstance(data, dict):
                return
            params = data.get("params") or data.get("result")
            if not params:
                return
            channel = params.get("channel")
            if not channel or not channel.startswith("book."):
                return
            ins = channel.split(".", 1)[1]
            items = params.get("data") or []
            for item in items:
                await self._apply_update(ins, item)
        except Exception as e:
            log.debug("Failed to handle book message", exc_info=e)

    async def _apply_update(self, ins: str, item) -> None:
        st = self._books.get(ins)
        if not st:
            return
        bids = item.get("bids") or []
        asks = item.get("asks") or []
        ts_ms = item.get("t") or item.get("ts")
        ts = (float(ts_ms) / 1000.0) if ts_ms else time.time()
        # Upsert levels. If size==0 -> delete.
        for p, q, *_ in bids:
            pf, qf = float(p), float(q)
            if qf <= 0:
                st.bids.pop(pf, None)
            else:
                st.bids[pf] = qf
        for p, q, *_ in asks:
            pf, qf = float(p), float(q)
            if qf <= 0:
                st.asks.pop(pf, None)
            else:
                st.asks[pf] = qf
        self._last_ts[ins] = ts
        await METRICS.inc("book_updates", 1)
        # Optional checksum check if provided by server
        cs = item.get("checksum") or item.get("cs")
        if cs is not None:
            try:
                if int(cs) != self._calc_checksum(st):
                    log.warning("Orderbook checksum mismatch; resyncing", extra={"instrument": ins})
                    await METRICS.inc("book_checksum_mismatch", 1)
                    await self._fetch_snapshot(ins)
            except Exception:
                pass
        await self._publish(ins, ts)

    def _calc_checksum(self, st: _BookState, depth: int = 10) -> int:
        import zlib
        bids = sorted(st.bids.items(), key=lambda x: x[0], reverse=True)[:depth]
        asks = sorted(st.asks.items(), key=lambda x: x[0])[:depth]
        parts: list[str] = []
        # Interleave bid/ask like b0,a0,b1,a1,... (best practice for CRC across sides)
        for i in range(max(len(bids), len(asks))):
            if i < len(bids):
                parts.append(f"{bids[i][0]}:{bids[i][1]}")
            if i < len(asks):
                parts.append(f"{asks[i][0]}:{asks[i][1]}")
        payload = "|".join(parts).encode()
        return zlib.crc32(payload) & 0xFFFFFFFF

    async def _fetch_snapshot(self, ins: str) -> None:
        assert self._session is not None
        url = f"{REST_BASE}/public/get-book"
        params = {"instrument_name": ins, "depth": max(10, self.depth)}
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with self._session.get(url, params=params, timeout=timeout) as r:
                r.raise_for_status()
                data = await r.json()
        except Exception:
            log.warning("Failed per-instrument snapshot fetch", extra={"instrument": ins})
            return
        items = (data.get("result") or {}).get("data") or []
        if not items:
            return
        book = items[0]
        st = self._books[ins]
        st.bids.clear(); st.asks.clear()
        for p, q, *_ in (book.get("bids") or []):
            pf, qf = float(p), float(q)
            if qf > 0:
                st.bids[pf] = qf
        for p, q, *_ in (book.get("asks") or []):
            pf, qf = float(p), float(q)
            if qf > 0:
                st.asks[pf] = qf
        await METRICS.inc("book_resyncs", 1)
        await self._publish(ins, time.time())

    async def _monitor_stale(self) -> None:
        while not self._stop.is_set():
            await asyncio.sleep(5)
            now = time.time()
            for ins in list(self.instruments):
                last = self._last_ts.get(ins, 0.0)
                if last and now - last > self._stale_sec:
                    log.warning("Orderbook stale; resyncing", extra={"instrument": ins, "age": now - last})
                    await METRICS.inc("book_stale_resync", 1)
                    await self._fetch_snapshot(ins)

    async def _publish(self, ins: str, ts: float) -> None:
        st = self._books[ins]
        bids_sorted = sorted(st.bids.items(), key=lambda x: x[0], reverse=True)[: self.depth]
        asks_sorted = sorted(st.asks.items(), key=lambda x: x[0])[: self.depth]
        symbol = ins.replace("_", "")
        book = L2Book(symbol=symbol, ts=ts, bids=bids_sorted, asks=asks_sorted)
        await self.bus.publish("md.book", book)
        if bids_sorted and asks_sorted:
            bb = bids_sorted[0]
            ba = asks_sorted[0]
            top = TopOfBook(symbol=symbol, ts=ts, bid_px=bb[0], bid_sz=bb[1], ask_px=ba[0], ask_sz=ba[1])
            await self.bus.publish("md.top", top)
