# T02 — Hypothesis-Driven EDA

## Objective

Produce a small set of evidence that clarifies target structure, model design, and executive interpretation.

Do not perform open-ended exploration.

## Inputs

- T01 artifacts;
- cleaned in-memory datasets produced through validated loading logic;
- fixed age reference date;
- feature timing register.

## Hypothesis register

Evaluate up to five hypotheses.

### H1 — Target concentration

**Question:** Is the star distribution sufficiently heavy-tailed that log-scale modeling and segment-level error analysis are necessary?

**Evidence:**

- target quantiles;
- zero and low-star rates;
- top-tail share;
- log-scale distribution.

**Decision made easier:**

- target transform;
- baseline design;
- error reporting.

A table may be preferable to a chart.

### H2 — Repository age

**Question:** Are older repositories systematically more starred, and is the relationship nonlinear or highly dispersed?

**Required figure:**

- `age_stars.png`

Use a fixed reference date.

Prefer log-scaled stars, binned summaries, or density-aware plotting over an unreadable raw scatter.

**Decision made easier:**

- include age;
- transform age;
- avoid causal claims.

### H3 — Forks and activity proxies

**Question:** How much of star predictability is associated with contemporaneous community activity such as forks or issues?

**Evidence:**

- log-scale relationship;
- rank correlation;
- target-banded summaries;
- comparison with and without close proxies later in T04.

**Decision made easier:**

- feature inclusion in challenge model;
- sensitivity interpretation.

### H4 — Topics and language

**Question:** Do language and topic segments show different star distributions, subject to support and rare-category uncertainty?

**Required figure:**

- `topics_language.png`

The visualization must not become a dense matrix of unsupported rare combinations.

Use minimum support thresholds and record excluded mass.

**Decision made easier:**

- category handling;
- rare-category grouping;
- executive segmentation.

### H5 — Lifecycle and maintenance

**Question:** Are archived status, recency, or update patterns associated with different star distributions after controlling descriptively for age bands?

**Evidence:**

- grouped summaries;
- optional figure only if it adds more than a table.

**Decision made easier:**

- include lifecycle variables in full contemporaneous model;
- exclude them from early-information sensitivity.

## Maximum chart rule

Maximum five EDA charts, including the two required figures.

A sixth chart requires a written argument in the closure memo showing why no existing chart or table can answer the question.

## Outputs

- hypothesis register;
- finding register;
- required figures;
- zero to three additional figures;
- closure memo.

## Finding standard

Each finding must include:

- magnitude or directional evidence;
- population and support;
- caveat;
- relevance to model or decision;
- explicit label: descriptive, predictive, or sensitivity-related.

## Acceptance criteria

- all figures answer registered hypotheses;
- required figures exist;
- three to five findings are concise and evidence-backed;
- no causal claims;
- no runtime-dependent age;
- rare-category support is visible;
- no leakage-inducing transform is carried into modeling.

## Integrity checks

- plotting code uses validated data;
- figure paths are deterministic;
- chart filters are recorded;
- missing values are not silently dropped;
- topic parsing is reproducible;
- train/prediction distribution comparisons do not use hidden target values.

## Closure memo

Write `artifacts/generated/memos/T02_closure_memo.md`.

It must state:

- which hypotheses were supported;
- which were rejected or inconclusive;
- what changed in the modeling plan;
- which figures are presentation candidates;
- why any optional chart exists.

## Conditions that unlock T03 execution

- Gate 02 passes;
- baseline feature set is fixed;
- improved-model feature set is bounded;
- no unresolved EDA ambiguity is allowed to expand into a model zoo.
