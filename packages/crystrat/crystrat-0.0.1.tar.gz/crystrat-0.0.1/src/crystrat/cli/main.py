from __future__ import annotations

import argparse
import asyncio
import logging
import signal
from typing import Optional

from ..infra.config import load_config
from ..infra.logging import setup_logging
from ..infra.event_bus import EventBus
from ..strategy.loader import load_strategy
from ..marketdata.runtime import MarketDataRuntime
from ..exec.router import ExecRouter
from ..exec.api import ExecAPI


log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crystrat", description="Crystrat CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run live/paper/backtest runtime")
    p_run.add_argument("--config", required=True, help="Path to YAML config")
    p_run.add_argument("--strategy", required=True, help="Dotted path: module:Class")

    p_status = sub.add_parser("status", help="Show environment status")

    return parser


async def _run_async(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    setup_logging(cfg.log_level)
    log.info("Loaded config", extra={"mode": cfg.mode, "exchanges": cfg.exchanges, "symbols": cfg.symbols})

    bus = EventBus()
    strat_cls = load_strategy(args.strategy)
    strat = strat_cls()

    # In M1+, the runtime will wire market data and order routing here.
    router = ExecRouter(cfg, bus)
    await router.start()
    strat.on_start({"bus": bus, "config": cfg, "exec": ExecAPI(router)})

    md = MarketDataRuntime(cfg, bus)
    await md.start()

    stop_event = asyncio.Event()

    def _graceful(*_):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _graceful)
        except NotImplementedError:
            # Windows may not support add_signal_handler for SIGTERM
            pass

    log.info("Runtime started; press Ctrl+C to exit")
    await stop_event.wait()
    log.info("Shutting down...")
    await md.stop()
    await router.stop()
    await bus.close()
    # Final metrics snapshot on shutdown
    try:
        from ..infra.metrics import METRICS
        snap = await METRICS.snapshot()
        snap["bus_dropped"] = getattr(bus, "dropped", 0)
        log.info("Final metrics", extra=snap)
    except Exception:
        pass
    strat.on_stop()
    return 0


def _status_cmd() -> int:
    setup_logging("INFO")
    import platform
    from .. import __version__

    log.info("Crystrat status", extra={
        "version": __version__,
        "python": platform.python_version(),
        "system": platform.system(),
    })
    print(f"Crystrat v{__version__}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "status":
        return _status_cmd()
    if args.cmd == "run":
        return asyncio.run(_run_async(args))
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
