from __future__ import annotations

from typing import Any


class Strategy:
    """Lean Strategy base class with simple event handlers.

    Subclasses should override the handlers they care about. Helpers like
    `buy`, `sell`, and `bracket` are provided as stubs for now.
    """

    def on_start(self, ctx: Any) -> None:
        pass

    def on_tick(self, event: Any) -> None:
        pass

    def on_bar(self, bar: Any) -> None:
        pass

    def on_order(self, event: Any) -> None:
        pass

    def on_risk(self, event: Any) -> None:
        pass

    def on_stop(self) -> None:
        pass

    # --- order helpers (stubs) ---
    def buy(self, symbol: str, qty: float, **kwargs) -> None:  # noqa: D401
        raise NotImplementedError("Order helpers will be wired in M2")

    def sell(self, symbol: str, qty: float, **kwargs) -> None:
        raise NotImplementedError("Order helpers will be wired in M2")

    def bracket(self, symbol: str, qty: float, entry: float, sl: float, tp: float, **kwargs) -> None:
        raise NotImplementedError("Bracket orders will arrive in M7 milestone")

