"""Deterministic T04 packaging of the selected T03 model outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .contracts import validate_submission


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(root: Path) -> None:
    """Validate the selected output and write compact operational evidence."""
    generated = root / "artifacts/generated"
    modeling = generated / "modeling"
    submission_dir = generated / "submission"
    policy_dir = generated / "policy"
    policy_dir.mkdir(parents=True, exist_ok=True)

    selected = json.loads((modeling / "selected_model.json").read_text())
    comparison = pd.read_csv(modeling / "model_comparison.csv")
    selected_row = comparison.loc[comparison["selected"].astype(bool)]
    if len(selected_row) != 1:
        raise ValueError("T03 must record exactly one selected candidate")
    selected_row = selected_row.iloc[0]
    if selected_row["candidate"] != "M2" or selected["feature_view"] != "full-contemporaneous":
        raise ValueError("T04 expects the recorded T03 M2 full-contemporaneous selection")
    if not np.isclose(selected_row["rmsle"], selected["primary_rmsle"]):
        raise ValueError("Selected-model metadata does not match model comparison")

    prediction_path = root / "data/raw/github-repo-prediction-set.csv"
    prediction_set = pd.read_csv(prediction_path, usecols=["Name"])
    submission_path = submission_dir / "submission.csv"
    submission = pd.read_csv(submission_path)
    report = validate_submission(submission, prediction_set)
    report.update(
        {
            "prediction_order_method": "positional; no join",
            "continuous_precision": bool(
                pd.api.types.is_float_dtype(submission.get("Stars"))
                and (submission["Stars"] % 1 != 0).any()
            ),
            "selected_candidate": str(selected_row["candidate"]),
            "selected_feature_view": selected["feature_view"],
            "selected_rmsle_matches_t03": True,
            "submission_sha256": _sha256(submission_path),
            "prediction_input_sha256": _sha256(prediction_path),
        }
    )
    report["valid"] = bool(report["valid"] and report["continuous_precision"])
    if not report["valid"]:
        raise ValueError(f"Submission contract failed: {report}")
    (submission_dir / "submission_validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    rmsle = float(selected_row["rmsle"])
    median = float(selected_row["median_absolute_log_error"])
    interpretation = pd.DataFrame(
        [
            {
                "measure": "validation RMSLE",
                "log_value": rmsle,
                "multiplicative_factor": np.exp(rmsle),
                "interpretation": "RMS log-error scale expressed as exp(RMSLE); not a per-row guarantee",
            },
            {
                "measure": "median absolute log error",
                "log_value": median,
                "multiplicative_factor": np.exp(median),
                "interpretation": "Half of validation predictions have an absolute log error no larger than this factor",
            },
            {
                "measure": "within 2x",
                "log_value": np.log(2),
                "multiplicative_factor": 2.0,
                "interpretation": f'{selected_row["within_2x_pct"]:.1f}% of validation rows fall within this factor',
            },
            {
                "measure": "within 10x",
                "log_value": np.log(10),
                "multiplicative_factor": 10.0,
                "interpretation": f'{selected_row["within_10x_pct"]:.1f}% of validation rows fall within this factor',
            },
        ]
    )
    interpretation.to_csv(policy_dir / "error_interpretation.csv", index=False)

    views = comparison.set_index("candidate")
    full = float(views.loc["M2", "rmsle"])
    early = float(views.loc["M1", "rmsle"])
    sensitivity = pd.DataFrame(
        [
            {
                "candidate": "M2",
                "feature_view": "full-contemporaneous",
                "validation_rmsle": full,
                "absolute_rmsle_gap_vs_full": 0.0,
                "relative_rmsle_gap_vs_full_pct": 0.0,
                "submission_candidate": True,
            },
            {
                "candidate": "M1",
                "feature_view": "early-information",
                "validation_rmsle": early,
                "absolute_rmsle_gap_vs_full": early - full,
                "relative_rmsle_gap_vs_full_pct": (early / full - 1) * 100,
                "submission_candidate": False,
            },
        ]
    )
    sensitivity.to_csv(policy_dir / "sensitivity_comparison.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    run(parser.parse_args().root.resolve())
