from ion_lab_tools.processing.metrics import compute_psd
import numpy as np

def test_psd_nonnegative():
    x = np.random.randn(1024)
    f, p = compute_psd(x, fs_hz=1000.0)
    assert (p >= 0).all()
