# Business Decision

## What decision is actually supported?

The challenge does not specify a downstream business action such as funding repositories, allocating developer relations resources, or choosing projects to promote.

The only explicit decision is:

> Assign a predicted star count to each repository in the prediction dataset.

Therefore the primary deliverable is a prediction system and valid submission, not a complete operating policy.

## Decision hierarchy

### Level 1 — Required challenge decision

For each prediction row:

- produce one non-negative estimate of `Stars`;
- preserve row identity;
- satisfy the schema;
- optimize expected RMSLE.

### Level 2 — Model selection decision

Choose which candidate is defensible for submission using:

- out-of-sample RMSLE;
- stability;
- leakage risk;
- reproducibility;
- error behavior across star bands;
- implementation simplicity.

### Level 3 — Interpretive decision

Decide which associations are useful to explain:

- age and accumulated visibility;
- forks and community engagement;
- topics and language segments;
- maintenance and archive status;
- textual or categorical signals.

These are descriptive and predictive associations.

## What is not supported

The data does not, by itself, support claims such as:

- adding a topic will cause more stars;
- changing programming language will increase popularity;
- more issues create popularity;
- a repository will become popular after launch;
- a client should invest in a specific repository category.

## Operational translation

Because the formal output is numeric, the operational policy is:

1. validate the prediction-set identity contract;
2. apply the selected pipeline;
3. clip predictions at zero;
4. avoid unnecessary rounding;
5. write `Name,Stars` in original prediction-set order;
6. run schema and value checks;
7. save the exact model and configuration used.

## Optional sensitivity policy

To support a more business-relevant interpretation, compare:

- **full contemporaneous model:** may use valid snapshot variables such as forks and issues;
- **early-information sensitivity model:** excludes close popularity proxies and post-creation signals.

This sensitivity does not replace the challenge model. It clarifies how much predictive power comes from information that already reflects repository trajectory.
