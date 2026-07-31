# T00 — Problem Definition

## Status

**Provisionally closed. Reopen only if raw-file or interviewer evidence contradicts the contract.**

## Objective

Represent the problem before solving it.

Prevent the analysis from drifting between contemporaneous prediction, future forecasting, causal explanation, and mandatory visualization.

## Inputs

- challenge statement;
- required submission schema;
- supplied variable descriptions;
- interviewer clarifications, if any;
- repository governance documents.

## Analytical contract

### Business problem

Estimate hidden GitHub repository star counts from supplied repository metadata and explain the predictive evidence without making causal claims.

### Decision to support

Assign one defensible, non-negative star estimate to every prediction row and choose the model that best balances out-of-sample RMSLE, validity, robustness, and reproducibility.

### Unit of analysis

One GitHub repository snapshot.

Canonical entity candidate: `URL`, subject to T01 validation.

### Prediction target

`Stars` measured at the dataset snapshot.

### Prediction timing

Same snapshot as the predictors.

This is contemporaneous estimation, not future forecasting.

### Success metric

Primary:

- out-of-sample RMSLE.

Secondary:

- leakage-safe validation;
- stable results;
- valid submission;
- reproducible notebook;
- clear limitations;
- concise executive evidence.

### Operational constraints

- use supplied data only;
- no GitHub lookup;
- preserve raw files;
- fixed seeds;
- fixed age reference date;
- one notebook as presentation layer;
- one baseline plus one improvement;
- strict time budget.

### Leakage risks

- direct target inclusion;
- identity memorization;
- train/prediction entity overlap;
- repeated snapshots;
- fold-unsafe preprocessing;
- post-creation variables misrepresented as launch-time signals;
- target-informed category processing outside folds.

### Out of scope

- causal inference;
- future star growth;
- external enrichment;
- deployment;
- exhaustive tuning;
- model zoo;
- final recommendation written by the coding agent.

### Open assumptions

- train and prediction sets are comparable;
- a stable row identity can be preserved;
- `Name` is not necessarily unique;
- `URL` is an entity identifier;
- star predictions may remain continuous;
- a fixed snapshot reference date can be established;
- the notebook may be executed in a clean environment.

## Outputs

- this written analytical contract;
- `memos/T00_closure_memo.md`;
- initialized decision log.

## Artifacts

- `memos/T00_closure_memo.md`
- `memos/decision_log.md`

## Acceptance criteria

- all contract fields are explicit;
- prediction and causation are separated;
- prediction timing is explicit;
- human and agent responsibilities are explicit;
- T01 has a concrete audit target.

## Integrity checks

- no use of “future popularity” without a future horizon;
- no feature is yet approved merely because it appears in the dataset;
- no external data is implied;
- the submission identity issue is acknowledged.

## Closure memo

The initial closure memo is already provided in `memos/T00_closure_memo.md`.

T01 must reopen T00 only if it finds contradictory evidence, such as multiple target horizons, repeated snapshots, or challenge instructions requiring future prediction.

## Conditions that unlock T01

Gate 00 passes.

T01 is unlocked because the analytical contract exists and is internally consistent.
