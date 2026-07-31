import numpy as np
import pandas as pd

from src.case_bundle.modeling import TARGET_BINS, TARGET_LABELS, _metrics, _topics


def test_target_bands_are_zero_inclusive_and_non_overlapping():
    values = pd.cut(
        [0, 9, 10, 99, 100, 999, 1000, 9999, 10000], TARGET_BINS, labels=TARGET_LABELS
    )
    assert values.astype(str).tolist() == [
        "0–9",
        "0–9",
        "10–99",
        "10–99",
        "100–999",
        "100–999",
        "1,000–9,999",
        "1,000–9,999",
        "10,000+",
    ]


def test_metrics_are_log_aligned_and_exact_predictions_score_zero():
    actual = np.array([0.0, 9.0, 99.0])
    result = _metrics(actual, np.log1p(actual))
    assert result == {
        "rmsle": 0.0,
        "median_absolute_log_error": 0.0,
        "within_2x_pct": 100.0,
        "within_10x_pct": 100.0,
    }


def test_topic_count_is_deterministic_and_malformed_is_explicit_zero():
    assert _topics("['Python', 'api', 'Python']") == 2
    assert _topics("not-a-list") == 0
