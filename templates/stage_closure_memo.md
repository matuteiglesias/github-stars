# Stage Closure Memo Contract

Use this exact structure for every generated stage memo.

## Stage

State task identifier and name.

## Status

Choose exactly one:

- `passed`
- `passed-with-bounded-risk`
- `blocked`
- `reopened`

## Objective

Restate the stage objective in one sentence.

## Inputs used

List the concrete files, tables, and prior decisions used.

## Artifacts produced

List exact repository paths.

## Evidence and findings

Record only claims supported by the listed artifacts.

For each finding include:

- claim;
- evidence path;
- magnitude or result;
- implication.

## Integrity checks

List each required check as:

- check;
- result;
- evidence.

## Limitations and unresolved issues

For each issue include:

- severity;
- consequence;
- mitigation;
- whether it blocks the next stage.

## Decision

State what was decided and what was deliberately not decided.

## Gate evaluation

List each acceptance criterion and pass/fail status.

## Next stage

State exactly one:

- next stage unlocked;
- next stage blocked;
- prior stage reopened.

Include the reason.

## Run metadata

Record:

- run identifier;
- timestamp;
- code version or commit when available;
- random seed when relevant;
- agent or author.
