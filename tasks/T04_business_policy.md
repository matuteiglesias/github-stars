# T04 — Operational Translation

## Objective

Translate model output into an operationally usable challenge response and a defensible interpretation of what the model can and cannot support.

This stage is named business policy, but the case does not define a real downstream business intervention. Do not invent one.

## Inputs

- selected model;
- validation predictions;
- segment error table;
- feature timing register;
- T02 findings;
- prediction dataset in original row order.

## Required work

### 1. Produce the challenge submission

- generate predictions from the selected model;
- clip at zero;
- preserve useful precision;
- preserve prediction-set row order;
- write exact columns `Name,Stars`;
- do not join on `Name` unless uniqueness is proven;
- validate schema and values.

### 2. Interpret RMSLE operationally

Translate log error into multiplicative intuition.

For example, relate representative RMSLE or absolute log errors to approximate multiplicative factors without claiming that a single factor describes every row.

Produce a compact table.

### 3. Identify risk segments

Summarize where predictions are less reliable:

- very low-star repositories;
- extreme high-star repositories;
- rare languages or topics;
- missing descriptions;
- young repositories;
- archived or unusual lifecycle states;
- duplicated or ambiguous entities, if any remain.

### 4. Run early-information sensitivity

When feasible, compare the selected full contemporaneous model with a restricted view excluding:

- forks;
- issues;
- updated-at recency;
- archive status;
- other variables that clearly reflect later trajectory.

Purpose:

- quantify how much predictive performance comes from contemporaneous popularity proxies;
- prevent the presentation from implying launch-time forecasting.

This sensitivity is not automatically the submission candidate.

### 5. Record implementation considerations

Document:

- required inputs;
- deterministic preprocessing;
- inference order;
- clipping;
- schema enforcement;
- fixed reference date;
- known failure modes;
- clean-run requirements.

## Capacity scenarios

The master execution philosophy prefers capacity and cutoff scenarios when predictions drive limited operational capacity.

This case provides no such capacity.

Therefore:

- do not invent top-k budgets;
- do not invent promotion thresholds;
- do not calculate expected gains for a fictional intervention.

A ranking or top-k view may be included only as a descriptive convenience for inspecting predictions, not as a client policy.

## Outputs

- validated submission;
- submission validation report;
- multiplicative error interpretation;
- sensitivity comparison;
- implementation notes;
- closure memo.

## Acceptance criteria

- submission passes all contract checks;
- model use matches the stated timing;
- metric interpretation is understandable;
- high-risk segments are visible;
- sensitivity is complete or clearly marked infeasible;
- no unsupported policy has been invented.

## Integrity checks

- same selected model metadata as T03;
- no post-hoc manual prediction edits;
- no accidental index column;
- no negative or non-finite values;
- exact row count;
- stable order;
- no causal wording.

## Closure memo

Write `artifacts/generated/memos/T04_closure_memo.md`.

It must state:

- whether the submission is operationally valid;
- selected model identifier;
- dominant error risks;
- full versus early-information result;
- unresolved delivery risks;
- what the human must decide before presentation.

## Conditions that unlock T05

Gate 04 passes and every material claim can be traced to a saved artifact.
