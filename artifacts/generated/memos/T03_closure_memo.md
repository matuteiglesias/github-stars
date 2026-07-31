# T03 Closure Memo — Baseline Modeling and Model Selection

## Objective, inputs, and fixed design

T03 answered whether contemporaneous activity, size, recency, lifecycle, and nonlinear structure materially improve out-of-sample RMSLE over the early-information baseline. Inputs were the T01-validated labeled and prediction files, feature-timing register, and T02 feature contract. Seed **202503** defines one 80/20 random holdout (120,416 fit; 30,104 validation). All learned preprocessing is fitted after splitting. Raw Name, URL, repository identity, target-derived features, description text, and a topic vocabulary are excluded.

The temporal check fits the oldest 80% by `Created At` and evaluates the newest 20%. It is a **robustness stress test under temporal shift**, not the primary challenge estimate and not evidence that this task is future forecasting. The primary holdout alone selects the candidate.

## Model ladder and primary evidence

| Candidate | Timing view | Primary RMSLE | Median absolute log error | Within 2× | Within 10× | Temporal RMSLE |
|---|---|---:|---:|---:|---:|---:|
| M0 log-target mean | training-target-only constant | 0.9932 | 0.6748 | 51.4% | 96.3% | n/a |
| M1 Ridge | early-information | 0.9429 | 0.6126 | 56.4% | 97.1% | 0.9552 |
| M2 histogram gradient boosting | full contemporaneous | **0.5286** | **0.3296** | **83.5%** | **99.9%** | **0.5529** |

M0 verifies log-metric and prediction plumbing. M1 adds limited signal but remains weak in the high-star tail. Of two predeclared M2 configurations, the selected 140-iteration configuration scored 0.5286 versus 0.5380 for the smaller configuration; no broader search was run.

M2 improves RMSLE over M1 by **0.4143 absolute, or 43.9% relative**. Score-change labels are fixed as: **negligible** = under 0.01 absolute and under 2% relative; **modest** = 0.01–0.05 absolute or 2–10% relative; **material** = over 0.05 absolute and over 10% relative. By that declared rule the gain is **material**, and its magnitude outweighs the bounded implementation complexity. This is predictive comparison, not causal attribution.

## Timing sensitivity and interpretation boundary

M1 is the early-information interpretive/sensitivity view. M2 is the challenge model because it uses snapshot-available `log1p(Size)`, `log1p(Forks)`, `log1p(Issues)`, update recency, and archived state, with nonlinear structure. The gain is conceptually consistent with close popularity/activity proxies—especially Forks—but this comparison does not isolate each addition and must not be described as feature causality.

Including those proxies removes any basis for claims about predicting future success at repository creation or recommending actions that cause Stars. M2 estimates contemporaneous Stars from contemporaneous metadata. No topic indicators were retained: deterministic topic count captures bounded metadata breadth, while a learned topic vocabulary was not necessary to establish a large tabular gain.

Temporal RMSLE degrades from 0.5286 to 0.5529 for M2 (4.6%), versus 0.9429 to 0.9552 for M1 (1.3%). M2 is somewhat less stable proportionally, but remains directionally credible and substantially stronger than M1 under the stress test. This qualifies confidence without changing selection.

## Segment evidence and failure taxonomy

M2 RMSLE is 0.4649 for the supported 100–999 band, 0.7295 for 1,000–9,999, and 0.6819 for 10,000+ (only 462 validation rows). The high-star bands therefore retain the largest practical risk even though M2 sharply reduces M1's 3.2443 RMSLE for 10,000+. M2 is stable across proxy-age bands (0.5120–0.5339), description status (0.4955–0.5299), and archive state (0.5281–0.5286). Rare-or-unseen language support is slightly worse (0.5537, n=768) than common support (0.5279).

Inspection of the largest absolute log errors produced this compact taxonomy:

1. **Activity–popularity mismatch:** repositories with hundreds or thousands of forks but only hundreds of Stars are strongly overpredicted.
2. **Historically popular, low-current-proxy repositories:** several older high-Star repositories with comparatively few forks/issues are underpredicted.
3. **Extreme-star tail:** the sparse 10,000+ band remains difficult despite major improvement.
4. **Young or unusual metadata profiles:** some young repositories with high proxy activity, and rare-language cases, produce large errors.
5. **Zero-issue exceptions:** older repositories with high Stars but zero or very few recorded issues appear among large underpredictions.

No repository-specific prediction was manually changed. Archived-state aggregate error is not elevated, although historically popular metadata exceptions remain possible.

## Selection, artifacts, and integrity checks

**Selected candidate: M2, the full contemporaneous histogram gradient-boosting pipeline.** This is a machine-side model-selection result, not a final business recommendation. The pipeline was refitted on all 150,520 labeled rows. It generated 64,502 continuous, finite, non-negative predictions in original prediction-row order. The submission schema is exactly `Name,Stars`; predictions are attached positionally and are not joined on Name. The large row-level validation and submission files are reproducibly generated but intentionally excluded from version control.

Saved evidence includes the split manifest, three-row model comparison, row-level validation predictions, segment table, selected-model metadata, submission candidate, and submission validation report. Target bands remained the predeclared zero-inclusive boundaries; the dataset supplies no validation rows below 100 Stars, so unsupported bands are absent rather than silently pooled.

Integrity checks passed: target validity; split-before-fit; no URL overlap; no identity or target feature; fold-safe imputation/encoding/scaling; safe unknown categories; untouched primary validation; non-negative inverse-transform; exact submission schema, row count, order, null, finite, precision, and accidental-index checks.

## Acceptance decision and human handoff

**PASS — Gate 03 is closed and deterministic prediction generation is unlocked.** Stop tuning: M0, M1, and exactly one improved family were evaluated; primary and temporal evidence is saved; segment risks are understood; and no critical leakage or identity issue remains.

Questions reserved for the human consultant:

1. Is a 43.9% relative RMSLE improvement large enough to lead with, given the contemporaneous interpretation?
2. Should the presentation describe M1 as the interpretive model and M2 as the challenge model?
3. Does M2's 4.6% temporal degradation materially weaken confidence?
4. Should the 1,000–9,999/high-tail segment be emphasized as the largest practical risk?
5. Is there any presentation value in topic complexity when it was not needed for selection?
6. Does the human approve M2 for the final submission workflow?
