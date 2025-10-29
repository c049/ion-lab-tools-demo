import numpy as np
import pandas as pd

def basic_stats(series: pd.Series):
    return {
        "mean": float(series.mean()),
        "std": float(series.std(ddof=1)),
        "min": float(series.min()),
        "max": float(series.max())
    }

def compute_psd(y, fs_hz):
    # Periodogram (simple PSD estimate)
    y = np.asarray(y) - np.mean(y)
    n = len(y)
    window = np.hanning(n)
    yf = np.fft.rfft(y * window)
    psd = (np.abs(yf)**2) / (np.sum(window**2) * fs_hz)
    freqs = np.fft.rfftfreq(n, d=1.0/fs_hz)
    return freqs, psd

def quality_flags(df):
    flags = []
    if (df['rb_fidelity'] < 0.95).mean() > 0.2:
        flags.append("RB fidelity often < 0.95")
    if (df['lock_error'].abs() > 200).mean() > 0.1:
        flags.append("Lock error frequently > 200 Hz")
    if df['temperature'].diff().abs().mean() > 0.2:
        flags.append("Temperature drifting")
    return flags
