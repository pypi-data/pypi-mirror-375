from __future__ import annotations

import aiohttp
from typing import Any, Dict, Optional

from .constants import REST_BASE


class CryptoComREST:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._own_session = session is None
        self.session = session or aiohttp.ClientSession()

    async def close(self) -> None:
        if self._own_session:
            await self.session.close()

    async def get_instruments(self) -> Dict[str, Any]:
        url = f"{REST_BASE}/public/get-instruments"
        async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            r.raise_for_status()
            return await r.json()

    async def get_trades(self, instrument_name: str, limit: int = 50) -> Dict[str, Any]:
        url = f"{REST_BASE}/public/get-trades"
        params = {"instrument_name": instrument_name, "limit": limit}
        async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
            r.raise_for_status()
            return await r.json()

    async def get_book(self, instrument_name: str, depth: int = 50) -> Dict[str, Any]:
        url = f"{REST_BASE}/public/get-book"
        params = {"instrument_name": instrument_name, "depth": depth}
        async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
            r.raise_for_status()
            return await r.json()

