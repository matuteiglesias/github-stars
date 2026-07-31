# T04 Implementation Notes

## Purpose and fixed inputs

The production artifact estimates contemporaneous `Stars`; it is not a launch-time forecast. It uses the T03-selected **M2 full-contemporaneous** histogram-gradient-boosting pipeline and its recorded configuration without tuning or feature changes. Required inputs are the labeled and prediction CSV schemas audited in T01, including the fixed feature set in `selected_model.json`. The reference date is fixed at **2023-09-25 UTC**.

## Deterministic clean-run sequence

1. From the repository root, install the pinned packages in `requirements.txt`.
2. Run `python -m src.case_bundle.modeling --root .`. This recreates the seeded split, fold-safe preprocessing, validation evidence, full-data refit, and positionally assembled submission.
3. Run `python -m src.case_bundle.operational --root .`. This verifies that selected-model metadata agrees with T03, validates the submission, records input/output SHA-256 hashes, and rebuilds the T04 tables.
4. Run `pytest -q` and inspect `artifacts/generated/submission/submission_validation.json` for `"valid": true` before delivery.

The prediction file is read in source order, transformed without sorting, and predictions are attached positionally—never joined on `Name`. Numeric/date missingness is handled by training-fitted imputers; unknown categories use the pipeline's safe unknown encoding. Inference applies `expm1` to log predictions, clips at zero, retains floating-point precision, and writes exactly `Name,Stars` without an index.

## Validation and known failure modes

Validation fails loudly for selected-model metadata drift, ambiguous selection, schema or row-count changes, reordered names, null/non-finite/negative predictions, an accidental index, or loss of continuous precision. Input and submission hashes make the validated files identifiable. No prediction may be manually edited after generation; any input change requires a complete rerun.

The main reliability risks are high-star repositories, activity–popularity mismatches, historically popular repositories with weak current proxies, rare/unseen languages, and unusual young or zero-issue profiles. Missing descriptions and archive status did not show aggregate degradation on the held-out sample, but individual exceptions remain. The strong full-versus-early score gap shows reliance on contemporaneous trajectory proxies and rules out interpreting the result as repository-creation forecasting or causal evidence.
