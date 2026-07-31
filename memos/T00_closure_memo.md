# T00 Closure Memo

## Stage

T00 — Problem Definition

## Status

Closed provisionally.

## Objective

Represent the problem before data analysis or modeling.

## Decision

Proceed with the following working definition:

> Given a snapshot of metadata for a GitHub repository, estimate the number of stars recorded in that same snapshot.

The formal challenge decision is to assign a non-negative star estimate to each prediction row and produce a schema-valid submission optimized for RMSLE.

## Evidence used

- challenge requirements summarized in `docs/problem_statement.md`;
- required submission schema;
- known variable descriptions;
- explicit distinction between prediction, description, and causation.

## Contract summary

- Unit: repository snapshot.
- Target: contemporaneous `Stars`.
- Timing: same snapshot as features.
- Metric: RMSLE.
- Identity candidate: `URL`.
- Submission fields: `Name,Stars`.
- External lookup: prohibited by default.
- Final recommendation: human-owned.
- Notebook: thin presentation layer.
- Repository: reproducible source of truth.

## Leakage position

`Forks`, `Issues`, `Updated At`, and lifecycle flags may be valid for contemporaneous estimation.

They must not be described as launch-time information.

A restricted early-information sensitivity should be produced if feasible.

## Integrity checks

Passed:

- prediction timing is explicit;
- causal claims are excluded;
- external enrichment is excluded;
- identity risk is acknowledged;
- validation choice remains evidence-driven;
- feature timing is required before modeling.

## Unresolved assumptions

- raw-file roles;
- extraction date;
- train/prediction partition mechanism;
- uniqueness of URL and Name;
- integer requirement for submission;
- clean-environment execution requirement.

These are T01 audit targets, not reasons to delay bundle execution.

## Gate decision

Gate 00 passes.

T01 is unlocked.

Reopen T00 only if raw-file or interviewer evidence contradicts the contemporaneous snapshot interpretation.
