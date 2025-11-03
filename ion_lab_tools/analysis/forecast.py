"""Simple forecasting utilities for drift/lead-time analysis."""

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd


@dataclass
class ForecastResult:
    forecast: np.ndarray
    horizon_seconds: float
    mae: float
    mape: float
    lead_time_seconds: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "forecast_mae": float(self.mae),
            "forecast_mape": float(self.mape),
            "forecast_lead_seconds": float(self.lead_time_seconds),
        }


def ar1_forecast(series: pd.Series, sample_period: float, steps_ahead: int, alert_threshold: float) -> ForecastResult:
    """
    Fit a simple AR(1)+bias model and forecast forward.

    Parameters
    ----------
    series : pd.Series
        Recent measurements of a metric (e.g., lock error).
    sample_period : float
        Sampling period (seconds).
    steps_ahead : int
        Number of future steps to predict.
    alert_threshold : float
        Threshold to trigger a warning (absolute value).
    """

    y = series.to_numpy(dtype=float)
    if y.size < 10:
        raise ValueError("Need at least 10 samples for AR(1) forecast")

    y0 = y[:-1]
    y1 = y[1:]

    # Solve for AR(1) with bias using least squares: y1 = c + phi * y0
    A = np.vstack([np.ones_like(y0), y0]).T
    phi_vec, *_ = np.linalg.lstsq(A, y1, rcond=None)
    c, phi = phi_vec

    history = y.copy()
    forecast = []
    current = history[-1]
    for _ in range(steps_ahead):
        current = c + phi * current
        forecast.append(current)
    forecast = np.asarray(forecast)

    horizon_seconds = steps_ahead * sample_period

    # Back-test on last segment for MAE/MAPE
    backtest_steps = min(steps_ahead, len(y1))
    preds = c + phi * y0[-backtest_steps:]
    truth = y1[-backtest_steps:]
    mae = float(np.mean(np.abs(truth - preds)))
    mape = float(np.mean(np.abs((truth - preds) / np.maximum(np.abs(truth), 1e-6))) * 100.0)

    # Lead time estimation
    lead_time_seconds = np.nan
    if alert_threshold > 0:
        for idx, val in enumerate(np.abs(forecast), start=1):
            if val >= alert_threshold:
                lead_time_seconds = idx * sample_period
                break

    return ForecastResult(
        forecast=forecast,
        horizon_seconds=horizon_seconds,
        mae=mae,
        mape=mape,
        lead_time_seconds=float(lead_time_seconds) if not np.isnan(lead_time_seconds) else np.nan,
    )
