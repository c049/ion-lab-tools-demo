# ion-lab-tools-demo

A minimal **data → plots → PDF** pipeline for trapped-ion lab datasets.  
Targets QCL-style daily tasks: calibration logs, RB metrics, frequency locks, and environmental drift.

## Features
- Ingest CSV logs with timestamps and metrics.
- Generate standard plots (time series, PSD).
- One-click **PDF report** (using Matplotlib's `PdfPages`).
- Simple quality flags & threshold-based alerts.
- Tested with `pytest`; reproducible via fixed random seeds.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ion_lab_tools.run --input data/sample/sample_log.csv --out out
```

Outputs appear in `out/`:
- `timeseries.png` – key metrics over time
- `psd.png` – power spectral density
- `summary.txt` – basic stats & alerts
- `report.pdf` – a compiled PDF with figures and summary

## Data schema (CSV)
Required columns:
- `timestamp` (ISO format)
- `rb_fidelity` (0..1)
- `rabi_freq` (Hz)
- `lock_error` (Hz)
- `temperature` (C)

## Repo layout
```
ion-lab-tools-demo/
  ion_lab_tools/
    __init__.py
    run.py                # CLI entry point
    processing/
      io.py               # load & validate
      metrics.py          # stats & PSD
    reporting/
      make_plots.py       # plots
      report.py           # PdfPages report + summary
  data/sample/sample_log.csv
  tests/
    test_metrics.py
  out/                    # generated
  requirements.txt
  README.md
```

## Why this matters for QCL
- Replaces manual “data → figure” workflows.
- Gives baseline **noise/PSD** visibility and **drift alerts**.
- Ready to extend with instrument APIs and scheduling.
