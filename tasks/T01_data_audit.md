# T01 — Data Audit

## Objective

Determine whether the supplied files can support the analytical contract and expose any integrity issue before EDA or modeling.

## Inputs

- all files under `data/raw/`;
- T00 analytical contract;
- challenge schema and submission instructions.

## Required checks

### File inventory

- file names;
- file sizes;
- row counts;
- column counts;
- likely role: train, prediction, sample submission, unknown.

### Dimensions and schema

- observed columns;
- inferred dtypes;
- parse failures;
- inconsistent columns across files;
- accidental index columns;
- duplicate column names.

### Target profile

For the labeled dataset:

- count;
- missing count;
- zero count and rate;
- negative count;
- minimum;
- quantiles;
- mean;
- maximum;
- `log1p` distribution;
- extreme-value rows traced by stable identifier.

Do not call this “class balance.” It is a regression target. Use target distribution and target-band coverage.

### Duplicate and identity audit

Within and across datasets:

- exact duplicate rows;
- duplicate URLs;
- duplicate names;
- same URL with conflicting metadata;
- same name under multiple URLs;
- normalized URL overlap;
- possible repeated snapshots;
- fork/source relationships if directly represented;
- prediction rows that appear in training.

### Missingness and unknown literals

For every variable:

- null count and rate;
- empty strings;
- whitespace-only values;
- literal values such as `unknown`, `none`, `null`, `n/a`, `-`, `?`;
- whether missingness differs by train versus prediction set.

### Ranges and validity

- negative counts;
- impossible booleans;
- malformed URLs;
- invalid dates;
- updated-before-created cases;
- values beyond plausible technical ranges;
- unexpected category cardinality;
- list-like fields that fail parsing.

### Temporal coverage

- min and max created date;
- min and max updated date;
- invalid dates;
- train/prediction date overlap;
- candidate extraction date;
- fixed age-reference decision;
- whether temporal holdout is meaningful.

### Leakage review

- direct target copies;
- target-like names;
- identity columns;
- post-target timestamps;
- aggregate columns that may derive from `Stars`;
- cross-file overlap;
- preprocessing risks.

### Feature timing

Classify every observed variable using `docs/feature_timing.md`.

### Data limitations

For each limitation record:

- evidence;
- consequence;
- severity;
- mitigation;
- whether unresolved.

## Outputs

- file inventory;
- schema audit;
- data-quality table;
- target profile;
- duplicate audit;
- temporal coverage;
- feature-timing register;
- limitations register;
- closure memo.

## Artifacts

Use exact paths defined in `plans/artifact_contract.md`.

## Acceptance criteria

- every raw file has a role;
- every variable has a timing classification;
- every critical identity risk has an explicit handling rule;
- prediction row identity strategy is fixed;
- age reference date is fixed or a blocking uncertainty is declared;
- target is valid for RMSLE;
- no unexplained critical overlap remains.

## Integrity checks

- raw files unchanged;
- checks are deterministic;
- summaries do not expose or use external data;
- no model fitting occurs;
- no EDA chart is generated beyond what is necessary to verify data integrity;
- no join on `Name` alone.

## Closure memo

Write `artifacts/generated/memos/T01_closure_memo.md` using the stage memo contract.

The memo must answer:

1. Can the case proceed?
2. What is the reliable entity key?
3. How will prediction order be preserved?
4. What is the age reference date?
5. What leakage risks remain?
6. Which assumptions from T00 were confirmed, rejected, or revised?

## Conditions that unlock T02 and T03 design

- Gate 01 passes;
- all variables are classified;
- critical issues are either resolved or explicitly bounded.
