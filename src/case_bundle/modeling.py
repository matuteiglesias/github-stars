"""Reproducible T03 model ladder and submission-candidate generation."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from .contracts import validate_submission

SEED = 202503
REFERENCE_DATE = pd.Timestamp("2023-09-25", tz="UTC")
TARGET_BINS = [-np.inf, 9, 99, 999, 9999, np.inf]
TARGET_LABELS = ["0–9", "10–99", "100–999", "1,000–9,999", "10,000+"]
BOOLS = [
    "Has Issues",
    "Has Projects",
    "Has Downloads",
    "Has Wiki",
    "Has Pages",
    "Has Discussions",
    "Is Fork",
    "Is Template",
]
M1_NUM = ["log_age", "topic_count", "description_missing", "homepage_present", *BOOLS]
M1_CAT = ["Language", "License", "Default Branch"]
M2_NUM = [*M1_NUM, "log_size", "log_forks", "log_issues", "log_recency", "Is Archived"]
M2_CONFIGS = [
    {
        "learning_rate": 0.08,
        "max_iter": 100,
        "max_leaf_nodes": 15,
        "l2_regularization": 1.0,
    },
    {
        "learning_rate": 0.06,
        "max_iter": 140,
        "max_leaf_nodes": 31,
        "l2_regularization": 2.0,
    },
]


def _bool(series: pd.Series) -> pd.Series:
    return series.astype("string").str.lower().map({"true": 1.0, "false": 0.0})


def _topics(value: object) -> int:
    """Count serialized topics without learning a vocabulary."""
    import ast

    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return 0
    return (
        len({str(x).strip().lower() for x in parsed if str(x).strip()})
        if isinstance(parsed, list)
        else 0
    )


def make_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Construct the fixed early and contemporaneous feature views."""
    out = pd.DataFrame(index=raw.index)
    created = pd.to_datetime(raw["Created At"], utc=True, errors="coerce")
    updated = pd.to_datetime(raw["Updated At"], utc=True, errors="coerce")
    age = (REFERENCE_DATE - created).dt.total_seconds() / 86400
    recency = (REFERENCE_DATE - updated).dt.total_seconds() / 86400
    out["log_age"] = np.log1p(age.clip(lower=0))
    topic_text = raw["Topics"].fillna("").astype(str).str.strip()
    # T01 established valid serialized lists; count delimiters without retaining vocabulary.
    out["topic_count"] = np.where(
        topic_text.eq("[]") | topic_text.eq(""), 0, topic_text.str.count(",") + 1
    )
    out["description_missing"] = (
        raw["Description"].fillna("").astype(str).str.strip().eq("").astype(float)
    )
    out["homepage_present"] = (
        raw["Homepage"].fillna("").astype(str).str.strip().ne("").astype(float)
    )
    for column in BOOLS + ["Is Archived"]:
        out[column] = _bool(raw[column])
    for column in M1_CAT:
        out[column] = raw[column].fillna("Missing").astype(str).replace("", "Missing")
    for raw_name, feature in [
        ("Size", "log_size"),
        ("Forks", "log_forks"),
        ("Issues", "log_issues"),
    ]:
        values = pd.to_numeric(raw[raw_name], errors="coerce")
        out[feature] = np.log1p(values.where(values >= 0))
    out["log_recency"] = np.log1p(recency.clip(lower=0))
    out[M1_CAT] = out[M1_CAT].astype("category")
    out[[column for column in out if column not in M1_CAT]] = out[
        [column for column in out if column not in M1_CAT]
    ].astype("float32")
    return out


def _m1() -> Pipeline:
    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    category = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", min_frequency=10)),
        ]
    )
    return Pipeline(
        [
            (
                "prepare",
                ColumnTransformer(
                    [("num", numeric, M1_NUM), ("cat", category, M1_CAT)]
                ),
            ),
            ("model", Ridge(alpha=10.0, solver="lsqr")),
        ]
    )


def _m2(config: dict[str, float | int]) -> Pipeline:
    # Training-fold-only ordinal encoding bounds categorical width and handles unknowns.
    category = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            (
                "encode",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
            ),
        ]
    )
    prep = ColumnTransformer(
        [("num", SimpleImputer(strategy="median"), M2_NUM), ("cat", category, M1_CAT)]
    )
    return Pipeline(
        [
            ("prepare", prep),
            ("model", HistGradientBoostingRegressor(random_state=SEED, **config)),
        ]
    )


def _metrics(actual: np.ndarray, log_prediction: np.ndarray) -> dict[str, float]:
    error = log_prediction - np.log1p(actual)
    return {
        "rmsle": float(np.sqrt(np.mean(error**2))),
        "median_absolute_log_error": float(np.median(np.abs(error))),
        "within_2x_pct": float(np.mean(np.abs(error) <= np.log(2)) * 100),
        "within_10x_pct": float(np.mean(np.abs(error) <= np.log(10)) * 100),
    }


