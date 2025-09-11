from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import OrderRequest


@dataclass(slots=True)
class RiskLimits:
    max_order_notional: Optional[float] = None
    max_qty_per_order: Optional[float] = None


class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def check(self, req: OrderRequest, ref_price: Optional[float]) -> tuple[bool, str | None]:
        if req.qty <= 0:
            return False, "qty must be > 0"
        if req.type == req.__class__.model_fields["type"].annotation.LIMIT and (req.price is None or req.price <= 0):
            return False, "limit price required"
        if self.limits.max_qty_per_order is not None and req.qty > self.limits.max_qty_per_order:
            return False, "qty exceeds max_qty_per_order"
        if self.limits.max_order_notional is not None:
            px = req.price if req.price is not None else (ref_price or 0)
            notional = px * req.qty
            if px <= 0 or notional > self.limits.max_order_notional:
                return False, "order notional exceeds limit or price unavailable"
        return True, None

