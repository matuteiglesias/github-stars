# T03 — Modeling

## Objective

Build a reproducible model ladder that establishes a credible baseline, tests one meaningful improvement, and selects a defensible submission candidate.

## Inputs

- T01 audit and timing register;
- T02 findings;
- validated loaders;
- fixed split strategy;
- fixed random seed;
- target `log1p(Stars)`.

## T03A — Naive baseline

Required candidate:

- constant prediction based on the training target in log space, converted back with `expm1`.

The exact statistic may be mean log target or another justified constant aligned with RMSLE.

Purpose:

- establish the minimum useful performance;
- validate metric implementation;
- catch pipeline failures.

## T03B — Simple pipeline baseline

Preferred design:

- numeric count and age features;
- boolean flags;
- compact categorical encoding;
- missingness handling;
- regularized linear model on `log1p(Stars)`.

Possible implementation:

- `ColumnTransformer`;
- imputation;
- one-hot encoding with unknown handling;
- scaling for numeric features when appropriate;
- Ridge, Elastic Net, or another simple regularized regressor.

The baseline must remain explainable and fast.

## T03C — One improved model

Choose exactly one improvement path based on T01 and T02 evidence.

Preferred options:

1. a compact tree-based boosting model for nonlinear tabular relationships; or
2. the baseline plus bounded TF-IDF features for description, topics, and limited name text.

Selection rule:

- choose the path most likely to improve RMSLE within the remaining time and dependency constraints;
- do not implement both unless one is abandoned before evaluation.

## Validation strategy

Primary validation must imitate the apparent train/prediction split mechanism.

Possible choices:

- random holdout or K-fold when train and prediction sets appear contemporaneous and similarly distributed;
- grouped split if repeated entities exist;
- temporal holdout if prediction data is clearly later or the task explicitly requires temporal generalization.

Optional robustness:

- one temporal split;
- one alternate seed;
- one proxy-excluded sensitivity.

Do not expand robustness into extensive tuning.

## Required metrics

Primary:

- RMSLE.

Additional diagnostic metrics:

- median absolute log error;
- percentage within multiplicative factors such as 2× and 10×;
- RMSLE by target band;
- RMSLE by age band;
- RMSLE for missing-text and rare-language segments.

Generic RMSE on raw stars is not a selection metric unless included only to illustrate tail sensitivity.

## Prediction rules

- train on `log1p(Stars)` when compatible with the model;
- convert with `expm1`;
- clip at zero;
- retain continuous predictions unless the contract requires integers;
- preserve prediction row order;
- save selected model metadata.

## Model comparison table

Required columns:

- `candidate`
- `feature_view`
- `validation_strategy`
- `rmsle`
- `stability_measure`
- `complexity`
- `leakage_risk`
- `selected`
- `selection_rationale`

## Stopping rule

Stop modeling when:

- one improved model has been evaluated;
- it either materially improves the baseline or the baseline is preferred for a documented reason;
- segment errors are understood;
- no critical leakage concern remains;
- a valid submission can be produced.

Do not tune merely because time remains.

## Outputs

- split manifest;
- model comparison;
- validation predictions;
- segment error table;
- selected model metadata;
- closure memo.

## Acceptance criteria

- naive baseline exists;
- simple pipeline baseline exists;
- one improved model exists or is explicitly abandoned with evidence;
- preprocessing is fold-safe;
- selected candidate is justified;
- predictions are non-negative;
- selected model is reproducible;
- error segments are available.

## Integrity checks

- metric tests pass;
- no direct target in features;
- no raw URL in production features;
- no train/prediction contamination;
- no full-data vocabulary or target encoding;
- validation rows are not used for model selection beyond the bounded comparison;
- no hidden manual edits to predictions.

## Closure memo

Write `artifacts/generated/memos/T03_closure_memo.md`.

It must answer:

1. What did the naive baseline establish?
2. What did the simple model add?
3. What improvement was tested?
4. Which model was selected and why?
5. Where does the model fail?
6. What evidence would change the selection?

## Conditions that unlock T04

Gate 03 passes and a selected candidate can generate deterministic prediction-set outputs.
