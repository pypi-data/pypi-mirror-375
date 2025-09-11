import numpy as np

from mlsort.features import estimate_properties


def test_estimate_properties_simple():
    x = [1, 2, 3, 4]
    props = estimate_properties(x)
    assert props["n"] == 4
    assert props["dtype_code"] == 1  # int
    assert props["est_sortedness"] >= 0.9
    assert props["est_dup_ratio"] <= 0.1
    assert props["est_range"] >= 3
    assert props["est_entropy"] >= 0
    assert props["est_run_len"] >= 2
