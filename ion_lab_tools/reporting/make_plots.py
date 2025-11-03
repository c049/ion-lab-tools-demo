import matplotlib

# Use a non-interactive backend to avoid GUI requirements
matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def timeseries_plot(df: pd.DataFrame, path: str):
    fig = plt.figure(figsize=(8, 4))
    ax1 = plt.gca()
    ax1.plot(df["timestamp"], df["rb_fidelity"], label="RB fidelity", color="#1f77b4")
    ax1.set_ylabel("RB fidelity")
    ax1.set_xlabel("Time")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(df["timestamp"], df["lock_error"], label="Lock error (Hz)", color="#ff7f0e", alpha=0.7)
    ax2.set_ylabel("Lock error (Hz)")
    fig.autofmt_xdate()

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")

    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def psd_plot(freqs: np.ndarray, psd: np.ndarray, path: str, xlabel: str = "Frequency (Hz)", ylabel: str = "PSD"):
    fig = plt.figure(figsize=(6, 4))
    ax = plt.gca()
    ax.loglog(freqs[1:], psd[1:], color="#2ca02c")  # skip DC
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="both", ls="--", alpha=0.4)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def rb_fit_plot(m: np.ndarray, y: np.ndarray, fit_y: np.ndarray, ci_half_width: float, path: str):
    fig = plt.figure(figsize=(6, 4))
    ax = plt.gca()
    ax.scatter(m, y, label="Measured data", color="#1f77b4")
    ax.plot(m, fit_y, label="Fit curve", color="#d62728")
    ax.fill_between(m, fit_y - ci_half_width, fit_y + ci_half_width, color="#ff9896", alpha=0.4, label="95% CI")
    ax.set_xlabel("Sequence length (Clifford count)")
    ax.set_ylabel("RB fidelity")
    ax.legend(loc="upper right")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def allan_plot(taus: np.ndarray, adevs: np.ndarray, path: str):
    fig = plt.figure(figsize=(6, 4))
    ax = plt.gca()
    ax.loglog(taus, adevs, marker="o", color="#9467bd")
    ax.set_xlabel("Integration time tau (s)")
    ax.set_ylabel("Allan deviation")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def forecast_plot(time_index: pd.Series, actual: pd.Series, forecast: np.ndarray, sample_period: float, path: str, threshold: float):
    future_times = time_index.iloc[-1] + pd.to_timedelta(np.arange(1, forecast.size + 1) * sample_period, unit="s")

    fig = plt.figure(figsize=(8, 4))
    ax = plt.gca()
    ax.plot(time_index, actual, label="Lock error (measured)", color="#1f77b4")
    ax.plot(future_times, forecast, label="AR(1) forecast", color="#d62728", linestyle="--")
    ax.axhline(threshold, color="#ff7f0e", linestyle=":", label="Alert threshold")
    ax.axhline(-threshold, color="#ff7f0e", linestyle=":")
    ax.set_ylabel("Lock error (Hz)")
    ax.set_xlabel("Time")
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def bo_comparison_plot(df: pd.DataFrame, path: str):
    fig = plt.figure(figsize=(6, 4))
    ax = plt.gca()
    for method, group in df.groupby("method"):
        sorted_group = group.sort_values("step")
        cum_best = np.maximum.accumulate(sorted_group["score"].to_numpy())
        ax.plot(sorted_group["step"], cum_best, marker="o", label=method.upper())
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best score (cumulative)")
    ax.legend(loc="lower right")
    ax.grid(True, ls="--", alpha=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def robustness_plot(noise_levels: np.ndarray, noise_ratio: np.ndarray, factors: np.ndarray, drifts: np.ndarray, path: str):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].plot(noise_levels, noise_ratio, marker="o", color="#17becf")
    axes[0].set_xlabel("Injected noise std (Hz)")
    axes[0].set_ylabel("Std amplification")
    axes[0].set_title("Noise sensitivity")
    axes[0].grid(True, ls="--", alpha=0.3)

    axes[1].plot(factors, drifts, marker="s", color="#bcbd22")
    axes[1].set_xlabel("Downsample factor")
    axes[1].set_ylabel("Mean drift (Hz)")
    axes[1].set_title("Sampling sensitivity")
    axes[1].grid(True, ls="--", alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
