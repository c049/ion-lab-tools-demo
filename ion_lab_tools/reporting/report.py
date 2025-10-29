import matplotlib

# 与绘图模块保持一致，强制使用 Agg 后端（无 GUI 也能运行）
matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def write_summary_text(summary_dict, flags):
    lines = []
    for k,v in summary_dict.items():
        lines.append(f"{k}: {v:.6g}")
    if flags:
        lines.append("")
        lines.append("Alerts:")
        for f in flags:
            lines.append(f"- {f}")
    return "\n".join(lines)

def save_text_as_figure(text, fig_path):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.text(0.05, 0.95, "Summary", fontsize=16, va='top')
    fig.text(0.05, 0.9, text, fontsize=10, va='top', family='monospace')
    fig.savefig(fig_path, dpi=200, bbox_inches='tight')
    plt.close(fig)

def compile_pdf(fig_paths, pdf_path):
    with PdfPages(pdf_path) as pdf:
        for p in fig_paths:
            img = plt.imread(p)
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = plt.gca()
            ax.imshow(img)
            ax.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
