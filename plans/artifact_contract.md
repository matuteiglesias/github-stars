# Artifact Contract

All generated outputs belong under `artifacts/generated/`.

## Global rules

- Stable names only.
- CSV files must include headers.
- Tables must be readable without notebook state.
- Every figure must have a companion findings row or memo reference.
- Every artifact must be listed in `artifacts/artifact_registry.csv`.
- Raw data must never be copied into version control unless explicitly authorized.
- Personally identifying or external lookup data must not be added.

## T00 artifacts

| Path | Purpose |
|---|---|
| `memos/T00_closure_memo.md` | Written analytical contract and gate decision. |
| `memos/decision_log.md` | Durable record of assumptions and method decisions. |

## T01 artifacts

| Path | Required content |
|---|---|
| `artifacts/generated/data/file_inventory.csv` | File name, size, row count, column count, inferred role. |
| `artifacts/generated/data/schema_audit.csv` | Dataset, variable, dtype, null count, unique count, sample-safe summary. |
| `artifacts/generated/data/data_quality_table.csv` | Check, dataset, result, severity, evidence, implication. |
| `artifacts/generated/data/target_profile.csv` | Count, zero rate, quantiles, mean, max, log-scale summaries. |
| `artifacts/generated/data/duplicate_audit.csv` | Exact rows, URL duplicates, name duplicates, cross-file overlap, snapshot clues. |
| `artifacts/generated/data/temporal_coverage.csv` | Min, max, invalid dates, reference-date candidates, overlap by file. |
| `artifacts/generated/data/feature_timing_register.csv` | Full observed-schema timing classification. |
| `artifacts/generated/data/limitations_register.csv` | Limitation, evidence, consequence, mitigation, unresolved status. |
| `artifacts/generated/memos/T01_closure_memo.md` | Gate decision and audit conclusions. |

## T02 artifacts

| Path | Required content |
|---|---|
| `artifacts/generated/eda/hypothesis_register.csv` | Hypothesis, metric, population, expected pattern, result, decision relevance. |
| `artifacts/generated/eda/finding_register.csv` | Finding ID, evidence, magnitude, caveat, implication. |
| `artifacts/generated/figures/topics_language.png` | Required Topics × Language visualization. |
| `artifacts/generated/figures/age_stars.png` | Required Age × Stars visualization with fixed reference date. |
| `artifacts/generated/figures/eda_03.png` | Optional third decision-relevant chart. |
| `artifacts/generated/figures/eda_04.png` | Optional fourth decision-relevant chart. |
| `artifacts/generated/figures/eda_05.png` | Optional fifth decision-relevant chart. |
| `artifacts/generated/memos/T02_closure_memo.md` | Findings, rejected hypotheses, gate decision. |

Unused optional figure files must not be created.

## T03 artifacts

| Path | Required content |
|---|---|
| `artifacts/generated/modeling/split_manifest.json` | Seed, strategy, row counts, date logic, leakage controls. |
| `artifacts/generated/modeling/model_comparison.csv` | Candidate, features, validation RMSLE, stability, complexity, status. |
| `artifacts/generated/modeling/validation_predictions.csv` | Row identifier, actual, prediction, log error, segment labels. |
| `artifacts/generated/modeling/segment_error.csv` | Error by target band, age band, missingness, language support. |
| `artifacts/generated/modeling/selected_model.json` | Model name, rationale, seed, features, exclusions, validation evidence. |
| `artifacts/generated/memos/T03_closure_memo.md` | Baseline comparison, selected candidate, gate decision. |

## T04 artifacts

| Path | Required content |
|---|---|
| `artifacts/generated/submission/submission.csv` | Exact required schema in original prediction-set row order. |
| `artifacts/generated/submission/submission_validation.json` | Schema, row count, null, finite, non-negative, order checks. |
| `artifacts/generated/policy/error_interpretation.csv` | RMSLE translated into multiplicative-error language. |
| `artifacts/generated/policy/sensitivity_comparison.csv` | Full model versus early-information sensitivity. |
| `artifacts/generated/policy/implementation_notes.md` | Reproduction and use instructions. |
| `artifacts/generated/memos/T04_closure_memo.md` | Operational readiness and unresolved risks. |

## T05 artifacts

| Path | Required content |
|---|---|
| `artifacts/generated/handoff/human_brief.md` | Complete evidence briefing, without final recommendation. |
| `artifacts/generated/handoff/presentation_evidence_map.csv` | Claim, evidence artifact, caveat, possible slide role. |
| `artifacts/generated/handoff/open_questions.md` | Questions requiring human judgment. |
| `artifacts/generated/memos/T05_closure_memo.md` | Handoff completeness and final agent stop. |

## Submission contract

Required columns in exact order:

```text
Name,Stars
```

Required checks:

- row count equals prediction-set row count;
- row order preserved unless an explicit stable key is validated;
- no null predictions;
- all predictions finite;
- all predictions non-negative;
- no accidental index column;
- no duplicate column names;
- no join on `Name` alone unless uniqueness is proven;
- values retain useful precision unless integers are explicitly required.
