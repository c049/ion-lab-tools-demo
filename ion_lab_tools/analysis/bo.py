"""Bayesian optimisation vs baselines diagnostics."""

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass
class BOComparison:
    step_reduction: float
    terminal_gain: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "bo_step_reduction_pct": float(self.step_reduction),
            "bo_terminal_gain": float(self.terminal_gain),
        }


def _cum_best(values: np.ndarray) -> np.ndarray:
    return np.maximum.accumulate(values)


def compare_methods(df: pd.DataFrame, target: float = None) -> BOComparison:
    """
    Compare BO vs random/grid search using cumulative best values.

    Parameters
    ----------
    df : DataFrame
        Columns: method, step, score. Higher score is better.
    target : float, optional
        Target score to reach. If None, uses 95% of BO terminal best.

    Returns
    -------
    BOComparison with step reduction (%) and terminal gain.
    """

    required = {"method", "step", "score"}
    if not required <= set(df.columns):
        raise ValueError("BO data must contain 'method', 'step', 'score'")

    pivot = (
        df.sort_values("step")
        .groupby("method")
        .apply(lambda g: pd.DataFrame({"step": g["step"], "best": _cum_best(g["score"].to_numpy())}))
        .reset_index(level=0)
    )

    bo = pivot[pivot["method"] == "bo"]
    baseline = pivot[pivot["method"] != "bo"]
    if bo.empty or baseline.empty:
        raise ValueError("Need at least one BO trajectory and one baseline")

    bo_terminal = float(bo["best"].iloc[-1])
    if target is None:
        target = 0.95 * bo_terminal

    def steps_to_target(df_method: pd.DataFrame) -> float:
        hit = df_method[df_method["best"] >= target]
        if hit.empty:
            return np.inf
        return float(hit["step"].iloc[0])

    baseline_steps = np.mean([steps_to_target(g) for _, g in baseline.groupby("method")])
    bo_steps = steps_to_target(bo)
    if np.isinf(baseline_steps) or np.isinf(bo_steps):
        step_reduction = 0.0
    else:
        step_reduction = ((baseline_steps - bo_steps) / baseline_steps) * 100.0 if baseline_steps else 0.0

    terminal_gain = bo_terminal - float(baseline.groupby("method")["best"].apply(lambda s: s.iloc[-1]).mean())
    return BOComparison(step_reduction=step_reduction, terminal_gain=terminal_gain)
