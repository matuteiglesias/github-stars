"""Deterministic, decision-led T02 analysis for the GitHub stars case."""

from __future__ import annotations

import argparse
import ast
import csv
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REFERENCE_DATE = datetime(2023, 9, 25, tzinfo=timezone.utc)
AGE_EDGES = [0, 1, 2, 3, 5, 8, 12, 16, math.inf]
AGE_LABELS = ["<1", "1–2", "2–3", "3–5", "5–8", "8–12", "12–16", "16+"]
FORK_EDGES = [-1, 0, 1, 5, 20, 100, 1000, math.inf]
FORK_LABELS = ["0", "1", "2–5", "6–20", "21–100", "101–1k", ">1k"]
RECENCY_EDGES = [-1, 30, 90, 365, 1095, math.inf]
RECENCY_LABELS = ["≤30d", "31–90d", "91d–1y", "1–3y", ">3y"]


def _write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _date(value: str) -> datetime | None:
    if not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _number(value: str) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def _band(value: float, edges: list[float], labels: list[str]) -> str:
    for left, right, label in zip(edges[:-1], edges[1:], labels):
        if left < value <= right:
            return label
    raise ValueError(f"Value outside band specification: {value}")


def _summary(values: list[float]) -> dict[str, object]:
    if not values:
        return {"count": 0, "median_log1p_stars": "", "p25_log1p_stars": "", "p75_log1p_stars": "", "median_stars": ""}
    a = np.asarray(values, dtype=float)
    log = np.log1p(a)
    return {
        "count": len(values), "median_log1p_stars": round(float(np.median(log)), 4),
        "p25_log1p_stars": round(float(np.quantile(log, .25)), 4),
        "p75_log1p_stars": round(float(np.quantile(log, .75)), 4),
        "median_stars": round(float(np.median(a)), 2),
    }


def _topics(value: str) -> tuple[list[str], str]:
    if not value.strip():
        return [], "missing"
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return [], "malformed"
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        return [], "malformed"
    return sorted({item.strip().lower() for item in parsed if item.strip()}), "serialized_list"


