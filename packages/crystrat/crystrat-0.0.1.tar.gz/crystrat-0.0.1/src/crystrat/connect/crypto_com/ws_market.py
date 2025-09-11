from __future__ import annotations

import asyncio
import json
import logging
from typing import Iterable, List, Optional

import aiohttp

from .constants import WS_MARKET, CHANNEL_TRADE, to_instrument
from ...infra.event_bus import EventBus
from ...models.base import Tick
from ...infra.metrics import METRICS


log = logging.getLogger(__name__)


class CryptoComMarketWS:
    """Minimal Crypto.com market WebSocket client for trades.

    Subscribes to trade channels and publishes Tick events to the event bus.
    """

    def __init__(self, symbols: Iterable[str], bus: EventBus, *, reconnect_delay: float = 3.0):
        self.instruments: List[str] = [to_instrument(s) for s in symbols]
        self.bus = bus
        self.reconnect_delay = reconnect_delay
        self._stop = asyncio.Event()
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self._stop.clear()
        self._session = aiohttp.ClientSession()
        while not self._stop.is_set():
            try:
                await self._run_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.warning("WS error; reconnecting", exc_info=e)
                await asyncio.sleep(self.reconnect_delay)
        await self._cleanup()

    async def stop(self) -> None:
        self._stop.set()

    async def _cleanup(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _run_once(self) -> None:
        assert self._session is not None
        timeout = aiohttp.ClientTimeout(total=None, sock_read=60)
        async with self._session.ws_connect(WS_MARKET, heartbeat=20, timeout=timeout) as ws:
            log.info("Connected to Crypto.com market WS")
            # Subscribe to trades for instruments
            channels = [f"{CHANNEL_TRADE}.{ins}" for ins in self.instruments]
            sub_msg = {"id": 1, "method": "subscribe", "params": {"channels": channels}}
            await ws.send_str(json.dumps(sub_msg))
            log.info("Subscribed", extra={"channels": channels})

            async for msg in ws:
                if self._stop.is_set():
                    break
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(msg.json(loads=json.loads))
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.error("WebSocket error: %s", msg.data)
                    break
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                    break

    async def _handle_message(self, data):
        # Expect messages like: {"method":"public/subscribe","result":{...}} or trade updates
        try:
            if not isinstance(data, dict):
                return
            # Trade update example: {"method":"public/heartbeat"} or {"method":"subscribe","params":{"channel":"trade.BTC_USDT","data":[...]}}
            params = data.get("params") or data.get("result")
            if not params:
                return
            channel = params.get("channel")
            if not channel or not channel.startswith("trade."):
                return
            ins = channel.split(".", 1)[1]
            # Data can be a list of trades
            trades = params.get("data", [])
            await METRICS.inc("ws_trades_msgs", 1)
            await METRICS.inc("ws_trades_count", len(trades))
            for t in trades:
                price = float(t.get("p") or t.get("price") or 0.0)
                qty = float(t.get("q") or t.get("quantity") or 0.0)
                ts = float((t.get("t") or t.get("timestamp") or 0)) / 1000.0
                if price and qty:
                    tick = Tick(symbol=ins.replace("_", ""), ts=ts, price=price, size=qty, raw=t)
                    await self.bus.publish("md.trade", tick)
        except Exception as e:
            log.debug("Failed to handle message", exc_info=e)
