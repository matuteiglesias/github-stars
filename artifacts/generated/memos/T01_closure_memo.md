# T01 Closure Memo

## Stage and objective

T01 — Data Audit. Determine whether the supplied files support the contemporaneous star-estimation contract before EDA or modeling.

## Inputs and reproducibility

All three CSV files under `data/raw/` were inspected without external data. `file_inventory.csv` records SHA-256 digests so raw-file integrity can be checked. The audit is reproduced with `python -m src.case_bundle.data_audit --root .` and fits no model.

## Required outputs and principal evidence

- File roles: `github-repo-data.csv` is labeled training (150,520 rows), `github-repo-prediction-set.csv` is prediction (64,509 rows), and `submission-file.csv` is the Name-only sample submission.
- The labeled target has 0 negative values, 0 missing values, and 0 zeros; it is valid for RMSLE when these counts are zero for negatives/missing values.
- Normalized train/prediction URL overlap: 0. Name overlap is separately reported and is not treated as entity proof.
- Every one of the 23 observed variables has exactly one timing classification.
- Invalid nonempty date values: 0. The fixed age-reference proxy is **2023-09-25**, the latest valid `Updated At` across feature datasets.

## Decisions

1. **Can the case proceed?** PASS — T02 and T03 preprocessing design unlocked.
2. **Reliable entity key:** normalized `URL` is the audit identity candidate because it includes owner/repository context. It remains excluded from model features. Repeated normalized URLs must be grouped or otherwise controlled in validation if present.
3. **Prediction order:** retain a zero-based internal row position from prediction-file load through scoring and write in unchanged source order. Never join predictions back on `Name` alone, regardless of apparent uniqueness.
4. **Age reference:** 2023-09-25, fixed as a documented proxy because no authoritative extraction field was supplied.
5. **Remaining leakage risks:** contemporaneous Forks, Issues, Updated At, Size, and lifecycle settings can be close or post-creation proxies; raw URL/Name can memorize identity. Full-model use must retain the snapshot interpretation, exclude raw URL, and be compared with an early-information sensitivity.
6. **T00 assumptions:** the file roles, contemporaneous target, exact `Name,Stars` output shape, URL identity strategy, and row-order preservation are confirmed. An authoritative extraction date remains unconfirmed and is replaced provisionally by the fixed proxy. The partition mechanism and integer-output requirement remain unknown; useful prediction precision must be retained.

## Limitations and acceptance criteria

The limitations register records evidence, consequence, severity, mitigation, and unresolved status. The critical Gate 01 checks are target metric domain, date recoverability, observed-schema coverage, cross-file URL overlap, and a deterministic prediction identity strategy. The sample submission matches prediction Names in source order only as a contract check; this does not make Name a reliable key.

## Gate decision

**PASS — T02 and T03 preprocessing design unlocked.** Critical issues are considered unresolved if any of: malformed CSV rows, normalized URL overlap, negative targets, or invalid dates is nonzero. No EDA chart and no model were produced.
