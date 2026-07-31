# Execution Plan

## Overall time budget

- Interview discussion: 15 minutes
- Independent work: 120 minutes
- Presentation: 45 minutes

The repository bundle supports the 120-minute execution period and the handoff into presentation preparation.

## Interview discussion — 0 to 15 minutes

Human consultant objectives:

1. clarify whether the target is contemporaneous or future;
2. ask how train and prediction sets were constructed;
3. ask whether external data is prohibited;
4. ask whether submissions require integer star counts;
5. ask whether the notebook will be executed from a clean environment;
6. state the distinction between prediction, association, and causation.

Do not spend the interview discussing model brands.

## Independent work — 120 minutes

### 0–10 minutes — T00 confirmation

- verify raw file inventory;
- confirm target and output schema references;
- reconcile any prompt contradictions;
- record final working assumptions;
- close T00.

Primary artifact:

- `memos/T00_closure_memo.md`

### 10–30 minutes — T01 data audit

Perform:

- dimensions;
- schemas;
- target distribution;
- duplicates;
- missingness;
- literal unknown values;
- ranges;
- temporal coverage;
- repeated entities;
- train/prediction overlap;
- submission identity checks;
- feature timing classification;
- limitations.

Primary artifacts:

- data audit table;
- limitation register;
- feature timing register;
- audit summary.

### 30–50 minutes — T02 hypothesis-driven EDA

Evaluate no more than five questions.

Minimum expected findings:

- global target shape;
- age relationship;
- forks/activity relationship;
- language/topics segmentation;
- lifecycle or maintenance pattern.

Required challenge figures must be produced here or from the same validated tables.

### 50–85 minutes — T03 modeling

Build:

1. naive baseline;
2. regularized simple baseline;
3. one improved model.

Use reproducible preprocessing and validation.

Save:

- split manifest;
- model comparison;
- out-of-fold or validation predictions;
- segment error table;
- selected candidate metadata.

### 85–100 minutes — T04 operational translation

Produce:

- submission;
- submission validation;
- multiplicative error interpretation;
- error-risk segments;
- sensitivity excluding close popularity proxies;
- implementation notes.

### 100–115 minutes — T05 human handoff

Prepare:

- evidence summary;
- model comparison;
- main findings;
- risks;
- limitations;
- uncertainties;
- suggested narrative;
- questions for human judgment.

### 115–120 minutes — execution check

Run:

- required-file checks;
- schema checks;
- notebook top-to-bottom smoke test if already available;
- artifact registry update;
- final gate status.

Do not use this time for last-minute model expansion.

## Presentation preparation — 45 minutes

Human-owned sequence:

1. 5 minutes — choose headline and recommendation boundary;
2. 10 minutes — select three to five findings;
3. 10 minutes — choose model comparison and validation explanation;
4. 10 minutes — assemble narrative around decision, evidence, and limitations;
5. 10 minutes — rehearse and remove unnecessary detail.

The presentation should not mirror the notebook cell-by-cell.
