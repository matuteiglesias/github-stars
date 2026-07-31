# Feature Timing Contract

## Decision moment

The provisional decision moment is the repository snapshot used by the challenge.

The target is `Stars` measured at that same snapshot.

This timing makes contemporaneous repository metadata available for the challenge prediction. It does not make those features valid for predicting future success at repository creation.

## Allowed classes

Every variable must be classified as exactly one of:

- `pre-decision`
- `available-during-decision`
- `generated-after-decision`
- `ambiguous`

No production candidate may be trained until the observed schema has been fully classified.

## Provisional classification

| Variable | Timing class | Production use | Rationale and risk |
|---|---|---:|---|
| `Stars` | generated-after-decision | No | Direct target. |
| `URL` | available-during-decision | Identity only | Canonical entity candidate; high memorization and external lookup risk. |
| `Name` | available-during-decision | Restricted | May support fold-safe lexical features; raw identity risk; not a safe join key without uniqueness proof. |
| `Description` | available-during-decision | Candidate | Text exists at snapshot; missingness and high dimensionality require controlled processing. |
| `Created At` | pre-decision | Derived only | Use for fixed-reference age and date components. |
| `Updated At` | available-during-decision | Candidate in full model | Valid for contemporaneous estimation, invalid for launch-time forecasting. |
| `Forks` | available-during-decision | Candidate in full model | Close proxy for popularity and community reach; exclude in early-information sensitivity. |
| `Issues` | available-during-decision | Candidate in full model | May reflect community size and repository configuration; exclude or flag in sensitivity. |
| `Topics` | available-during-decision | Candidate | Multi-valued categorical text; rare-value and parsing risks. |
| `Language` | available-during-decision | Candidate | Segment signal; rare classes and missing values require handling. |
| `Homepage` | available-during-decision | Derived only | Use simple presence or domain-type features; no external resolution. |
| `Is Archived` | available-during-decision | Candidate in full model | Lifecycle state may occur long after creation. |
| `Is Fork` | available-during-decision | Candidate | Must be interpreted alongside source-repository overlap risk. |
| `Has Issues` | available-during-decision | Candidate | Configuration flag, distinct from issue count. |
| `Has Projects` | available-during-decision | Candidate | Configuration flag. |
| `Has Downloads` | available-during-decision | Candidate | Configuration flag. |
| `Has Wiki` | available-during-decision | Candidate | Configuration flag. |
| `Has Pages` | available-during-decision | Candidate | Configuration flag. |

## Required observed-schema register

T01 must produce:

```text
artifacts/generated/data/feature_timing_register.csv
```

Required columns:

- `variable`
- `observed_dtype`
- `semantic_role`
- `timing_class`
- `production_use`
- `sensitivity_use`
- `leakage_risk`
- `notes`

Any unexpected variable must be classified before modeling.

## Timing-sensitive model views

### Full contemporaneous view

Uses variables available at the snapshot, except direct target, raw identity, and any variable proven unsafe.

### Early-information sensitivity view

Uses only information plausibly available near creation:

- created date;
- language;
- topics;
- description-derived features;
- stable repository configuration flags, only if their timing is defensible.

This view is interpretive and robustness-oriented, not necessarily the submission candidate.
