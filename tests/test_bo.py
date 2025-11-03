import pandas as pd

from ion_lab_tools.analysis.bo import compare_methods


def test_compare_methods():
    data = pd.DataFrame(
        {
            "method": ["bo", "bo", "bo", "random", "random", "grid", "grid"],
            "step": [1, 2, 3, 1, 2, 1, 2],
            "score": [0.5, 0.7, 0.9, 0.4, 0.45, 0.42, 0.48],
        }
    )
    result = compare_methods(data, target=0.8)
    assert result.step_reduction >= 0
    assert result.terminal_gain >= 0
