"""
    Band-pass filter a recorded signal (data/unfiltered.dat) sample by sample.
    Author. Gabriel Galeote Checa
    email: gabriel@imse-cnm.csic.es
    GNU license
"""
from pathlib import Path

import matplotlib.pylab as plt
import numpy as np

from firdesigner import FIRFilter, designer, plotting

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'output'

fs = 2000  # Hertz
NTAPS = 1000
SAMPLES = 100 * fs

mysignal = np.loadtxt(ROOT / 'data' / 'unfiltered.dat', max_rows=SAMPLES)[:, 1]

b = designer.bandpass(NTAPS, 1, 40, fs)
y = FIRFilter(b).filter(mysignal)

plotting.plot_before_after(mysignal, y, fs, log=True)

OUTPUT.mkdir(exist_ok=True)
designer.save_coefficients(b, OUTPUT / 'coefficients.dat')

plt.show()
