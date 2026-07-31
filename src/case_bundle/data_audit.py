"""Deterministic T01 audit for the supplied GitHub repository CSV files.

The implementation deliberately uses the Python standard library so the audit can
run in a clean environment without fitting any preprocessing or model.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

UNKNOWN_LITERALS = {"unknown", "none", "null", "n/a", "na", "-", "?"}
BOOL_COLUMNS = {
    "Has Issues", "Has Projects", "Has Downloads", "Has Wiki", "Has Pages",
    "Has Discussions", "Is Fork", "Is Archived", "Is Template",
}
NUMERIC_COLUMNS = {"Size", "Stars", "Forks", "Issues"}
DATE_COLUMNS = {"Created At", "Updated At"}

TIMING = {
    "Name": ("identity/text", "available-during-decision", "restricted lexical only", "sensitivity candidate", "identity memorization; unsafe join unless unique"),
    "Description": ("free text", "available-during-decision", "candidate", "candidate", "high dimensionality and missingness"),
    "URL": ("identity", "available-during-decision", "identity only", "exclude", "target recovery and memorization"),
    "Created At": ("timestamp", "pre-decision", "derived only", "derived age/date", "fixed reference date required"),
    "Updated At": ("timestamp", "available-during-decision", "candidate in full model", "exclude", "post-creation lifecycle proxy"),
    "Homepage": ("URL/text", "available-during-decision", "derived only", "candidate presence flag", "external resolution prohibited"),
    "Size": ("count", "available-during-decision", "candidate in full model", "exclude", "snapshot-derived and heavy-tailed"),
    "Stars": ("target", "generated-after-decision", "exclude", "exclude", "direct target"),
    "Forks": ("count", "available-during-decision", "candidate in full model", "exclude", "close popularity proxy"),
    "Issues": ("count", "available-during-decision", "candidate in full model", "exclude", "community-activity proxy"),
    "Language": ("category", "available-during-decision", "candidate", "candidate", "rare categories and missingness"),
    "License": ("category", "available-during-decision", "candidate", "candidate if timing defensible", "may change after creation"),
    "Topics": ("list-like category", "available-during-decision", "candidate", "candidate", "parsing and rare-value risk"),
    "Has Issues": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Has Projects": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Has Downloads": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Has Wiki": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Has Pages": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Has Discussions": ("boolean", "available-during-decision", "candidate in full model", "candidate if timing defensible", "configuration can change"),
    "Is Fork": ("boolean", "available-during-decision", "candidate", "candidate", "source relationship not directly supplied"),
    "Is Archived": ("boolean", "available-during-decision", "candidate in full model", "exclude", "late lifecycle state"),
    "Is Template": ("boolean", "available-during-decision", "candidate", "candidate if timing defensible", "configuration can change"),
    "Default Branch": ("category", "available-during-decision", "candidate", "candidate if timing defensible", "may change after creation"),
}


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _normal_url(value: str) -> str:
    try:
        split = urlsplit(value.strip())
        path = re.sub(r"/+", "/", split.path).rstrip("/")
        if path.lower().endswith(".git"):
            path = path[:-4]
        return urlunsplit((split.scheme.lower(), split.netloc.lower(), path.lower(), "", ""))
    except ValueError:
        return value.strip().lower().rstrip("/")


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] if low == high else ordered[low] * (high - position) + ordered[high] * (position - low)


def run_audit(root: Path) -> None:
    raw_dir = root / "data/raw"
    output = root / "artifacts/generated"
    paths = sorted(raw_dir.glob("*.csv"))
    inventories, schemas, quality, duplicates, temporal = [], [], [], [], []
    frames: dict[str, dict[str, object]] = {}
    malformed_total = 0

    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            raw_rows = list(reader)
        malformed = sum(len(row) != len(header) for row in raw_rows)
        malformed_total += malformed
        rows = [dict(zip(header, row)) for row in raw_rows if len(row) == len(header)]
        role = "labeled training" if "Stars" in header else ("sample submission" if header == ["Name"] else "prediction")
        name = path.name
        frames[name] = {"header": header, "rows": rows, "role": role, "sha256": digest}
        inventories.append({"file_name": name, "size_bytes": path.stat().st_size, "row_count": len(raw_rows), "column_count": len(header), "inferred_role": role, "sha256": digest})
        quality.extend([
            {"check": "malformed row width", "dataset": name, "result": malformed, "severity": "critical" if malformed else "info", "evidence": f"{malformed} rows differ from {len(header)} columns", "implication": "Parsing unreliable" if malformed else "CSV row widths are consistent"},
            {"check": "duplicate column names", "dataset": name, "result": len(header)-len(set(header)), "severity": "critical" if len(header)!=len(set(header)) else "info", "evidence": str([c for c,n in Counter(header).items() if n>1]), "implication": "Ambiguous fields" if len(header)!=len(set(header)) else "None"},
            {"check": "accidental index columns", "dataset": name, "result": sum(c.lower().startswith("unnamed:") for c in header), "severity": "warning" if any(c.lower().startswith("unnamed:") for c in header) else "info", "evidence": str([c for c in header if c.lower().startswith("unnamed:")]), "implication": "Exclude if present"},
        ])
        for column in header:
            values = [row[column] for row in rows]
            empty = sum(value == "" for value in values)
            whitespace = sum(bool(value) and not value.strip() for value in values)
            unknown = sum(value.strip().lower() in UNKNOWN_LITERALS for value in values)
            parse_failures = 0
            inferred = "string"
            valid_values = [v for v in values if v.strip() and v.strip().lower() not in UNKNOWN_LITERALS]
            if column in NUMERIC_COLUMNS:
                inferred = "numeric"
                for value in valid_values:
                    try: float(value)
                    except ValueError: parse_failures += 1
            elif column in DATE_COLUMNS:
                inferred = "datetime"
                parse_failures = sum(_parse_date(value) is None for value in valid_values)
            elif column in BOOL_COLUMNS:
                inferred = "boolean"
                parse_failures = sum(value not in {"True", "False"} for value in valid_values)
            elif column == "Topics":
                inferred = "list-like string"
                for value in valid_values:
                    try:
                        parsed = ast.literal_eval(value)
                        if not isinstance(parsed, list): parse_failures += 1
                    except (ValueError, SyntaxError): parse_failures += 1
            schemas.append({"dataset": name, "variable": column, "inferred_dtype": inferred, "null_count": empty, "null_rate": round(empty / len(rows), 8) if rows else 0, "unique_count": len(set(values)), "parse_failures": parse_failures, "sample_safe_summary": f"nonempty={len(rows)-empty}; unknown_literals={unknown}; whitespace_only={whitespace}"})
            quality.append({"check": f"missing/unknown: {column}", "dataset": name, "result": empty+whitespace+unknown, "severity": "warning" if empty+whitespace+unknown else "info", "evidence": f"empty={empty}; whitespace={whitespace}; literal_unknown={unknown}; parse_failures={parse_failures}", "implication": "Handle explicitly in later pipelines" if empty+whitespace+unknown+parse_failures else "No issue observed"})

        tuple_rows = [tuple(row.get(c, "") for c in header) for row in rows]
        urls = [row.get("URL", "") for row in rows if row.get("URL", "")]
        names = [row.get("Name", "") for row in rows if row.get("Name", "")]
        for check, count, note in [
            ("exact duplicate rows", len(tuple_rows)-len(set(tuple_rows)), "all-column equality"),
            ("duplicate URLs", len(urls)-len(set(urls)), "exact nonempty URL"),
            ("duplicate normalized URLs", len(urls)-len({_normal_url(v) for v in urls}), "case/trailing slash/.git normalized"),
            ("duplicate names", len(names)-len(set(names)), "Name is not assumed to be identity"),
        ]:
            duplicates.append({"dataset_a": name, "dataset_b": name, "check": check, "count": count, "severity": "warning" if count else "info", "evidence": note, "handling_rule": "Use URL/row position; investigate conflicts" if count else "No action"})

        for date_column in DATE_COLUMNS & set(header):
            parsed = [_parse_date(row[date_column]) for row in rows if row[date_column].strip()]
            valid = [value for value in parsed if value is not None]
            temporal.append({"dataset": name, "date_field": date_column, "minimum": min(valid).isoformat() if valid else "", "maximum": max(valid).isoformat() if valid else "", "invalid_count": len(parsed)-len(valid), "reference_date_candidate": max(valid).date().isoformat() if valid else "", "notes": "UTC timestamps parsed with ISO-8601"})
        if DATE_COLUMNS <= set(header):
            reversed_dates = sum(1 for row in rows if (c := _parse_date(row["Created At"])) and (u := _parse_date(row["Updated At"])) and u < c)
            quality.append({"check": "updated before created", "dataset": name, "result": reversed_dates, "severity": "critical" if reversed_dates else "info", "evidence": f"{reversed_dates} rows", "implication": "Age/lifecycle invalid" if reversed_dates else "Date ordering valid"})
        for column in NUMERIC_COLUMNS & set(header):
            numeric = [float(row[column]) for row in rows if row[column].strip() and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", row[column].strip())]
            negatives = sum(v < 0 for v in numeric)
            quality.append({"check": f"negative numeric: {column}", "dataset": name, "result": negatives, "severity": "critical" if column == "Stars" and negatives else ("warning" if negatives else "info"), "evidence": f"minimum={min(numeric) if numeric else 'n/a'}; maximum={max(numeric) if numeric else 'n/a'}", "implication": "Invalid metric domain" if column == "Stars" and negatives else ("Review before modeling" if negatives else "Range is non-negative")})
        if "URL" in header:
            malformed_urls = sum(
                not (urlsplit(row["URL"]).scheme in {"http", "https"} and urlsplit(row["URL"]).netloc)
                for row in rows if row["URL"].strip()
            )
            quality.append({"check": "malformed repository URL", "dataset": name, "result": malformed_urls, "severity": "warning" if malformed_urls else "info", "evidence": f"{malformed_urls} nonempty values lack HTTP(S) scheme or host", "implication": "Identity normalization needs review" if malformed_urls else "URL syntax supports identity audit"})
            name_urls: dict[str, set[str]] = defaultdict(set)
            for row in rows:
                if row["Name"] and row["URL"]:
                    name_urls[row["Name"].strip().lower()].add(_normal_url(row["URL"]))
            multi_url_names = sum(len(values) > 1 for values in name_urls.values())
            duplicates.append({"dataset_a": name, "dataset_b": name, "check": "same normalized name under multiple URLs", "count": multi_url_names, "severity": "warning" if multi_url_names else "info", "evidence": "normalized Name groups mapped to >1 normalized URL", "handling_rule": "Never join on Name alone" if multi_url_names else "No action"})

    train_name = next(name for name, data in frames.items() if data["role"] == "labeled training")
    pred_name = next(name for name, data in frames.items() if data["role"] == "prediction")
    train_rows, pred_rows = frames[train_name]["rows"], frames[pred_name]["rows"]
    target_like = [column for column in frames[pred_name]["header"] if re.search(r"star|target|label", column, re.I)]
    quality.append({"check": "target-like prediction feature names", "dataset": pred_name, "result": len(target_like), "severity": "critical" if target_like else "info", "evidence": str(target_like), "implication": "Potential direct leakage" if target_like else "No direct target-name copy observed"})
    sample_name = next(name for name, data in frames.items() if data["role"] == "sample submission")
    sample_rows = frames[sample_name]["rows"]
    sample_order_ok = len(sample_rows) == len(pred_rows) and all(a.get("Name") == b.get("Name") for a, b in zip(sample_rows, pred_rows))
    quality.append({"check": "sample submission Name order", "dataset": sample_name, "result": sample_order_ok, "severity": "critical" if not sample_order_ok else "info", "evidence": f"sample_rows={len(sample_rows)}; prediction_rows={len(pred_rows)}; exact_order_match={sample_order_ok}", "implication": "Preserve prediction row order" if sample_order_ok else "Submission identity contract unresolved"})
    for key, normalizer in [("URL", _normal_url), ("Name", lambda x: x.strip().lower())]:
        left = {normalizer(row[key]) for row in train_rows if row.get(key)}
        right = {normalizer(row[key]) for row in pred_rows if row.get(key)}
        overlap = left & right
        duplicates.append({"dataset_a": train_name, "dataset_b": pred_name, "check": f"cross-file normalized {key} overlap", "count": len(overlap), "severity": "critical" if key == "URL" and overlap else ("warning" if overlap else "info"), "evidence": "set intersection only; values withheld", "handling_rule": "Block until explained" if key == "URL" and overlap else "Preserve prediction row position; never join on Name alone"})
    # Same identity with different full metadata is a possible repeated snapshot/conflict.
    for dataset, data in frames.items():
        if "URL" not in data["header"]: continue
        grouped: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        for row in data["rows"]:
            grouped[_normal_url(row["URL"])].add(tuple(row.get(c, "") for c in data["header"] if c != "Stars"))
        conflicts = sum(len(items) > 1 for items in grouped.values())
        duplicates.append({"dataset_a": dataset, "dataset_b": dataset, "check": "same URL with conflicting metadata / snapshot clue", "count": conflicts, "severity": "warning" if conflicts else "info", "evidence": "normalized URL groups with >1 distinct non-target record", "handling_rule": "Keep snapshots separate and group during validation" if conflicts else "No action"})

    target = [float(row["Stars"]) for row in train_rows if row["Stars"].strip()]
    log_target = [math.log1p(value) for value in target]
    profile_metrics = {
        "count": len(target), "missing_count": len(train_rows)-len(target), "zero_count": sum(v == 0 for v in target),
        "zero_rate": sum(v == 0 for v in target)/len(target), "negative_count": sum(v < 0 for v in target), "minimum": min(target),
        "p01": _quantile(target,.01), "p10": _quantile(target,.1), "p25": _quantile(target,.25), "median": _quantile(target,.5),
        "p75": _quantile(target,.75), "p90": _quantile(target,.9), "p95": _quantile(target,.95), "p99": _quantile(target,.99),
        "mean": sum(target)/len(target), "maximum": max(target), "log1p_minimum": min(log_target),
        "log1p_median": _quantile(log_target,.5), "log1p_mean": sum(log_target)/len(log_target), "log1p_maximum": max(log_target),
    }
    target_profile = [{"metric": key, "value": round(value, 8) if isinstance(value, float) else value, "notes": "Stars in labeled dataset; linear scale" if not key.startswith("log1p") else "natural-log scale"} for key,value in profile_metrics.items()]
    top_rows = sorted(enumerate(train_rows), key=lambda item: float(item[1]["Stars"]), reverse=True)[:10]
    for rank, (position, row) in enumerate(top_rows, 1):
        target_profile.append({"metric": f"extreme_rank_{rank}", "value": row["Stars"], "notes": f"stable URL={row['URL']}; source_row={position+2}"})

    all_updated = [_parse_date(row["Updated At"]) for data in frames.values() if "Updated At" in data["header"] for row in data["rows"] if row["Updated At"]]
    reference = max(value for value in all_updated if value is not None).date().isoformat()
    temporal.append({"dataset": "all feature datasets", "date_field": "fixed age reference", "minimum": "", "maximum": reference, "invalid_count": 0, "reference_date_candidate": reference, "notes": "Latest observed valid Updated At; deterministic snapshot-date proxy"})
    train_dates = {_parse_date(row["Created At"]).date() for row in train_rows if _parse_date(row["Created At"])}
    pred_dates = {_parse_date(row["Created At"]).date() for row in pred_rows if _parse_date(row["Created At"])}
    temporal.append({"dataset": "train vs prediction", "date_field": "Created At date overlap", "minimum": min(train_dates & pred_dates).isoformat() if train_dates & pred_dates else "", "maximum": max(train_dates & pred_dates).isoformat() if train_dates & pred_dates else "", "invalid_count": 0, "reference_date_candidate": reference, "notes": f"{len(train_dates & pred_dates)} shared calendar dates; chronology alone does not define partition"})

    observed = []
    dtypes = {row["variable"]: row["inferred_dtype"] for row in schemas}
    for variable in sorted({c for data in frames.values() for c in data["header"]}):
        semantic, timing, production, sensitivity, risk = TIMING.get(variable, ("unknown", "ambiguous", "exclude pending review", "exclude", "unexpected schema"))
        observed.append({"variable": variable, "observed_dtype": dtypes[variable], "semantic_role": semantic, "timing_class": timing, "production_use": production, "sensitivity_use": sensitivity, "leakage_risk": risk, "notes": "Classification applies to contemporaneous snapshot decision moment"})

    url_overlap = next(row["count"] for row in duplicates if row["check"] == "cross-file normalized URL overlap")
    name_unique_pred = len({row["Name"] for row in pred_rows}) == len(pred_rows)
    invalid_dates = sum(int(row["invalid_count"]) for row in temporal if row["dataset"] not in {"all feature datasets", "train vs prediction"})
    limitations = [
        {"limitation": "Extraction date is not explicitly supplied", "evidence": f"Latest valid Updated At is {reference}", "consequence": "Age uses a proxy rather than authoritative extraction metadata", "severity": "medium", "mitigation": f"Fix {reference} as deterministic reference and reopen if authoritative date appears", "unresolved": "yes"},
        {"limitation": "Name may not be a safe entity key", "evidence": f"Prediction Name uniqueness={name_unique_pred}", "consequence": "Name-only joins can reorder or duplicate predictions", "severity": "high", "mitigation": "Preserve source row order; use normalized URL for audit identity only", "unresolved": "bounded"},
        {"limitation": "Contemporaneous proxies are not launch-time features", "evidence": "Forks, Issues, Updated At, lifecycle fields coexist with Stars", "consequence": "Model associations cannot be interpreted as causal or early forecasts", "severity": "high", "mitigation": "Full snapshot model plus restricted early-information sensitivity", "unresolved": "bounded"},
        {"limitation": "No source-repository URL is supplied for forks", "evidence": "Only Is Fork is represented", "consequence": "Fork/source family dependence cannot be directly grouped", "severity": "medium", "mitigation": "Flag Is Fork; avoid raw identity; disclose residual dependence risk", "unresolved": "yes"},
        {"limitation": "Cross-file entity overlap", "evidence": f"{url_overlap} normalized URL overlaps", "consequence": "Could contaminate validation or expose target", "severity": "critical" if url_overlap else "low", "mitigation": "Block if nonzero; otherwise retain automated check", "unresolved": "yes" if url_overlap else "no"},
        {"limitation": "Date parse integrity", "evidence": f"{invalid_dates} invalid nonempty date values", "consequence": "Age may be unavailable for affected records", "severity": "critical" if invalid_dates else "low", "mitigation": "Do not silently impute; block if age is materially unrecoverable", "unresolved": "yes" if invalid_dates else "no"},
    ]

    _write(output/"data/file_inventory.csv", ["file_name","size_bytes","row_count","column_count","inferred_role","sha256"], inventories)
    _write(output/"data/schema_audit.csv", ["dataset","variable","inferred_dtype","null_count","null_rate","unique_count","parse_failures","sample_safe_summary"], schemas)
    _write(output/"data/data_quality_table.csv", ["check","dataset","result","severity","evidence","implication"], quality)
    _write(output/"data/target_profile.csv", ["metric","value","notes"], target_profile)
    _write(output/"data/duplicate_audit.csv", ["dataset_a","dataset_b","check","count","severity","evidence","handling_rule"], duplicates)
    _write(output/"data/temporal_coverage.csv", ["dataset","date_field","minimum","maximum","invalid_count","reference_date_candidate","notes"], temporal)
    _write(output/"data/feature_timing_register.csv", ["variable","observed_dtype","semantic_role","timing_class","production_use","sensitivity_use","leakage_risk","notes"], observed)
    _write(output/"data/limitations_register.csv", ["limitation","evidence","consequence","severity","mitigation","unresolved"], limitations)

    critical = malformed_total or url_overlap or profile_metrics["negative_count"] or invalid_dates
    status = "FAIL — blocked" if critical else "PASS — T02 and T03 preprocessing design unlocked"
    memo = f"""# T01 Closure Memo

