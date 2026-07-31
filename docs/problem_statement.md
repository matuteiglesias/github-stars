# Problem Statement

## Formal challenge

The supplied challenge asks the analyst to:

- estimate `Stars` for repositories whose target value is hidden;
- produce `submission.csv`;
- minimize the evaluation metric;
- provide two required visualizations;
- explain the work in one notebook.

The expected raw data location is `data/raw/`.

## Problem represented before solving

The case statement mixes prediction, explanation, and visualization. These must be separated.

### Product 1 — Prediction

Estimate the star count for each repository in the prediction dataset.

### Product 2 — Description

Describe empirical relationships among repository characteristics, age, languages, topics, and star counts.

### Product 3 — Interpretation

Identify predictive associations that help explain model behavior, while avoiding causal language.

A predictive model can exploit associations without identifying factors that cause popularity.

## Working analytical question

> Given a snapshot of metadata for a GitHub repository, estimate the number of stars recorded in that same snapshot.

This is a supervised cross-sectional estimation problem.

It is not, absent additional target timestamps, a forecast of future popularity.

## Decision supported

The only explicit operational action in the challenge is:

1. estimate hidden star values;
2. generate a valid submission;
3. minimize RMSLE.

No actual business intervention, resource allocation, or user decision is specified.

Accordingly, the minimal defensible decision is:

> Which numeric star estimate should be assigned to each repository in the prediction set?

Any broader recommendation must be presented as an interpretive extension, not as a requirement directly supported by the prompt.

## Unit of analysis

A row is provisionally interpreted as one repository observed at one extraction moment.

The canonical entity identifier is provisionally `URL`, subject to validation.

`Name` must not be assumed unique. Repositories can share names under different owners.

## Target

`Stars` at the dataset snapshot.

## Prediction timing

The prediction is made using values from the same snapshot as the target.

Variables such as `Forks`, `Issues`, and `Updated At` may be valid for contemporaneous estimation while being invalid for a launch-time forecast.

## Success metric

The formal metric is RMSLE:

```text
sqrt(mean((log1p(y_true) - log1p(y_pred))^2))
```

Implications:

- negative predictions are invalid;
- multiplicative error matters more than absolute error;
- training and validation should align with `log1p(Stars)`;
- model comparison must use untouched validation data;
- predictions should not be rounded unless required by the submission contract.

## Required outputs

- `submission.csv` with columns `Name,Stars`;
- one executable notebook;
- Topics × Language visualization;
- Age × Stars visualization;
- concise explanation of method, validation, findings, and limitations.

## Constraints

Default policy:

- use only supplied files;
- do not query GitHub;
- do not enrich repository identities externally;
- fix seeds;
- fix the age reference date;
- keep the notebook thin;
- keep all mechanical logic reproducible outside notebook cells;
- preserve raw inputs unchanged.

## Leakage and validity risks

- direct inclusion of `Stars`;
- repository identity memorization through raw `URL` or `Name`;
- duplicated repositories across train and prediction sets;
- multiple snapshots of the same repository;
- preprocessing fit before splitting;
- target-derived features;
- target encoding fit outside training folds;
- interpreting contemporaneous community variables as launch-time predictors.

## Out of scope

Unless new evidence explicitly changes the contract:

- causal inference;
- future star forecasting;
- external GitHub lookup;
- scraping;
- deep learning;
- exhaustive tuning;
- production deployment;
- a business intervention not named in the case;
- claims about what makes repositories popular in a causal sense.

## Open assumptions to test

- train and prediction data represent comparable snapshots;
- `URL` identifies repository entities consistently;
- `Name` may contain duplicates;
- prediction rows retain a stable order;
- star predictions may be real-valued;
- the evaluator accepts non-integer predictions;
- a fixed extraction or proxy date can be inferred;
- the notebook may need to run in a clean environment.
