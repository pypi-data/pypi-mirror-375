from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


class AppConfig(BaseModel):
    mode: Literal["live", "paper", "backtest"] = Field(default="paper")
    exchanges: List[str] = Field(default_factory=list)
    symbols: List[str] = Field(default_factory=list)
    log_level: str = Field(default="INFO")
    bar_intervals: List[str] = Field(default_factory=list)
    book_depth: int = Field(default=50)


def load_config(path: str | Path) -> AppConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    try:
        return AppConfig.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid configuration: {e}")