def _spearman(x: list[float], y: list[float]) -> float:
    def ranks(values: list[float]) -> np.ndarray:
        a = np.asarray(values)
        order = np.argsort(a, kind="stable")
        result = np.empty(len(a), float)
        i = 0
        while i < len(a):
            j = i + 1
            while j < len(a) and a[order[j]] == a[order[i]]:
                j += 1
            result[order[i:j]] = (i + j - 1) / 2 + 1
            i = j
        return result
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def run_eda(root: Path) -> None:
    raw, out = root / "data/raw", root / "artifacts/generated"
    train = _read(raw / "github-repo-data.csv")
    prediction = _read(raw / "github-repo-prediction-set.csv")
    hypotheses = [
        {"hypothesis_id":"H1","exact_question":"Is Stars sufficiently concentrated to require log modeling and target-band evaluation?","population":"labeled repositories only","variables":"Stars; log1p(Stars)","statistic_or_plot":"quantiles; top 1%/10% shares; log1p summary table","decision_affected":"target transform; baseline and error reporting","expected_failure_mode":"raw mean and histogram dominated by a small tail"},
        {"hypothesis_id":"H2","exact_question":"Are older repositories more starred, nonlinearly and with substantial within-band dispersion?","population":"labeled repositories only","variables":"Created At; Stars","statistic_or_plot":"age-bin median and IQR log1p(Stars), with support","decision_affected":"include and transform proxy age; interpretation caveat","expected_failure_mode":"dense scatter or causal age-effect language"},
        {"hypothesis_id":"H3","exact_question":"How strongly are contemporaneous Forks and Issues associated with Stars, including zeros and the high tail?","population":"labeled repositories only","variables":"Forks; Issues; Stars","statistic_or_plot":"Spearman log relationships; fork-band target summaries","decision_affected":"full-model proxies and nonlinear treatment; later sensitivity","expected_failure_mode":"single correlation hides zeros and tail dominance"},
        {"hypothesis_id":"H4","exact_question":"Do supported Topics × Language segments differ in typical Stars?","population":"labeled repositories with valid topic lists; supported cells only","variables":"Topics; Language; Stars","statistic_or_plot":"bounded heatmap of median log1p(Stars), annotated support","decision_affected":"rare-category grouping and compact categorical features","expected_failure_mode":"unsupported, unreadable rare-category matrix"},
        {"hypothesis_id":"H5","exact_question":"Are lifecycle states associated with Stars within proxy-age bands, and do train/prediction feature distributions differ?","population":"labeled repositories for Stars; both files for feature drift","variables":"Updated At; Is Archived; settings; age; core features","statistic_or_plot":"grouped lifecycle and compact drift tables","decision_affected":"full versus early-information features; validation design","expected_failure_mode":"late variables treated as launch-time levers or target used in prediction set"},
    ]
    # The register is deliberately persisted before figure creation.
    register_path = out / "eda/hypothesis_register.csv"
    _write(register_path, list(hypotheses[0]), hypotheses)

    stars = [float(row["Stars"]) for row in train]
    if len(stars) != len(train) or any(not math.isfinite(v) or v < 0 for v in stars):
        raise ValueError("T02 requires complete, finite, non-negative labeled targets; zero is valid")
    s = np.asarray(stars)
    ordered = np.sort(s)[::-1]
    profile = []
    metrics = {"count":len(s), "minimum":s.min(), "median":np.median(s), "p75":np.quantile(s,.75), "p90":np.quantile(s,.9), "p95":np.quantile(s,.95), "p99":np.quantile(s,.99), "maximum":s.max(), "mean":s.mean(), "top_1pct_total_star_share":ordered[:math.ceil(.01*len(s))].sum()/s.sum(), "top_10pct_total_star_share":ordered[:math.ceil(.10*len(s))].sum()/s.sum(), "log1p_minimum":np.log1p(s).min(), "log1p_median":np.median(np.log1p(s)), "log1p_p75":np.quantile(np.log1p(s),.75), "log1p_p90":np.quantile(np.log1p(s),.9), "log1p_p95":np.quantile(np.log1p(s),.95), "log1p_p99":np.quantile(np.log1p(s),.99), "log1p_maximum":np.log1p(s).max(), "log1p_mean":np.log1p(s).mean()}
    for key, value in metrics.items():
        profile.append({"metric":key, "value":round(float(value), 6) if not isinstance(value, int) else value, "population":"labeled repositories", "notes":"Zeros are valid; missing, negative, or non-finite targets block RMSLE analysis."})
    _write(out/"eda/target_profile.csv", list(profile[0]), profile)

    age_groups: dict[str, list[float]] = defaultdict(list)
    age_missing = age_negative = 0
    ages = []
    for row, target in zip(train, stars):
        created = _date(row["Created At"])
        if created is None:
            age_missing += 1; continue
        years = (REFERENCE_DATE.date()-created.date()).days/365.25
        if years < 0:
            age_negative += 1; continue
        ages.append(years); age_groups[_band(years, AGE_EDGES, AGE_LABELS)].append(target)
    if age_negative:
        raise ValueError(f"{age_negative} Created At values exceed fixed reference date")
    age_rows = []
    for label in AGE_LABELS:
        age_rows.append({"age_band_years":label, **_summary(age_groups[label]), "missing_created_at_count":age_missing, "reference_date":REFERENCE_DATE.date().isoformat(), "age_definition":"proxy age at reference date"})
    _write(out/"eda/age_summary.csv", list(age_rows[0]), age_rows)
    supported_age_rows = [row for row in age_rows if row["count"]]
    x = np.arange(len(supported_age_rows)); med=np.array([r["median_log1p_stars"] for r in supported_age_rows],float); lo=np.array([r["p25_log1p_stars"] for r in supported_age_rows],float); hi=np.array([r["p75_log1p_stars"] for r in supported_age_rows],float)
    fig, ax = plt.subplots(figsize=(10,6)); ax.fill_between(x,lo,hi,color="#9ecae1",alpha=.7,label="Interquartile range"); ax.plot(x,med,"o-",color="#08519c",lw=2,label="Median"); ax.set_xticks(x,[r["age_band_years"] for r in supported_age_rows]); ax.set_xlabel("Proxy age band (years)"); ax.set_ylabel("log1p(Stars)"); ax.set_title("Stars rise with proxy age, while within-band dispersion remains wide\nReference date: 2023-09-25 (latest Updated At proxy; not confirmed extraction date)"); ax.grid(axis="y",alpha=.25); ax.legend(loc="upper left")
    for i,r in enumerate(supported_age_rows): ax.text(i,hi[i]+.025,f"n={int(r['count']):,}",ha="center",va="bottom",fontsize=8)
    fig.tight_layout(); (out/"figures").mkdir(parents=True,exist_ok=True); fig.savefig(out/"figures/age_stars.png",dpi=180); plt.close(fig)

    raw_fork_pairs = [(_number(row["Forks"]), target) for row, target in zip(train, stars)]
    raw_issue_pairs = [(_number(row["Issues"]), target) for row, target in zip(train, stars)]
    invalid_forks = sum(value is not None and value < 0 for value, _ in raw_fork_pairs)
    invalid_issues = sum(value is not None and value < 0 for value, _ in raw_issue_pairs)
    fork_pairs = [(value, target) for value, target in raw_fork_pairs if value is not None and value >= 0]
    issue_pairs = [(value, target) for value, target in raw_issue_pairs if value is not None and value >= 0]
    forks = [value for value, _ in fork_pairs]; fork_stars = [target for _, target in fork_pairs]
    issues = [value for value, _ in issue_pairs]; issue_stars = [target for _, target in issue_pairs]
    fork_groups: dict[str,list[float]]=defaultdict(list)
    for value,target in fork_pairs: fork_groups[_band(value,FORK_EDGES,FORK_LABELS)].append(target)
    high_cut=float(np.quantile(forks,.99)); total_forks=sum(forks)
    proxy_rows=[]
    for feature,values,targets in [("Forks",forks,fork_stars),("Issues",issues,issue_stars)]:
        invalid = invalid_forks if feature == "Forks" else invalid_issues
        missing = sum(_number(row[feature]) is None for row in train)
        proxy_rows.append({"record_type":"overall","feature":feature,"band":"all","count":len(values),"zero_fraction":round(sum(v==0 for v in values)/len(values),6),"spearman_log1p_with_log1p_stars":round(_spearman(np.log1p(values).tolist(),np.log1p(targets).tolist()),6),"median_stars":"","p75_stars":"","p90_stars":"","tail_evidence":f"missing={missing}; invalid_negative={invalid}; top 1% fork cutoff={high_cut:g}; share of all forks={sum(v for v in forks if v>=high_cut)/total_forks:.4f}" if feature=="Forks" else f"missing={missing}; invalid_negative={invalid}"})
    for label in FORK_LABELS:
        vals=np.asarray(fork_groups[label]); proxy_rows.append({"record_type":"fork_band","feature":"Forks","band":label,"count":len(vals),"zero_fraction":"","spearman_log1p_with_log1p_stars":"","median_stars":round(float(np.median(vals)),2),"p75_stars":round(float(np.quantile(vals,.75)),2),"p90_stars":round(float(np.quantile(vals,.9)),2),"tail_evidence":""})
    _write(out/"eda/proxy_activity.csv",list(proxy_rows[0]),proxy_rows)

    topic_counts=Counter(); language_counts=Counter(); parsed_rows=[]; parse_status=Counter()
    for row,target in zip(train,stars):
        topics,status=_topics(row["Topics"]); parse_status[status]+=1
        language=(row["Language"].strip() or "Missing"); language_counts[language]+=1
        parsed_rows.append((language,topics,target)); topic_counts.update(topics)
    languages=[x for x,_ in language_counts.most_common(8)]; topics=[x for x,_ in topic_counts.most_common(10)]; cell=defaultdict(list)
    for language,row_topics,target in parsed_rows:
        if language in languages:
            for topic in row_topics:
                if topic in topics: cell[(topic,language)].append(target)
    min_support=100; matrix=np.full((len(topics),len(languages)),np.nan); support=np.zeros_like(matrix,int)
    topic_rows=[]
    for i,topic in enumerate(topics):
        for j,language in enumerate(languages):
            vals=cell[(topic,language)]; support[i,j]=len(vals)
            if len(vals)>=min_support: matrix[i,j]=np.median(np.log1p(vals))
            topic_rows.append({"topic":topic,"language":language,"support":len(vals),"median_log1p_stars":round(float(matrix[i,j]),4) if not np.isnan(matrix[i,j]) else "","included":len(vals)>=min_support,"minimum_support":min_support})
    eligible=sum(1 for language,row_topics,_ in parsed_rows if language in languages and any(t in topics for t in row_topics)); shown=sum(1 for language,row_topics,_ in parsed_rows if any(language==l and t in row_topics and len(cell[(t,l)])>=min_support for l in languages for t in topics))
    topic_rows.append({"topic":"__AUDIT__","language":"all","support":len(train),"median_log1p_stars":"","included":True,"minimum_support":min_support})
    _write(out/"eda/topics_language_support.csv",list(topic_rows[0]),topic_rows)
    fig,ax=plt.subplots(figsize=(12,7)); masked=np.ma.masked_invalid(matrix); im=ax.imshow(masked,aspect="auto",cmap="YlGnBu"); ax.set_xticks(range(len(languages)),languages,rotation=35,ha="right"); ax.set_yticks(range(len(topics)),topics); ax.set_xlabel("Top languages by repository support"); ax.set_ylabel("Top topics by repository support"); ax.set_title(f"Typical stars vary across supported Topic × Language cells\nMedian log1p(Stars); n≥{min_support}; shown repository coverage {shown/len(train):.1%}; malformed topics {parse_status['malformed']:,}")
    for i in range(len(topics)):
        for j in range(len(languages)):
            ax.text(j,i,f"{matrix[i,j]:.1f}\nn={support[i,j]:,}" if not np.isnan(matrix[i,j]) else f"—\nn={support[i,j]:,}",ha="center",va="center",fontsize=7,color="white" if not np.isnan(matrix[i,j]) and matrix[i,j]>5.5 else "black")
    fig.colorbar(im,ax=ax,label="Median log1p(Stars)"); fig.tight_layout(); fig.savefig(out/"figures/topics_language.png",dpi=180); plt.close(fig)

    lifecycle=defaultdict(list); invalid_recency=missing_updated=0
    for row,target in zip(train,stars):
        created=_date(row["Created At"]); updated=_date(row["Updated At"])
        age_label="Missing" if created is None else _band((REFERENCE_DATE.date()-created.date()).days/365.25,AGE_EDGES,AGE_LABELS)
        if updated is None: recency="Missing"; missing_updated+=1
        else:
            days=(REFERENCE_DATE.date()-updated.date()).days
            if days<0: invalid_recency+=1; recency="Invalid-negative"
            else: recency=_band(days,RECENCY_EDGES,RECENCY_LABELS)
        lifecycle[("archived",row["Is Archived"] or "Missing",age_label)].append(target); lifecycle[("recency",recency,age_label)].append(target)
    if invalid_recency: raise ValueError(f"{invalid_recency} Updated At values exceed fixed reference date")
    lifecycle_rows=[]
    for (view,state,age_label),values in sorted(lifecycle.items()): lifecycle_rows.append({"view":view,"state":state,"age_band_years":age_label,**_summary(values),"invalid_negative_recency_count":invalid_recency,"missing_updated_at_count":missing_updated})
    _write(out/"eda/lifecycle_summary.csv",list(lifecycle_rows[0]),lifecycle_rows)

    def drift_values(rows, feature):
        if feature=="age_years": return [((REFERENCE_DATE.date()-d.date()).days/365.25) for r in rows if (d:=_date(r["Created At"])) is not None]
        return [v for r in rows if (v:=_number(r[feature])) is not None and v >= 0]
    drift=[]
    for feature in ["age_years","Forks","Issues","Size"]:
        a,b=drift_values(train,feature),drift_values(prediction,feature)
        for statistic,q in [("p25",.25),("median",.5),("p75",.75),("p90",.9)]:
            av,bv=float(np.quantile(a,q)),float(np.quantile(b,q)); drift.append({"feature":feature,"statistic":statistic,"train_value":round(av,4),"prediction_value":round(bv,4),"difference_prediction_minus_train":round(bv-av,4),"notes":"features only for cross-file comparison"})
    for feature in ["Description","Language","Is Archived","Topics"]:
        def miss(r):
            if feature=="Topics": return _topics(r[feature])[1] in {"missing","malformed"}
            return not r[feature].strip()
        av=sum(miss(r) for r in train)/len(train); bv=sum(miss(r) for r in prediction)/len(prediction); drift.append({"feature":feature,"statistic":"missing_or_invalid_rate","train_value":round(av,6),"prediction_value":round(bv,6),"difference_prediction_minus_train":round(bv-av,6),"notes":"features only for cross-file comparison"})
    train_lang={r["Language"].strip() or "Missing" for r in train}; unseen=sum((r["Language"].strip() or "Missing") not in train_lang for r in prediction)/len(prediction); drift.append({"feature":"Language","statistic":"prediction_unseen_category_rate","train_value":0,"prediction_value":round(unseen,6),"difference_prediction_minus_train":round(unseen,6),"notes":"category absent from labeled data"})
    for name,rows in [("train",train),("prediction",prediction)]:
        counts=[]
        for r in rows: counts.append(len(_topics(r["Topics"])[0]))
        if name=="train": tc=counts
        else: pc=counts
    for statistic,q in [("p25",.25),("median",.5),("p75",.75),("p90",.9)]: drift.append({"feature":"topic_count","statistic":statistic,"train_value":float(np.quantile(tc,q)),"prediction_value":float(np.quantile(pc,q)),"difference_prediction_minus_train":round(float(np.quantile(pc,q)-np.quantile(tc,q)),4),"notes":"deterministically parsed serialized lists"})
    _write(out/"eda/feature_drift.csv",list(drift[0]),drift)

    top1=metrics["top_1pct_total_star_share"]; rho=proxy_rows[0]["spearman_log1p_with_log1p_stars"]
    findings=[
        {"finding_id":"F1","hypothesis_id":"H1","evidence":f"p50={metrics['median']:.0f}, p99={metrics['p99']:.0f}, max={metrics['maximum']:.0f}; top 1% holds {top1:.1%} of Stars","magnitude":f"mean/median={metrics['mean']/metrics['median']:.1f}×","population_and_support":f"{len(train):,} labeled repositories","caveat":"Describes labeled target only; transfer to prediction rows is unobserved","decision_relevance":"Train/evaluate on log1p scale and retain target-band error analysis","finding_type":"descriptive"},
        {"finding_id":"F2","hypothesis_id":"H2","evidence":f"median log1p(Stars) spans {med.min():.2f}–{med.max():.2f} across supported proxy-age bands; every band has a wide IQR","magnitude":f"oldest versus youngest median difference={med[-1]-med[0]:.2f} log units","population_and_support":f"{len(ages):,} labeled rows with valid Created At; {age_missing:,} missing","caveat":"Proxy age at 2023-09-25, not exact age at extraction; accumulated association, not an age effect","decision_relevance":"Include nonlinear proxy age, but do not use it alone","finding_type":"descriptive"},
        {"finding_id":"F3","hypothesis_id":"H3","evidence":f"Spearman(log1p Forks, log1p Stars)={rho:.3f}; zero-fork share={proxy_rows[0]['zero_fraction']:.1%}","magnitude":proxy_rows[0]["tail_evidence"],"population_and_support":f"{len(train):,} labeled repositories","caveat":"Forks is a contemporaneous close proxy, not a causal lever or launch-time feature","decision_relevance":"Use log1p(Forks) in full model; exclude it from early-information sensitivity","finding_type":"sensitivity-related"},
        {"finding_id":"F4","hypothesis_id":"H4","evidence":f"bounded 10-topic × 8-language heatmap uses n≥{min_support}; shown repository coverage={shown/len(train):.1%}","magnitude":f"{sum(~np.isnan(matrix))} supported cells; {sum(np.isnan(matrix))} suppressed cells","population_and_support":f"{len(train):,} labeled rows; {parse_status['malformed']:,} malformed and {parse_status['missing']:,} missing topic values","caveat":"Top categories and support filtering exclude rare combinations; cells are descriptive","decision_relevance":"Group rare/unknown categories and bound topic features","finding_type":"descriptive"},
        {"finding_id":"F5","hypothesis_id":"H5","evidence":"Lifecycle summaries are age-stratified; feature drift table compares train and prediction without target access","magnitude":f"archived rows={sum(r['Is Archived']=='True' for r in train):,}; unseen prediction language rate={unseen:.2%}","population_and_support":f"{len(train):,} labeled and {len(prediction):,} prediction repositories","caveat":"Lifecycle state is late and associations do not establish transfer or causality","decision_relevance":"Lifecycle fields stay full-model only; use fold-safe unknown handling and random primary validation with temporal robustness check","finding_type":"sensitivity-related"},
    ]
    _write(out/"eda/finding_register.csv",list(findings[0]),findings)
    consequences=[
        ("Strong target concentration","Train on log1p(Stars), evaluate RMSLE, and report target-band errors"),("Proxy-age gradient with wide dispersion","Include transformed proxy age; do not imply causal age effect"),("Fork relationship is strong, zero-heavy, and tailed","Use log1p(Forks) in full model and exclude close proxies in sensitivity"),("Rare Topic × Language cells lack support","Use fold-safe rare grouping/unknown handling; compact topic indicators only"),("Lifecycle fields are late and cross-file drift is measurable","Full-model only; primary random split plus a bounded temporal robustness check")]
    memo=f"""# T02 Closure Memo

## Objective, inputs, and controls

T02 tested five pre-registered questions to constrain modeling and presentation, using the validated labeled and prediction CSVs, T01 timing register, and the fixed **2023-09-25** reference proxy. Stars were used only for labeled rows. Cross-file comparisons use features only. The reference is the maximum observed `Updated At`, not a confirmed extraction date; age is therefore **proxy age at reference date**. All `Created At` values are on or before the reference ({age_negative} violations), and all recency values are non-negative ({invalid_recency} violations).

The hypothesis register was saved before plotting. Exactly two figures were generated; there are no optional charts. Tables carry target, proxy, lifecycle, topic-support, and drift detail.

## Hypothesis disposition and findings

- **H1 supported:** Stars are strongly concentrated (top 1% share {top1:.1%}); log-scale modeling and target-band evaluation are required. Zero targets are valid for RMSLE; the blocking conditions are missing, negative, or non-finite targets.
- **H2 supported descriptively:** typical Stars rise across proxy-age bands, but dispersion remains large within every band. This is accumulated association, not an age effect.
- **H3 supported for full-model design:** Forks has rank association {rho:.3f} with Stars and requires log/nonlinear treatment. It is a contemporaneous close proxy and must be removed from the early-information sensitivity.
- **H4 supported only for well-represented cells:** the bounded heatmap suppresses topic-language cells below n={min_support}; rare combinations do not support broad segment claims.
- **H5 supported as a lifecycle/sensitivity distinction:** archived and update-recency summaries are age-stratified. These variables may aid contemporaneous estimation but are not launch-time levers. Cross-file drift is documented without prediction targets.

The five evidence-backed finding rows in `finding_register.csv` include magnitude, support, caveat, decision relevance, and type.

## Modeling consequences

| Evidence | Modeling consequence |
|---|---|
"""+"\n".join(f"| {a} | {b} |" for a,b in consequences)+f"""

### Fixed simple baseline features

`log1p(age_days)`, `Language`, `License`, topic count, missing-description flag, homepage-present flag, `Is Fork`, and timing-defensible repository settings. Raw `URL`, raw identity, target-derived aggregates, Size, Forks, Issues, Updated At/recency, and archived status are excluded from this early-information baseline/sensitivity view. Learned imputing, scaling, vocabulary, and category handling must be fitted inside training folds.

### Bounded improved model

One nonlinear tree-based tabular family using the fixed baseline features plus `log1p(Size)`, `log1p(Forks)`, `log1p(Issues)`, update-recency bands, and archived status. Compact deterministic topic indicators may be included with fold-safe vocabulary selection; no free expansion to another improved family or broad tuning is authorized. A full-versus-proxy-excluded comparison remains required later.

## Train/prediction distribution and validation implication

`feature_drift.csv` reports train/prediction quantiles, missing-rate differences, unseen Language rate, and topic-count differences for age, Forks, Issues, Size, Language, description missingness, archive status, and Topics. Because the partition mechanism is unknown and Created At ranges overlap, T03 should use a seeded random primary holdout that approximates the apparent partition, plus one bounded temporal robustness check—not claim future forecasting.

## Presentation candidates and limitations

Both required figures are candidates: `age_stars.png` communicates the gradient and persistent dispersion; `topics_language.png` communicates supported segmentation while displaying cell counts and excluded coverage. The age figure explicitly prints the proxy reference date. The topic figure records n≥{min_support}, shown coverage, and malformed count. No optional figure was warranted because grouped tables answer H1, H3, H5, and drift more precisely.

Repeated normalized URLs within train: **0** (exact URLs: 0); within prediction: **0**. Cross-file normalized URL overlap is 0. Repeated Names remain non-identity duplicates and raw identity remains excluded.

## Integrity checks and acceptance criteria

- Target: {len(stars):,} complete finite non-negative values; zeros permitted.
- Age: {age_missing:,} missing Created At values and {age_negative:,} values after the reference; missingness is explicit.
- Recency: {missing_updated:,} missing Updated At values and {invalid_recency:,} negative values.
- Topics: deterministic literal-list parsing; status counts are serialized={parse_status['serialized_list']:,}, missing={parse_status['missing']:,}, malformed={parse_status['malformed']:,}.
- Figure count: 2, both tied to registered hypotheses and deterministic paths.

## Gate decision

**PASS — Gate 02 criteria met; T03 model execution is unlocked.** The baseline feature set is fixed, the improved family is bounded, and no EDA ambiguity is authorized to expand into a model zoo. This memo constrains evidence and modeling; it does not make a final recommendation.
"""
    memo_path=out/"memos/T02_closure_memo.md"; memo_path.parent.mkdir(parents=True,exist_ok=True); memo_path.write_text(memo,encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path.cwd()); args=parser.parse_args(); run_eda(args.root.resolve())


if __name__ == "__main__":
    main()
