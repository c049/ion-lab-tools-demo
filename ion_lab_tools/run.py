import argparse
import os

from . import report as config_report
from .processing.io import load_csv
from .processing.metrics import basic_stats, compute_psd, quality_flags
from .reporting.make_plots import psd_plot, timeseries_plot
from .reporting.report import compile_pdf, save_text_as_figure, write_summary_text


def _simple_pipeline(input_csv: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    df = load_csv(input_csv)

    stats = {
        "rb_fidelity_mean": basic_stats(df["rb_fidelity"])["mean"],
        "rabi_freq_mean": basic_stats(df["rabi_freq"])["mean"],
        "lock_error_std": basic_stats(df["lock_error"])["std"],
        "temperature_mean": basic_stats(df["temperature"])["mean"],
    }

    dt = (df["timestamp"].diff().dt.total_seconds()).median()
    fs = 1.0 / dt if dt and dt > 0 else 1.0
    freqs, psd = compute_psd(df["lock_error"].values, fs)
    flags = quality_flags(df)

    ts_path = os.path.join(out_dir, "timeseries.png")
    psd_path = os.path.join(out_dir, "psd.png")
    timeseries_plot(df, ts_path)
    psd_plot(freqs, psd, psd_path)

    summary_text = write_summary_text(stats, flags)
    with open(os.path.join(out_dir, "summary.txt"), "w", encoding="utf-8") as fh:
        fh.write(summary_text)
    summary_fig = os.path.join(out_dir, "summary.png")
    save_text_as_figure(summary_text, summary_fig)

    pdf_path = os.path.join(out_dir, "report.pdf")
    compile_pdf([summary_fig, ts_path, psd_path], pdf_path)
    print("Done. Outputs saved to", out_dir)


def main():
    ap = argparse.ArgumentParser(description="Ion lab quick pipeline")
    ap.add_argument("--config", help="YAML config file for the enhanced report")
    ap.add_argument("--input", help="CSV file (simple pipeline)")
    ap.add_argument("--out", default="out", help="Output directory")
    args = ap.parse_args()

    if args.config:
        config = config_report._load_config(args.config)
        config.setdefault("output_dir", args.out)
        config_report.generate_from_config(config)
        print(f"Enhanced report generated: {config['output_dir']}")
    else:
        if not args.input:
            ap.error("--input is required for the simple mode (or use --config)")
        _simple_pipeline(args.input, args.out)


if __name__ == "__main__":
    main()
