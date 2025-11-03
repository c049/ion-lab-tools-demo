import pandas as pd

from ion_lab_tools.analysis.robustness import (
    evaluate_downsample_robustness,
    evaluate_noise_robustness,
    summarize_robustness,
)


def test_robustness_summary():
    series = pd.Series([float(i) for i in range(100)])
    noise_levels, noise_ratio = evaluate_noise_robustness(series, [0.0, 1.0, 2.0])
    factors, drifts = evaluate_downsample_robustness(series, [1, 2, 5])
    summary = summarize_robustness(noise_levels, noise_ratio, factors, drifts)
    assert summary.noise_slope >= 0
    assert summary.downsample_slope >= 0
