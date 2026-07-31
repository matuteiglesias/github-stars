from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

EXPECTED_TARGET = "Stars"
EXPECTED_SUBMISSION_COLUMNS = ["Name", "Stars"]

def validate_raw_frame(
    frame: pd.DataFrame,
    *,
    require_target: bool,
    required_identity_columns: tuple[str, ...] = ("Name",),
) -> dict[str, Any]:
    """Validate minimum raw-frame contracts without mutating the input."""
    missing_identity = [
        column for column in required_identity_columns if column not in frame.columns
    ]
    duplicate_columns = frame.columns[frame.columns.duplicated()].tolist()

    target_present = EXPECTED_TARGET in frame.columns
    target_contract_ok = target_present if require_target else True

    target_non_negative = None
    target_finite = None
    if target_present:
        target_numeric = pd.to_numeric(frame[EXPECTED_TARGET], errors="coerce")
        target_non_negative = bool((target_numeric.dropna() >= 0).all())
        target_finite = bool(np.isfinite(target_numeric.dropna()).all())

    valid = (
        not missing_identity
        and not duplicate_columns
        and target_contract_ok
        and target_non_negative is not False
        and target_finite is not False
    )

    return {
        "valid": bool(valid),
        "row_count": int(len(frame)),
        "column_count": int(frame.shape[1]),
        "missing_identity_columns": missing_identity,
        "duplicate_columns": duplicate_columns,
        "target_present": target_present,
        "target_required": require_target,
        "target_non_negative": target_non_negative,
        "target_finite": target_finite,
    }

def validate_submission(
    submission: pd.DataFrame,
    prediction_frame: pd.DataFrame,
) -> dict[str, Any]:
    """Validate exact challenge output and preservation of prediction-row order."""
    columns_exact = list(submission.columns) == EXPECTED_SUBMISSION_COLUMNS
    row_count_matches = len(submission) == len(prediction_frame)

    no_null_predictions = False
    finite_predictions = False
    non_negative = False

    if "Stars" in submission.columns:
        numeric = pd.to_numeric(submission["Stars"], errors="coerce")
        no_null_predictions = bool(numeric.notna().all())
        finite_predictions = bool(np.isfinite(numeric.to_numpy(dtype=float)).all())
        non_negative = bool((numeric >= 0).all())

    name_order_matches = False
    if (
        "Name" in submission.columns
        and "Name" in prediction_frame.columns
        and row_count_matches
    ):
        name_order_matches = bool(
            submission["Name"].reset_index(drop=True).equals(
                prediction_frame["Name"].reset_index(drop=True)
            )
        )

    no_accidental_index = not any(
        str(column).lower().startswith("unnamed:")
        for column in submission.columns
    )

    valid = all(
        [
            columns_exact,
            row_count_matches,
            no_null_predictions,
            finite_predictions,
            non_negative,
            name_order_matches,
            no_accidental_index,
        ]
    )

    return {
        "valid": bool(valid),
        "columns_exact": columns_exact,
        "row_count_matches": row_count_matches,
        "no_null_predictions": no_null_predictions,
        "finite_predictions": finite_predictions,
        "non_negative": non_negative,
        "name_order_matches": name_order_matches,
        "no_accidental_index": no_accidental_index,
    }
