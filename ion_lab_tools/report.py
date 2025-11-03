"""
Configuration-driven reporting CLI.

Example:
    python -m ion_lab_tools.report --config configs/demo.yaml
"""

import argparse
import json
import os
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml

from .analysis.allan import allan_deviation
from .analysis.bo import compare_methods
from .analysis.forecast import ar1_forecast
from .analysis.rb import fit_rb_decay
from .analysis.robustness import (
    evaluate_downsample_robustness,
    evaluate_noise_robustness,
    summarize_robustness,
)
from .processing.io import load_csv
from .processing.metrics import basic_stats, compute_psd, quality_flags
from .reporting.make_plots import (
    allan_plot,
    bo_comparison_plot,
    forecast_plot,
    psd_plot,
    rb_fit_plot,
    robustness_plot,
    timeseries_plot,
)
from .reporting.report import compile_pdf, save_text_as_figure, write_summary_text


def _ensure_out(path: str):
    os.makedirs(path, exist_ok=True)


def _load_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def generate_from_config(config: Dict) -> Dict[str, str]:
    output = config.get("output_dir", "out")
    _ensure_out(output)

    log_df = load_csv(config["inputs"]["log"])
    rb_df = pd.read_csv(config["inputs"]["rb"])
    bo_df = pd.read_csv(config["inputs"]["bo"])

    dt = (log_df["timestamp"].diff().dt.total_seconds()).median()
    sample_period = float(dt if dt and dt > 0 else 1.0)
    fs = 1.0 / sample_period

    stats = {
        "rb_fidelity_mean": basic_stats(log_df["rb_fidelity"])["mean"],
        "lock_error_std": basic_stats(log_df["lock_error"])["std"],
    }

    freqs, psd_vals = compute_psd(log_df["lock_error"].to_numpy(), fs)
    psd_noise_floor = float(np.median(psd_vals[-10:])) if psd_vals.size >= 10 else float(np.median(psd_vals))

    taus, adevs = allan_deviation(log_df["lock_error"].to_numpy(), sample_period)

    m, rb_fit_y, rb_result = fit_rb_decay(rb_df)

    forecast_cfg = config.get("analysis", {}).get("forecast", {})
    steps_ahead = int(forecast_cfg.get("horizon_steps", 30))
    alert_threshold = float(forecast_cfg.get("alert_threshold", 200))
    forecast_result = ar1_forecast(log_df["lock_error"], sample_period, steps_ahead, alert_threshold)

    robustness_cfg = config.get("analysis", {}).get("robustness", {})
    noise_levels = np.asarray(robustness_cfg.get("noise_levels", [0.0, 30.0, 60.0]), dtype=float)
    downsample_factors = np.asarray(robustness_cfg.get("downsample_factors", [1, 2, 4]), dtype=int)
    noise_x, noise_ratio = evaluate_noise_robustness(log_df["lock_error"], noise_levels)
    ds_x, ds_drift = evaluate_downsample_robustness(log_df["lock_error"], downsample_factors)
    robustness_result = summarize_robustness(noise_x, noise_ratio, ds_x, ds_drift)

    bo_comparison = compare_methods(bo_df)

    flags = quality_flags(log_df)
    if not np.isnan(forecast_result.lead_time_seconds):
        flags.append(f"Forecast crosses lock-error threshold in {forecast_result.lead_time_seconds/60:.1f} min")

    # --- plots ---
    paths: Dict[str, str] = {}
    paths["timeseries"] = os.path.join(output, "timeseries.png")
    timeseries_plot(log_df, paths["timeseries"])

    paths["psd"] = os.path.join(output, "psd.png")
    psd_plot(freqs, psd_vals, paths["psd"])

    paths["rb_fit"] = os.path.join(output, "rb_fit.png")
    rb_fit_plot(
        m,
        rb_df.sort_values("sequence_length")["fidelity"].to_numpy(),
        rb_fit_y,
        rb_result.ci_half_width,
        paths["rb_fit"],
    )

    paths["allan"] = os.path.join(output, "allan.png")
    allan_plot(taus, adevs, paths["allan"])

    paths["forecast"] = os.path.join(output, "forecast.png")
    forecast_plot(
        log_df["timestamp"],
        log_df["lock_error"],
        forecast_result.forecast,
        sample_period,
        paths["forecast"],
        alert_threshold,
    )

    paths["bo_comparison"] = os.path.join(output, "bo_comparison.png")
    bo_comparison_plot(bo_df, paths["bo_comparison"])

    paths["robustness"] = os.path.join(output, "robustness.png")
    robustness_plot(noise_x, noise_ratio, ds_x, ds_drift, paths["robustness"])

    summary_entries: List = [
        ("RB gate fidelity p", rb_result.p),
        ("RB residual RMS", rb_result.residual_rms),
        ("RB CI half-width", rb_result.ci_half_width),
        (f"Allan deviation tau={taus[0]:.1f}s", adevs[0]),
        ("PSD noise floor (Hz^2/Hz)", psd_noise_floor),
        ("Forecast MAE (Hz)", forecast_result.mae),
        ("Forecast MAPE (%)", forecast_result.mape),
        ("Lead time (min)", forecast_result.lead_time_seconds / 60.0 if not np.isnan(forecast_result.lead_time_seconds) else float("nan")),
        ("BO step reduction (%)", bo_comparison.step_reduction),
        ("BO terminal gain", bo_comparison.terminal_gain),
        ("Noise sensitivity slope", robustness_result.noise_slope),
        ("Downsample sensitivity slope", robustness_result.downsample_slope),
    ]

    summary_text = write_summary_text(summary_entries, flags)
    summary_txt_path = os.path.join(output, "summary.txt")
    with open(summary_txt_path, "w", encoding="utf-8") as fh:
        fh.write(summary_text)

    summary_fig_path = os.path.join(output, "summary.png")
    save_text_as_figure(summary_text, summary_fig_path, title="Metric Overview")

    metrics_json = {
        **stats,
        **{"psd_noise_floor": psd_noise_floor},
        **rb_result.as_dict(),
        **forecast_result.as_dict(),
        **bo_comparison.as_dict(),
        **robustness_result.as_dict(),
        "allan_tau_seconds": float(taus[0]),
        "allan_deviation": float(adevs[0]),
    }
    metrics_path = os.path.join(output, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics_json, fh, indent=2)

    include_figs = config.get("report", {}).get("include_figures")
    if not include_figs:
        pdf_figs = [summary_fig_path, paths["rb_fit"], paths["timeseries"], paths["psd"], paths["allan"], paths["forecast"], paths["bo_comparison"], paths["robustness"]]
    else:
        pdf_figs = [os.path.join(output, fig) if not os.path.isabs(fig) else fig for fig in include_figs]

    pdf_path = os.path.join(output, "report.pdf")
    compile_pdf(pdf_figs, pdf_path)

    paths["summary"] = summary_fig_path
    paths["summary_text"] = summary_txt_path
    paths["metrics"] = metrics_path
    paths["pdf"] = pdf_path
    return paths


def main():
    parser = argparse.ArgumentParser(description="Ion lab reporting pipeline")
    parser.add_argument("--config", required=True, help="YAML config file")
    args = parser.parse_args()

    config = _load_config(args.config)
    outputs = generate_from_config(config)
    print("Report generated:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
