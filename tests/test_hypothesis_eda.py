import math

import numpy as np

from src.case_bundle.hypothesis_eda import _band, _spearman, _topics


def test_topic_parser_is_deterministic_and_rejects_non_lists():
    assert _topics("['Python', 'api', 'Python']") == (["api", "python"], "serialized_list")
    assert _topics("") == ([], "missing")
    assert _topics("{'topic': 'python'}") == ([], "malformed")


def test_bands_include_zero_and_expected_boundaries():
    assert _band(0, [-1, 0, 1, math.inf], ["zero", "one", "many"]) == "zero"
    assert _band(1, [-1, 0, 1, math.inf], ["zero", "one", "many"]) == "one"


def test_spearman_handles_ties():
    actual = _spearman([0, 1, 1, 3], [0, 2, 2, 9])
    assert np.isclose(actual, 1.0)
