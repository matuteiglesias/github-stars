from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

def rmsle(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Compute root mean squared logarithmic error.

    Both arrays must be finite and non-negative.
    """
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)

    if true.shape != pred.shape:
        raise ValueError(f"Shape mismatch: {true.shape} != {pred.shape}")
    if not np.isfinite(true).all() or not np.isfinite(pred).all():
        raise ValueError("RMSLE inputs must be finite.")
    if (true < 0).any() or (pred < 0).any():
        raise ValueError("RMSLE inputs must be non-negative.")

    return float(np.sqrt(np.mean(np.square(np.log1p(pred) - np.log1p(true)))))
