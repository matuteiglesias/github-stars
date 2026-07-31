import numpy as np
import pandas as pd
import pytest

from src.case_bundle.contracts import validate_submission
from src.case_bundle.metrics import rmsle

def test_rmsle_is_zero_for_exact_predictions():
    y = np.array([0.0, 1.0, 10.0, 100.0])
    assert rmsle(y, y) == pytest.approx(0.0)

def test_rmsle_rejects_negative_values():
    with pytest.raises(ValueError):
        rmsle(np.array([1.0]), np.array([-1.0]))

def test_valid_submission_passes():
    prediction_frame = pd.DataFrame({"Name": ["a", "a", "b"]})
    submission = pd.DataFrame({
        "Name": ["a", "a", "b"],
        "Stars": [1.2, 3.4, 0.0],
    })
    report = validate_submission(submission, prediction_frame)
    assert report["valid"] is True
    assert report["row_count_matches"] is True
    assert report["name_order_matches"] is True

def test_submission_rejects_wrong_order():
    prediction_frame = pd.DataFrame({"Name": ["a", "b"]})
    submission = pd.DataFrame({"Name": ["b", "a"], "Stars": [1.0, 2.0]})
    report = validate_submission(submission, prediction_frame)
    assert report["valid"] is False
    assert report["name_order_matches"] is False

def test_submission_rejects_negative_predictions():
    prediction_frame = pd.DataFrame({"Name": ["a"]})
    submission = pd.DataFrame({"Name": ["a"], "Stars": [-0.1]})
    report = validate_submission(submission, prediction_frame)
    assert report["valid"] is False
    assert report["non_negative"] is False
