"""Randomized benchmarking (RB) decay fitting utilities."""

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


@dataclass
class RBFitResult:
    """Container for RB fit parameters and diagnostic metrics."""

    a: float
    p: float
    b: float
    covariance: np.ndarray
    residual_rms: float
    ci_half_width: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "rb_a": float(self.a),
            "rb_p": float(self.p),
            "rb_b": float(self.b),
            "rb_residual_rms": float(self.residual_rms),
            "rb_ci_half_width": float(self.ci_half_width),
        }


def _rb_model(m: np.ndarray, a: float, p: float, b: float) -> np.ndarray:
    return a * (p**m) + b


def fit_rb_decay(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, RBFitResult]:
    """
    Fit the standard RB decay curve:
        F(m) = a * p^m + b

    Parameters
    ----------
    df : DataFrame
        Must contain `sequence_length` and `fidelity`.

    Returns
    -------
    m : np.ndarray
        Sorted sequence lengths used in the fit.
    fit_y : np.ndarray
        Model predictions for each m.
    result : RBFitResult
        Fit parameters and diagnostics.
    """

    if not {"sequence_length", "fidelity"} <= set(df.columns):
        raise ValueError("RB data must contain 'sequence_length' and 'fidelity'")

    data = df.dropna(subset=["sequence_length", "fidelity"]).sort_values("sequence_length")
    m = data["sequence_length"].to_numpy(dtype=float)
    y = data["fidelity"].to_numpy(dtype=float)

    if len(m) < 5:
        raise ValueError("Need at least 5 RB points to fit a decay curve")

    # Initial guesses: a~(y0 - y_end), p~0.995, b~y_end
    a0 = max(y[0] - y[-1], 0.01)
    p0 = 0.995
    b0 = max(y[-1], 0.5)

    popt, pcov = curve_fit(_rb_model, m, y, p0=[a0, p0, b0], bounds=([0, 0.5, 0], [1.5, 1.0, 1.0]))
    fit_y = _rb_model(m, *popt)
    residuals = y - fit_y
    residual_rms = float(np.sqrt(np.mean(residuals**2)))

    # 95% confidence interval half-width using diagonal of covariance
    sigma = np.sqrt(np.diag(pcov))
    ci_half_width = float(1.96 * np.mean(sigma))

    result = RBFitResult(
        a=float(popt[0]),
        p=float(popt[1]),
        b=float(popt[2]),
        covariance=pcov,
        residual_rms=residual_rms,
        ci_half_width=ci_half_width,
    )
    return m, fit_y, result
