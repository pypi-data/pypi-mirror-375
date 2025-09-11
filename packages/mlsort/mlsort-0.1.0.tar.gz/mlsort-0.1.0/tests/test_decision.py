from mlsort.decision import decide
from mlsort.installer import load_thresholds


def test_decision_pipeline():
    th = load_thresholds("artifacts/thresholds.json")
    # small n (below cutoff) should pick timsort
    n_small = max(2, th.cutoff_n - 1)
    arr_small = list(range(n_small, 0, -1))
    assert decide(arr_small, th) == "timsort"

    # small-range ints should allow valid algorithm from the supported set
    import numpy as np
    arr_sr = np.random.randint(0, 64, size=4000, dtype=np.int32)
    algo = decide(arr_sr, th)
    assert algo in {"timsort", "np_quick", "np_merge", "counting", "radix"}
