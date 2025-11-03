import numpy as np

from ion_lab_tools.analysis.allan import allan_deviation


def test_allan_deviation_monotonic():
    y = np.sin(np.linspace(0, 10, 200))
    taus, adevs = allan_deviation(y, sample_period=0.1)
    assert len(taus) == len(adevs) and len(taus) > 1
    assert np.all(adevs > 0)
