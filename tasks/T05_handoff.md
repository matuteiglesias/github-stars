# T05 — Human Handoff

## Objective

Package the evidence so the human consultant can make the final recommendation and build the presentation without reopening the entire analysis.

The coding agent must stop after this stage.

## Inputs

- all closure memos;
- artifact registry;
- validated figures;
- model comparison;
- segment error;
- submission validation;
- sensitivity results;
- limitations register.

## Required briefing sections

### 1. Evidence summary

Maximum ten bullets.

Each bullet must reference an artifact and state what decision it informs.

### 2. Model comparison

Include:

- naive baseline;
- simple pipeline;
- improved model;
- selected candidate;
- validation strategy;
- score;
- stability;
- complexity;
- selection reason.

### 3. Main findings

Three to five findings only.

For each:

- claim;
- magnitude;
- evidence;
- caveat;
- presentation value.

### 4. Risks

Include:

- leakage risks;
- identity risks;
- temporal mismatch;
- extreme-tail error;
- train/prediction drift;
- dependency or clean-run risk.

### 5. Limitations

Distinguish:

- data limitations;
- validation limitations;
- interpretation limitations;
- operational limitations.

### 6. Remaining uncertainties

List only uncertainties that could change:

- model choice;
- claimed interpretation;
- submission validity;
- presentation framing.

### 7. Suggested narrative

Provide a possible structure, not a final recommendation:

1. define the real task;
2. show data and timing discipline;
3. present two or three empirical patterns;
4. compare baseline and improvement;
5. explain model risk;
6. state what can and cannot be concluded;
7. hand decision framing to the human consultant.

### 8. Questions for the human consultant

Examples:

- Should the presentation lead with challenge performance or analytical discipline?
- Should the early-information sensitivity be central or backup?
- Which limitation should be volunteered before the interviewer asks?
- Is the selected score improvement worth the added complexity?
- Which three figures or tables best fit the 45-minute discussion?

## Required artifacts

- `artifacts/generated/handoff/human_brief.md`
- `artifacts/generated/handoff/presentation_evidence_map.csv`
- `artifacts/generated/handoff/open_questions.md`
- `artifacts/generated/memos/T05_closure_memo.md`

## Acceptance criteria

- every material claim links to evidence;
- the briefing can be read in under ten minutes;
- no more than five main findings;
- risks and limitations are not hidden;
- suggested narrative is clearly marked as optional;
- no final recommendation appears;
- open questions require human judgment rather than mechanical analysis.

## Integrity checks

- no stale metric copied from an earlier run;
- selected model matches submission metadata;
- figures match current artifacts;
- references resolve;
- no claim exceeds the evidence;
- no causal language;
- artifact registry status is current.

## Closure memo

The T05 closure memo must declare:

- handoff complete or incomplete;
- missing evidence, if any;
- final selected model identifier;
- submission validation status;
- unresolved human decisions;
- explicit agent stop.

## Terminal condition

After Gate 05 passes:

> Stop execution. Do not write the final recommendation. Do not redesign the analysis unless the human reopens a named stage.
