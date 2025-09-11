from __future__ import annotations

import logging
import os
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Configure basic logging. Future: add JSON formatting + structlog/OTel hooks.

    Args:
        level: Logging level name, e.g. "DEBUG", "INFO".
    """
    lvl = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(lvl)
        return

    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

