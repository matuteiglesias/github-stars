# Stage Gates

## Gate 00 — Problem Definition

### Unlocks

T01 Data Audit.

### Pass conditions

- business problem written;
- decision written;
- unit of analysis written;
- target written;
- prediction timing written;
- metric written;
- constraints written;
- leakage risks written;
- out-of-scope items written;
- open assumptions written;
- human/agent responsibility boundary written.

### Fail conditions

- the task is still described ambiguously as future popularity prediction;
- target timing is unstated;
- the agent intends to use external lookup;
- the final business recommendation is delegated to the agent.

## Gate 01 — Data Audit

### Unlocks

T02 Hypothesis-driven EDA and T03 preprocessing design.

### Pass conditions

- all raw files inventoried;
- schemas recorded;
- target distribution profiled;
- duplicates and overlaps checked;
- missing and literal unknown values checked;
- numeric and date ranges checked;
- temporal coverage documented;
- entity identity risks documented;
- submission identity strategy selected;
- every observed variable has a timing class;
- limitations register exists;
- no unresolved critical integrity failure.

### Critical failures

- target contamination in prediction features;
- unexplained cross-file entity overlap;
- malformed dates that make age irrecoverable;
- no reliable way to preserve prediction row identity;
- target values outside the metric domain;
- unexpected schema not incorporated into the timing register.

## Gate 02 — Hypothesis EDA

### Unlocks

Final feature set and model execution.

### Pass conditions

- each chart maps to a written hypothesis;
- no more than five charts without justification;
- both required challenge figures exist;
- three to five findings are recorded;
- findings distinguish description from causation;
- no EDA transform leaks target information into later validation.

### Fail conditions

- chart dump without decisions;
- required figures use runtime-dependent age;
- rare-category plots imply unsupported population claims;
- findings rely on unlogged manual filtering.

## Gate 03 — Modeling

### Unlocks

T04 Operational Translation.

### Pass conditions

- naive baseline exists;
- simple pipeline baseline exists;
- one improved model exists;
- validation strategy is documented;
- preprocessing is fold-safe;
- RMSLE is computed correctly;
- negative predictions are prevented;
- segment error is available;
- selected candidate beats or clearly justifies deviation from baseline;
- model selection rationale is recorded.

### Fail conditions

- in-sample metric used for selection;
- model chosen only by complexity or intuition;
- raw URL memorization;
- extensive model zoo;
- no reproducible seed or split manifest;
- unexplained score jump suggesting leakage.

## Gate 04 — Operational Translation

### Unlocks

T05 Human Handoff.

### Pass conditions

- submission schema passes;
- row identity passes;
- predictions are finite and non-negative;
- implementation steps are recorded;
- metric is explained in multiplicative terms;
- close-proxy sensitivity is reported or explicitly ruled infeasible;
- unresolved risks are visible.

### Fail conditions

- submission created through an unsafe join;
- predictions rounded without justification;
- policy language invents an unsupported client capacity;
- contemporaneous associations are framed as launch-time levers.

## Gate 05 — Human Handoff

### Unlocks

Human recommendation and presentation.

### Pass conditions

- evidence summary complete;
- model comparison complete;
- main findings linked to artifacts;
- risks and limitations explicit;
- uncertainties explicit;
- suggested narrative provided;
- human questions provided;
- no final recommendation written by the agent;
- artifact registry updated.

### Terminal condition

After Gate 05 passes, the coding agent stops. The human consultant owns the final recommendation and presentation.
