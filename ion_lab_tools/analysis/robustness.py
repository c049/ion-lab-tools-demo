"""Noise/decimation robustness diagnostics."""

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd


@dataclass
class RobustnessResult:
    noise_slope: float
    downsample_slope: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "robustness_noise_slope": float(self.noise_slope),
            "robustness_downsample_slope": float(self.downsample_slope),
        }


def evaluate_noise_robustness(series: pd.Series, noise_levels: Iterable[float]) -> Tuple[np.ndarray, np.ndarray]:
    """Return noise levels and resulting std values to show sensitivity."""

    baseline_std = series.std()
    levels = []
    stds = []
    for lvl in noise_levels:
        noisy = series + np.random.default_rng(0).normal(scale=lvl, size=series.size)
        stds.append(noisy.std())
        levels.append(lvl)
    return np.asarray(levels, dtype=float), np.asarray(stds, dtype=float) / (baseline_std + 1e-9)


def evaluate_downsample_robustness(series: pd.Series, factors: Iterable[int]) -> Tuple[np.ndarray, np.ndarray]:
    """Return downsample factors and resulting mean-drift magnitude."""

    baseline = series.mean()
    facs = []
    drifts = []
    for f in factors:
        if f <= 0:
            continue
        sampled = series.iloc[::f]
        if sampled.empty:
            continue
        drifts.append(abs(sampled.mean() - baseline))
        facs.append(f)
    return np.asarray(facs, dtype=float), np.asarray(drifts, dtype=float)


def summarize_robustness(noise_levels: np.ndarray, noise_ratio: np.ndarray, factors: np.ndarray, drifts: np.ndarray) -> RobustnessResult:
    noise_slope = float(np.polyfit(noise_levels, noise_ratio, 1)[0]) if len(noise_levels) > 1 else 0.0
    downsample_slope = float(np.polyfit(factors, drifts, 1)[0]) if len(factors) > 1 else 0.0
    return RobustnessResult(noise_slope=noise_slope, downsample_slope=downsample_slope)
