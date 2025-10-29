import matplotlib

# 使用非交互式后端避免在无 GUI 环境下崩溃
matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt

def timeseries_plot(df, path):
    fig = plt.figure(figsize=(8,6))
    ax1 = plt.gca()
    ax1.plot(df['timestamp'], df['rb_fidelity'], label='RB fidelity')
    ax1.set_ylabel('RB fidelity')
    ax1.set_xlabel('Time')
    ax1.legend(loc='best')
    fig.autofmt_xdate()
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)

def psd_plot(freqs, psd, path, xlabel="Frequency (Hz)", ylabel="PSD"):
    fig = plt.figure(figsize=(8,6))
    ax = plt.gca()
    ax.loglog(freqs[1:], psd[1:])  # skip DC
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
