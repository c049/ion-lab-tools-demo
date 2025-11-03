import matplotlib

# Match the plotting module to ensure Agg backend (headless friendly)
matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def write_summary_text(summary_entries, flags=None, title="Metric Summary"):
    """
    Accepts either a dict or iterable of (label, value) pairs.
    """
    if isinstance(summary_entries, dict):
        items = summary_entries.items()
    else:
        items = summary_entries

    lines = [title, "-" * len(title)]
    for label, value in items:
        if isinstance(value, float):
            lines.append(f"{label:<30} {value:.4g}")
        else:
            lines.append(f"{label:<30} {value}")

    if flags:
        lines.append("")
        lines.append("Threshold Alerts")
        lines.append("-" * len("Threshold Alerts"))
        for f in flags:
            lines.append(f"- {f}")

    return "\n".join(lines)


def save_text_as_figure(text, fig_path, title="Summary"):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.text(0.05, 0.95, title, fontsize=16, va="top")
    fig.text(0.05, 0.9, text, fontsize=10, va="top", family="monospace")
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def compile_pdf(fig_paths, pdf_path):
    with PdfPages(pdf_path) as pdf:
        for p in fig_paths:
            img = plt.imread(p)
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = plt.gca()
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
