import numpy as np
import pandas as pd

from ion_lab_tools.analysis.forecast import ar1_forecast


def test_ar1_forecast_shapes():
    rng = np.random.default_rng(0)
    base = np.cumsum(rng.normal(scale=5, size=120))
    series = pd.Series(base)
    result = ar1_forecast(series, sample_period=1.0, steps_ahead=12, alert_threshold=50)
    assert result.forecast.shape == (12,)
    assert result.mae >= 0
    assert result.mape >= 0
