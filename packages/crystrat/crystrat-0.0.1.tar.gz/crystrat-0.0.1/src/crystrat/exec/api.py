from __future__ import annotations

from typing import Optional

from .models import OrderRequest, Side, OrderType, TimeInForce
from .router import ExecRouter


class ExecAPI:
    def __init__(self, router: ExecRouter):
        self.router = router

    async def market(self, symbol: str, side: Side, qty: float, *, client_id: Optional[str] = None):
        req = OrderRequest(symbol=symbol, side=side, type=OrderType.MARKET, qty=qty, client_id=client_id)
        return await self.router.submit(req)

    async def limit(self, symbol: str, side: Side, qty: float, price: float, tif: TimeInForce = TimeInForce.GTC, *, client_id: Optional[str] = None):
        req = OrderRequest(symbol=symbol, side=side, type=OrderType.LIMIT, qty=qty, price=price, tif=tif, client_id=client_id)
        return await self.router.submit(req)

    async def buy(self, symbol: str, qty: float, *, client_id: Optional[str] = None):
        return await self.market(symbol, Side.BUY, qty, client_id=client_id)

    async def sell(self, symbol: str, qty: float, *, client_id: Optional[str] = None):
        return await self.market(symbol, Side.SELL, qty, client_id=client_id)

    async def cancel(self, client_id: str):
        return await self.router.cancel(client_id)

