import argparse
import os
from .processing.io import load_csv
from .processing.metrics import basic_stats, compute_psd, quality_flags
from .reporting.make_plots import timeseries_plot, psd_plot
from .reporting.report import write_summary_text, save_text_as_figure, compile_pdf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV file")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = load_csv(args.input)

    # Stats
    stats = {
        "rb_fidelity_mean": basic_stats(df['rb_fidelity'])['mean'],
        "rabi_freq_mean": basic_stats(df['rabi_freq'])['mean'],
        "lock_error_std": basic_stats(df['lock_error'])['std'],
        "temperature_mean": basic_stats(df['temperature'])['mean'],
    }
    # Sampling rate (approx) from median dt
    dt = (df['timestamp'].diff().dt.total_seconds()).median()
    fs = 1.0 / dt if dt and dt>0 else 1.0

    # PSD on lock_error
    freqs, psd = compute_psd(df['lock_error'].values, fs)
    flags = quality_flags(df)

    # Plots
    ts_path = os.path.join(args.out, "timeseries.png")
    psd_path = os.path.join(args.out, "psd.png")
    timeseries_plot(df, ts_path)
    psd_plot(freqs, psd, psd_path)

    # Summary
    summary_text = write_summary_text(stats, flags)
    open(os.path.join(args.out, "summary.txt"), "w").write(summary_text)
    summary_fig = os.path.join(args.out, "summary.png")
    save_text_as_figure(summary_text, summary_fig)

    # Report PDF
    pdf_path = os.path.join(args.out, "report.pdf")
    compile_pdf([summary_fig, ts_path, psd_path], pdf_path)

    print("Done. Outputs saved to", args.out)

if __name__ == "__main__":
    main()