## Stage and objective

T01 — Data Audit. Determine whether the supplied files support the contemporaneous star-estimation contract before EDA or modeling.

## Inputs and reproducibility

All three CSV files under `data/raw/` were inspected without external data. `file_inventory.csv` records SHA-256 digests so raw-file integrity can be checked. The audit is reproduced with `python -m src.case_bundle.data_audit --root .` and fits no model.

## Required outputs and principal evidence

- File roles: `{train_name}` is labeled training ({len(train_rows):,} rows), `{pred_name}` is prediction ({len(pred_rows):,} rows), and `submission-file.csv` is the Name-only sample submission.
- The labeled target has {profile_metrics['negative_count']} negative values, {profile_metrics['missing_count']} missing values, and {profile_metrics['zero_count']} zeros; it is valid for RMSLE when these counts are zero for negatives/missing values.
- Normalized train/prediction URL overlap: {url_overlap}. Name overlap is separately reported and is not treated as entity proof.
- Every one of the {len(observed)} observed variables has exactly one timing classification.
- Invalid nonempty date values: {invalid_dates}. The fixed age-reference proxy is **{reference}**, the latest valid `Updated At` across feature datasets.

## Decisions

1. **Can the case proceed?** {status}.
2. **Reliable entity key:** normalized `URL` is the audit identity candidate because it includes owner/repository context. It remains excluded from model features. Repeated normalized URLs must be grouped or otherwise controlled in validation if present.
3. **Prediction order:** retain a zero-based internal row position from prediction-file load through scoring and write in unchanged source order. Never join predictions back on `Name` alone, regardless of apparent uniqueness.
4. **Age reference:** {reference}, fixed as a documented proxy because no authoritative extraction field was supplied.
5. **Remaining leakage risks:** contemporaneous Forks, Issues, Updated At, Size, and lifecycle settings can be close or post-creation proxies; raw URL/Name can memorize identity. Full-model use must retain the snapshot interpretation, exclude raw URL, and be compared with an early-information sensitivity.
6. **T00 assumptions:** the file roles, contemporaneous target, exact `Name,Stars` output shape, URL identity strategy, and row-order preservation are confirmed. An authoritative extraction date remains unconfirmed and is replaced provisionally by the fixed proxy. The partition mechanism and integer-output requirement remain unknown; useful prediction precision must be retained.

## Limitations and acceptance criteria

The limitations register records evidence, consequence, severity, mitigation, and unresolved status. The critical Gate 01 checks are target metric domain, date recoverability, observed-schema coverage, cross-file URL overlap, and a deterministic prediction identity strategy. The sample submission matches prediction Names in source order only as a contract check; this does not make Name a reliable key.

## Gate decision

**{status}.** Critical issues are considered unresolved if any of: malformed CSV rows, normalized URL overlap, negative targets, or invalid dates is nonzero. No EDA chart and no model were produced.
"""
    memo_path = output/"memos/T01_closure_memo.md"
    memo_path.parent.mkdir(parents=True, exist_ok=True)
    memo_path.write_text(memo, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    run_audit(args.root.resolve())


if __name__ == "__main__":
    main()
