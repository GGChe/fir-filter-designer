"""
    Compare coefficients and magnitude response of a band-pass FIR
    designed with different windows.
"""
import matplotlib.pylab as plt

from firdesigner import plotting

SAMPLE_RATE = 2000  # Hertz
NTAPS = 1000

plotting.compare_windows(NTAPS, [0.5, 45], SAMPLE_RATE,
                         ['blackman', 'hamming', 'triang', 'blackmanharris'])
plt.show()
