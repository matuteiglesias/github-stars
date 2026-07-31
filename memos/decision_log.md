# Decision Log

| ID | Decision | Rationale | Reopen trigger |
|---|---|---|---|
| D-001 | Treat task as contemporaneous star estimation. | No future target horizon is specified. | Evidence of future target timestamps or explicit forecasting instruction. |
| D-002 | Separate prediction, description, and causation. | Predictive associations do not identify causal popularity factors. | A valid causal design or intervention data is supplied. |
| D-003 | Use supplied data only. | External GitHub lookup could recover the target and break case integrity. | Interviewer explicitly authorizes external enrichment and defines boundaries. |
| D-004 | Treat `URL` as identity, not a production feature. | High memorization and leakage risk. | Controlled identity feature is explicitly required and validated. |
| D-005 | Do not assume `Name` is unique. | Repository names may repeat across owners. | T01 proves uniqueness across all relevant files. |
| D-006 | Fix the age reference date. | `datetime.now()` would make results drift across runs. | Dataset provides a more authoritative extraction timestamp. |
| D-007 | Use one baseline and one improvement. | Time-constrained consulting value exceeds model breadth. | Baseline failure reveals one bounded alternative is necessary. |
| D-008 | Human owns final recommendation. | Recommendation requires judgment and presentation strategy. | Human explicitly delegates a bounded draft after handoff. |
