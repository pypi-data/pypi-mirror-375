from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Dict


log = logging.getLogger(__name__)


class Metrics:
    def __init__(self):
        self._c = Counter()
        self._lock = asyncio.Lock()

    async def inc(self, name: str, delta: int = 1) -> None:
        async with self._lock:
            self._c[name] += delta

    async def set(self, name: str, value: int) -> None:
        async with self._lock:
            self._c[name] = value

    async def snapshot(self) -> Dict[str, int]:
        async with self._lock:
            return dict(self._c)


METRICS = Metrics()

