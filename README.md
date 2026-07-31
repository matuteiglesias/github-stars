# GitHub Stars Consulting Analytics Execution Bundle

This repository bundle governs a time-constrained consulting analytics case in which a coding agent performs mechanical analysis while the human consultant retains responsibility for judgment, trade-offs, interpretation, and executive communication.

## Case objective

The formal challenge is to estimate `Stars` for repositories in the prediction dataset and produce a valid `submission.csv` scored by RMSLE.

The case statement also gestures toward explaining repository popularity. This bundle separates three distinct products:

1. **Prediction** — estimate contemporaneous star counts.
2. **Description** — show empirical patterns in the supplied data.
3. **Interpretation** — identify predictive associations without presenting them as causal effects.

The source of truth is the repository, not the notebook. The notebook must remain a thin, linear presentation layer that imports validated logic and consumes generated artifacts.

## Operating model

- The human consultant owns problem framing, supervision, interpretation, trade-offs, and the final recommendation.
- Codex owns reproducible data inspection, feature construction, modeling, evaluation, tables, figures, and evidence packaging.
- Codex must not write the final recommendation.
- No analysis may begin until T00 has a written analytical contract.
- No production candidate may be trained until every input variable has a feature-timing classification.
- Every stage closes with an evidence-backed memo and explicit gate decision.

## Repository structure

```text
README.md
AGENTS.md
CODEX_PROMPT.md
docs/
  problem_statement.md
  methodological_guardrails.md
  business_decision.md
  feature_timing.md
plans/
  execution_plan.md
  artifact_contract.md
  stage_gates.md
tasks/
  T00_problem_definition.md
  T01_data_audit.md
  T02_hypothesis_eda.md
  T03_modeling.md
  T04_business_policy.md
  T05_handoff.md
memos/
  README.md
  T00_closure_memo.md
  decision_log.md
templates/
  stage_closure_memo.md
  human_handoff_brief.md
  evidence_register.csv
artifacts/
  README.md
  artifact_registry.csv
tests/
  README.md
  test_bundle_contract.py
  test_submission_contract.py
src/
  README.md
  case_bundle/
    __init__.py
    contracts.py
    metrics.py
```

Raw files are expected in:

```text
data/raw/
```

Generated artifacts must go under:

```text
artifacts/generated/
```

The agent must never overwrite raw data.

## Execution order

1. Read `AGENTS.md`.
2. Read `docs/problem_statement.md`.
3. Confirm T00 in `tasks/T00_problem_definition.md`.
4. Run T01 and close its gate.
5. Run hypothesis-driven T02.
6. Run T03 baseline and one improved model.
7. Run T04 to translate model output into a usable policy and sensitivity view.
8. Run T05 to prepare the human handoff.
9. Only after the evidence package exists, build or refresh the notebook.

## Definition of done

The bundle is complete when the repository can regenerate, from `data/raw/`:

- a validated data audit;
- a feature-timing register;
- three to five decision-relevant findings;
- a baseline model;
- one reasonable improved model;
- reproducible validation results;
- required figures;
- non-negative prediction output;
- a schema-valid `submission.csv`;
- a briefing for the human consultant;
- a notebook that runs top-to-bottom without hidden state.

The final executive recommendation is intentionally excluded from Codex scope.
