from __future__ import annotations

import importlib
from typing import Type

from .base import Strategy


def load_strategy(dotted: str) -> Type[Strategy]:
    """Load a Strategy subclass from a `module:Class` dotted path.

    Example: "examples.simple_strategy:MyStrat"
    """
    if ":" not in dotted:
        raise ValueError("Strategy must be in 'module:Class' format")
    mod_name, cls_name = dotted.split(":", 1)
    mod = importlib.import_module(mod_name)
    try:
        cls = getattr(mod, cls_name)
    except AttributeError as e:
        raise ImportError(f"Strategy class '{cls_name}' not found in '{mod_name}'") from e
    if not issubclass(cls, Strategy):
        raise TypeError(f"{cls} is not a Strategy subclass")
    return cls