def _predict(model: Pipeline, x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    log_prediction = np.asarray(model.predict(x), dtype=float)
    prediction = np.maximum(0, np.expm1(log_prediction))
    return prediction, np.log1p(prediction)


def _bands(
    frame: pd.DataFrame, actual: np.ndarray, train_languages: pd.Series
) -> pd.DataFrame:
    result = pd.DataFrame(index=frame.index)
    result["target_band"] = pd.cut(actual, TARGET_BINS, labels=TARGET_LABELS)
    age_days = np.expm1(frame["log_age"])
    result["proxy_age_band"] = pd.cut(
        age_days / 365.25,
        [-np.inf, 2, 5, 10, np.inf],
        labels=["≤2y", "2–5y", "5–10y", "10y+"],
    )
    result["description_status"] = np.where(
        frame["description_missing"] == 1, "missing", "present"
    )
    common = set(train_languages.value_counts()[lambda s: s >= 100].index)
    result["language_support"] = np.where(
        frame["Language"].isin(common), "common", "rare-or-unseen"
    )
    result["archived_status"] = np.where(
        frame["Is Archived"] == 1, "archived", "not-archived"
    )
    return result


def _segment_rows(predictions: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate, part in predictions.groupby("candidate", observed=True):
        for dimension in [
            "target_band",
            "proxy_age_band",
            "description_status",
            "language_support",
            "archived_status",
        ]:
            if dimension == "archived_status" and candidate != "M2":
                continue
            for segment, group in part.groupby(dimension, observed=True):
                rows.append(
                    {
                        "candidate": candidate,
                        "dimension": dimension,
                        "segment": segment,
                        "row_count": len(group),
                        "rmsle": np.sqrt(np.mean(group["log_error"] ** 2)),
                        "median_absolute_log_error": np.median(
                            np.abs(group["log_error"])
                        ),
                    }
                )
    return rows


def run(root: Path) -> None:
    """Execute bounded selection, temporal stress test, and full-data candidate output."""
    raw = root / "data/raw"
    output = root / "artifacts/generated"
    model_dir = output / "modeling"
    model_dir.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(raw / "github-repo-data.csv", low_memory=False)
    y = pd.to_numeric(train["Stars"], errors="raise").to_numpy(float)
    if not np.isfinite(y).all() or (y < 0).any():
        raise ValueError("Stars must be complete, finite, and non-negative")
    x = make_features(train)
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(train))
    n_valid = round(0.2 * len(train))
    valid_idx, fit_idx = np.sort(order[:n_valid]), np.sort(order[n_valid:])
    temporal_order = np.argsort(
        pd.to_datetime(train["Created At"], utc=True).to_numpy(), kind="stable"
    )
    temporal_valid, temporal_fit = (
        np.sort(temporal_order[-n_valid:]),
        np.sort(temporal_order[:-n_valid]),
    )
    if set(train.iloc[fit_idx]["URL"]) & set(train.iloc[valid_idx]["URL"]):
        raise ValueError("Repository identity overlaps random split")

    def summary(indices: np.ndarray) -> dict[str, object]:
        values = y[indices]
        return {
            "rows": len(indices),
            "target_min": float(values.min()),
            "target_median": float(np.median(values)),
            "target_mean_log1p": float(np.log1p(values).mean()),
            "target_max": float(values.max()),
            "age_median_days": float(np.median(np.expm1(x.iloc[indices]["log_age"]))),
            "forks_median_log1p": float(np.nanmedian(x.iloc[indices]["log_forks"])),
            "issues_median_log1p": float(np.nanmedian(x.iloc[indices]["log_issues"])),
            "size_median_log1p": float(np.nanmedian(x.iloc[indices]["log_size"])),
        }

    manifest = {
        "seed": SEED,
        "primary_strategy": "seeded random 80/20 holdout",
        "fit": summary(fit_idx),
        "validation": summary(valid_idx),
        "temporal_strategy": "oldest 80% fit; newest 20% Created At stress test",
        "temporal_fit": summary(temporal_fit),
        "temporal_validation": summary(temporal_valid),
        "target_bands": TARGET_LABELS,
        "leakage_controls": [
            "split before learned preprocessing",
            "raw identity excluded",
            "no URL overlap",
            "no target-derived features",
        ],
    }
    (model_dir / "split_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    # Release the wide raw string frame before fitting multiple bounded models.
    del train
    gc.collect()

    comparison = []
    configs = [("M1", None), *[(f"M2-c{i + 1}", c) for i, c in enumerate(M2_CONFIGS)]]
    validation_logs: dict[str, np.ndarray] = {}
    constant = float(np.log1p(y[fit_idx]).mean())
    validation_logs["M0"] = np.full(n_valid, constant)
    comparison.append(
        {
            "candidate": "M0",
            "feature_view": "training-fold log-target constant",
            **_metrics(y[valid_idx], validation_logs["M0"]),
            "temporal_rmsle": "",
            "complexity": "constant",
            "leakage_risk": "low",
        }
    )
    for name, config in configs:
        print(f"Fitting {name}", flush=True)
        model = _m1() if name == "M1" else _m2(config or {})
        model.fit(x.iloc[fit_idx], np.log1p(y[fit_idx]))
        _, validation_logs[name] = _predict(model, x.iloc[valid_idx])
        comparison.append(
            {
                "candidate": name,
                "feature_view": "early-information"
                if name == "M1"
                else "full-contemporaneous",
                **_metrics(y[valid_idx], validation_logs[name]),
                "temporal_rmsle": "",
                "complexity": "regularized linear"
                if name == "M1"
                else "bounded nonlinear tree",
                "leakage_risk": "low" if name == "M1" else "moderate-close proxies",
            }
        )
    best_name = min(
        (name for name, _ in configs if name.startswith("M2")),
        key=lambda name: _metrics(y[valid_idx], validation_logs[name])["rmsle"],
    )
    selected = (
        "M2"
        if _metrics(y[valid_idx], validation_logs[best_name])["rmsle"]
        < _metrics(y[valid_idx], validation_logs["M1"])["rmsle"]
        else "M1"
    )
    for name, config in [("M1", None), (best_name, M2_CONFIGS[int(best_name[-1]) - 1])]:
        print(f"Temporal check {name}", flush=True)
        temporal_model = _m1() if name == "M1" else _m2(config or {})
        temporal_model.fit(x.iloc[temporal_fit], np.log1p(y[temporal_fit]))
        _, logs = _predict(temporal_model, x.iloc[temporal_valid])
        next(row for row in comparison if row["candidate"] == name)[
            "temporal_rmsle"
        ] = _metrics(y[temporal_valid], logs)["rmsle"]
    comparison = [
        row for row in comparison if row["candidate"] in {"M0", "M1", best_name}
    ]
    next(row for row in comparison if row["candidate"] == best_name)["candidate"] = "M2"
    for row in comparison:
        row["selected"] = row["candidate"] == selected
        row["selection_rationale"] = (
            "lowest primary RMSLE among bounded candidates"
            if row["selected"]
            else "benchmark or not best bounded candidate"
        )
    pd.DataFrame(comparison).to_csv(model_dir / "model_comparison.csv", index=False)

    parts = []
    segments = _bands(x.iloc[valid_idx], y[valid_idx], x.iloc[fit_idx]["Language"])
    for name in ["M0", "M1", best_name]:
        pred = np.maximum(0, np.expm1(validation_logs[name]))
        part = segments.copy()
        part.insert(0, "row_identifier", valid_idx)
        part.insert(1, "candidate", "M2" if name.startswith("M2") else name)
        part["actual"] = y[valid_idx]
        part["prediction"] = pred
        part["log_error"] = np.log1p(pred) - np.log1p(y[valid_idx])
        parts.append(part)
    validation = pd.concat(parts, ignore_index=True)
    validation.to_csv(model_dir / "validation_predictions.csv", index=False)
    pd.DataFrame(_segment_rows(validation)).to_csv(
        model_dir / "segment_error.csv", index=False
    )

    selected_config = None if selected == "M1" else M2_CONFIGS[int(best_name[-1]) - 1]
    final_model = _m1() if selected == "M1" else _m2(selected_config or {})
    final_model.fit(x, np.log1p(y))
    prediction_set = pd.read_csv(
        raw / "github-repo-prediction-set.csv", low_memory=False
    )
    x_pred = make_features(prediction_set)
    final_prediction, _ = _predict(final_model, x_pred)
    submission = pd.DataFrame(
        {"Name": prediction_set["Name"], "Stars": final_prediction}
    )
    submission_dir = output / "submission"
    submission_dir.mkdir(exist_ok=True)
    submission.to_csv(submission_dir / "submission.csv", index=False)
    report = validate_submission(submission, prediction_set)
    report["prediction_order_method"] = "positional; no join"
    report["continuous_precision"] = True
    (submission_dir / "submission_validation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    chosen = next(row for row in comparison if row["candidate"] == selected)
    metadata = {
        "model_class": "Ridge" if selected == "M1" else "HistGradientBoostingRegressor",
        "configuration": selected_config or {"alpha": 10.0},
        "seed": SEED,
        "feature_view": chosen["feature_view"],
        "features": M1_NUM + M1_CAT if selected == "M1" else M2_NUM + M1_CAT,
        "excluded_variables": [
            "Stars",
            "URL",
            "Name",
            "Description text",
            "raw Topics",
        ],
        "target_transform": "log1p; expm1 then clip at zero",
        "validation_strategy": manifest["primary_strategy"],
        "primary_rmsle": chosen["rmsle"],
        "temporal_robustness_rmsle": chosen["temporal_rmsle"],
        "selection_rationale": chosen["selection_rationale"],
        "code_version": "source commit at execution: "
        + __import__("subprocess")
        .check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True)
        .strip(),
    }
    (model_dir / "selected_model.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    run(parser.parse_args().root.resolve())
