# Codex Execution Prompt

You are executing a time-constrained consulting analytics case from this repository.

Do not solve the case from this prompt alone. First read:

1. `AGENTS.md`
2. `docs/problem_statement.md`
3. `tasks/T00_problem_definition.md`
4. `plans/execution_plan.md`
5. `plans/stage_gates.md`
6. the current task file

## Context

The exam consists of:

- 15 minutes with the interviewer;
- 120 minutes of independent work;
- 45 minutes of presentation.

The human consultant remains responsible for:

- understanding the problem;
- supervising execution;
- interpreting evidence;
- choosing trade-offs;
- building the executive recommendation;
- presenting the case.

You are responsible for reproducible mechanical analysis and evidence production.

## Case definition

The formal task is to estimate `Stars` for repositories in the prediction dataset and generate `submission.csv`.

Treat the problem provisionally as:

> Given a snapshot of repository metadata, estimate the star count recorded in the same snapshot.

This is contemporaneous estimation, not future forecasting.

Do not claim that predictive features cause popularity.

## Required execution sequence

### T00 — Problem Definition

Confirm that the written analytical contract is internally consistent and record any contradiction revealed by file names, schemas, or challenge instructions.

Do not inspect distributions or train models before T00 is closed.

### T01 — Data Audit

Audit all files under `data/raw/`.

Produce the exact artifacts required by `tasks/T01_data_audit.md`.

Classify every input variable by feature timing before modeling.

### T02 — Hypothesis-driven EDA

Evaluate only the hypotheses specified in `tasks/T02_hypothesis_eda.md`, unless T01 evidence makes one impossible or suggests a clearly superior replacement.

Generate at most five charts unless justified.

### T03 — Modeling

Build:

1. a naive log-scale baseline;
2. a simple reproducible baseline pipeline;
3. one reasonable improved model.

Use validation that best approximates the apparent test construction. Add temporal validation as a robustness test only when the data supports it.

### T04 — Business / Operational Policy

Do not stop at model metrics.

Translate the model output into:

- challenge submission implications;
- risk of large multiplicative errors;
- segment-level error considerations;
- optional early-information sensitivity excluding contemporaneous popularity proxies;
- implementation considerations.

Do not invent a client operating capacity that is not present in the case. When capacity scenarios are not supported, state that the operational action is the ranked or numeric prediction output itself.

### T05 — Human Handoff

Produce the complete briefing specified in `tasks/T05_handoff.md`.

Do not write the final recommendation.

## Execution philosophy

Prefer a complete small solution over an incomplete sophisticated solution.

Every artifact must make a decision easier. If it does not, remove it or justify it.

Save evidence to stable files. Do not rely on terminal output or notebook state as the only record.

When uncertain, state the uncertainty, choose a conservative default, and preserve the alternative as a sensitivity check rather than branching into uncontrolled analysis.
