# Methodological Guardrails

## 1. Separate the questions

Keep these claims distinct:

- **Prediction:** the model estimates star counts.
- **Association:** a feature is associated with star count or prediction.
- **Causation:** changing a feature would change popularity.

Only the first two are supported by this case.

## 2. Align validation with the actual task

Do not choose temporal validation merely because timestamps exist.

First compare train and prediction-set temporal distributions.

Use:

- a primary split that approximates the apparent construction of the hidden test set;
- an optional temporal holdout as a robustness test if the data supports a meaningful chronology.

State which generalization claim each split supports.

## 3. Fit transforms inside the training pipeline

All learned preprocessing must be fit on training folds only, including:

- imputers;
- scalers;
- vocabulary selection;
- rare-category grouping thresholds when target-informed;
- target encoders;
- text vectorizers;
- dimensionality reduction.

## 4. Preserve raw data

Never edit or overwrite `data/raw/`.

Create derived data under `artifacts/generated/derived/` only when required for reuse or auditability.

## 5. Use a fixed temporal reference

Repository age must not silently depend on runtime date.

Use, in order of preference:

1. dataset extraction date;
2. latest plausible snapshot date established from metadata;
3. a documented proxy date.

Record the chosen date and rationale.

## 6. Identity is not an ordinary feature

Use `URL` to:

- test uniqueness;
- detect duplicates;
- detect overlap;
- preserve joins;
- trace errors.

Do not feed raw repository identity into the production candidate.

`Name` may support limited lexical features only if:

- raw identity memorization is avoided;
- preprocessing is fold-safe;
- the benefit is measured;
- the handoff explains the risk.

## 7. Handle heavy-tailed targets explicitly

Expected target properties:

- non-negative;
- likely right-skewed;
- potentially many low-star repositories;
- potentially extreme outliers.

Required checks:

- target quantiles;
- zero count;
- maximum and top values;
- log-scale histogram or table;
- multiplicative error by target band.

## 8. Limit model complexity

Required model ladder:

1. naive constant baseline;
2. simple regularized baseline pipeline;
3. one improved model.

Stop when the improved model is good enough to support a coherent explanation and submission.

Do not trade away reproducibility for a marginal score gain.

## 9. Make figures answer questions

Each figure must have:

- a named hypothesis;
- a one-sentence question;
- a defined population;
- clear axes;
- appropriate scale;
- a saved file;
- a written finding;
- a limitation.

## 10. Report uncertainty honestly

At minimum report:

- validation variance or repeated split sensitivity when feasible;
- performance by target band;
- performance for rare categories or missingness segments;
- consequences of duplicate or temporal drift risk;
- sensitivity to excluding contemporaneous popularity proxies.

## 11. Preserve submission identity

The output contract may require `Name,Stars`, but `Name` may not be unique.

Generate submission rows by preserving prediction-set row order or a validated stable row identifier. Never join predictions back on `Name` alone unless uniqueness is proven.

## 12. Human recommendation boundary

The agent can suggest a narrative structure.

The agent cannot decide:

- the final headline;
- whether to emphasize score or interpretation;
- what caveats to lead with;
- what business recommendation to make beyond the evidence.
