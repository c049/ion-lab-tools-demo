"""Allan deviation utilities for frequency noise analysis."""

from typing import Iterable, Tuple

import numpy as np


def allan_deviation(y: np.ndarray, sample_period: float, cluster_sizes: Iterable[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Allan deviation for an evenly sampled time series.

    Parameters
    ----------
    y : array-like
        Signal (e.g., frequency lock error).
    sample_period : float
        Sampling period in seconds.
    cluster_sizes : iterable of int, optional
        Averaging factors. If None, chooses logarithmically spaced values.

    Returns
    -------
    taus : np.ndarray
        Averaging times (seconds).
    adevs : np.ndarray
        Allan deviation values.
    """

    y = np.asarray(y, dtype=float)
    n = y.size
    if n < 5:
        raise ValueError("Need at least 5 samples to compute Allan deviation")

    if cluster_sizes is None:
        max_m = max(2, n // 4)
        cluster_sizes = np.unique(np.logspace(0, np.log10(max_m), num=min(10, max_m), dtype=int))

    taus = []
    adevs = []
    for m in cluster_sizes:
        if m < 1 or 2 * m >= n:
            continue
        # Compute non-overlapping cluster averages
        trimmed = y[: (n // m) * m]
        clusters = trimmed.reshape(-1, m).mean(axis=1)
        if clusters.size < 2:
            continue
        diff = np.diff(clusters)
        allan_var = 0.5 * np.mean(diff**2)
        taus.append(m * sample_period)
        adevs.append(np.sqrt(allan_var))

    if not taus:
        raise ValueError("Failed to compute Allan deviation for the given data/cluster sizes")

    return np.asarray(taus), np.asarray(adevs)
