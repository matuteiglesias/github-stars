# T02 Closure Memo

## Objective, inputs, and controls

T02 tested five pre-registered questions to constrain modeling and presentation, using the validated labeled and prediction CSVs, T01 timing register, and the fixed **2023-09-25** reference proxy. Stars were used only for labeled rows. Cross-file comparisons use features only. The reference is the maximum observed `Updated At`, not a confirmed extraction date; age is therefore **proxy age at reference date**. All `Created At` values are on or before the reference (0 violations), and all recency values are non-negative (0 violations).

The hypothesis register was saved before plotting. Exactly two figures were generated; there are no optional charts. Tables carry target, proxy, lifecycle, topic-support, and drift detail.

## Hypothesis disposition and findings

- **H1 supported:** Stars are strongly concentrated (top 1% share 24.5%); log-scale modeling and target-band evaluation are required. Zero targets are valid for RMSLE; the blocking conditions are missing, negative, or non-finite targets.
- **H2 supported descriptively:** typical Stars rise across proxy-age bands, but dispersion remains large within every band. This is accumulated association, not an age effect.
- **H3 supported for full-model design:** Forks has rank association 0.642 with Stars and requires log/nonlinear treatment. It is a contemporaneous close proxy and must be removed from the early-information sensitivity.
- **H4 supported only for well-represented cells:** the bounded heatmap suppresses topic-language cells below n=100; rare combinations do not support broad segment claims.
- **H5 supported as a lifecycle/sensitivity distinction:** archived and update-recency summaries are age-stratified. These variables may aid contemporaneous estimation but are not launch-time levers. Cross-file drift is documented without prediction targets.

The five evidence-backed finding rows in `finding_register.csv` include magnitude, support, caveat, decision relevance, and type.

## Modeling consequences

| Evidence | Modeling consequence |
|---|---|
| Strong target concentration | Train on log1p(Stars), evaluate RMSLE, and report target-band errors |
| Proxy-age gradient with wide dispersion | Include transformed proxy age; do not imply causal age effect |
| Fork relationship is strong, zero-heavy, and tailed | Use log1p(Forks) in full model and exclude close proxies in sensitivity |
| Rare Topic × Language cells lack support | Use fold-safe rare grouping/unknown handling; compact topic indicators only |
| Lifecycle fields are late and cross-file drift is measurable | Full-model only; primary random split plus a bounded temporal robustness check |

### Fixed simple baseline features

`log1p(age_days)`, `Language`, `License`, topic count, missing-description flag, homepage-present flag, `Is Fork`, and timing-defensible repository settings. Raw `URL`, raw identity, target-derived aggregates, Size, Forks, Issues, Updated At/recency, and archived status are excluded from this early-information baseline/sensitivity view. Learned imputing, scaling, vocabulary, and category handling must be fitted inside training folds.

### Bounded improved model

One nonlinear tree-based tabular family using the fixed baseline features plus `log1p(Size)`, `log1p(Forks)`, `log1p(Issues)`, update-recency bands, and archived status. Compact deterministic topic indicators may be included with fold-safe vocabulary selection; no free expansion to another improved family or broad tuning is authorized. A full-versus-proxy-excluded comparison remains required later.

## Train/prediction distribution and validation implication

`feature_drift.csv` reports train/prediction quantiles, missing-rate differences, unseen Language rate, and topic-count differences for age, Forks, Issues, Size, Language, description missingness, archive status, and Topics. Because the partition mechanism is unknown and Created At ranges overlap, T03 should use a seeded random primary holdout that approximates the apparent partition, plus one bounded temporal robustness check—not claim future forecasting.

## Presentation candidates and limitations

Both required figures are candidates: `age_stars.png` communicates the gradient and persistent dispersion; `topics_language.png` communicates supported segmentation while displaying cell counts and excluded coverage. The age figure explicitly prints the proxy reference date. The topic figure records n≥100, shown coverage, and malformed count. No optional figure was warranted because grouped tables answer H1, H3, H5, and drift more precisely.

Repeated normalized URLs within train: **0** (exact URLs: 0); within prediction: **0**. Cross-file normalized URL overlap is 0. Repeated Names remain non-identity duplicates and raw identity remains excluded.

## Integrity checks and acceptance criteria

- Target: 150,520 complete finite non-negative values; zeros permitted.
- Age: 0 missing Created At values and 0 values after the reference; missingness is explicit.
- Recency: 0 missing Updated At values and 0 negative values.
- Topics: deterministic literal-list parsing; status counts are serialized=150,520, missing=0, malformed=0.
- Figure count: 2, both tied to registered hypotheses and deterministic paths.

## Gate decision

**PASS — Gate 02 criteria met; T03 model execution is unlocked.** The baseline feature set is fixed, the improved family is bounded, and no EDA ambiguity is authorized to expand into a model zoo. This memo constrains evidence and modeling; it does not make a final recommendation.
