"""Stable contracts for the consulting analytics case bundle.

Imports are lazy so standard-library audit utilities remain usable before the
optional numerical stack is installed.
"""

from typing import Any

__all__ = ["rmsle", "validate_raw_frame", "validate_submission"]


def __getattr__(name: str) -> Any:
    if name == "rmsle":
        from .metrics import rmsle

        return rmsle
    if name in {"validate_raw_frame", "validate_submission"}:
        from .contracts import validate_raw_frame, validate_submission

        return {"validate_raw_frame": validate_raw_frame, "validate_submission": validate_submission}[name]
    raise AttributeError(name)
