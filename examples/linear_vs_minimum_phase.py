"""
    Compare a linear-phase low-pass FIR with its minimum-phase versions
    (homomorphic and Hilbert) on a recorded signal.
    Author. Gabriel Galeote Checa
    email: gabriel@imse-cnm.csic.es
    GNU license
"""
from pathlib import Path

import matplotlib.pylab as plt
import numpy as np

from firdesigner import FIRFilter, analysis, designer, plotting

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'output'

SAMPLE_RATE = 2000  # Hertz
NTAPS = 1000
SAMPLES = 100 * SAMPLE_RATE
XLIM = (20000, 60000)

mysignal = np.loadtxt(ROOT / 'data' / 'unfiltered.dat', max_rows=SAMPLES)[:, 1]

filters = {
    'linear phase': designer.lowpass(NTAPS, 40, SAMPLE_RATE),
}
filters['minimum phase (homomorphic)'] = designer.to_minimum_phase(filters['linear phase'], 'homomorphic')
filters['minimum phase (hilbert)'] = designer.to_minimum_phase(filters['linear phase'], 'hilbert')

print("-- Start computation of impulse response --")
fig, axs = plt.subplots(len(filters), 1, num=1)
for ax, (name, b) in zip(axs, filters.items()):
    ax.plot(analysis.impulse_response(b))
    ax.set_title(name)

print("-- Start computation of filtering --")
outputs = {name: FIRFilter(b).filter(mysignal) for name, b in filters.items()}

fig, axs = plt.subplots(len(filters) + 1, 1, num=2)
axs[0].plot(mysignal)
axs[0].set_title('unfiltered')
for ax, (name, y) in zip(axs[1:], outputs.items()):
    ax.plot(y)
    ax.set_title(name)
for ax in axs:
    ax.set_xlim(XLIM)

print("-- Start Frequency spectrum calculations --")
fig, axs = plt.subplots(len(filters) + 1, 1, num=3)
plotting.plot_spectrum(mysignal, SAMPLE_RATE, ax=axs[0], log=True)
for ax, y in zip(axs[1:], outputs.values()):
    plotting.plot_spectrum(y, SAMPLE_RATE, ax=ax, log=True)

OUTPUT.mkdir(exist_ok=True)
designer.save_coefficients(filters['linear phase'], OUTPUT / 'coefficients_fir.dat')
designer.save_coefficients(filters['minimum phase (homomorphic)'], OUTPUT / 'coefficients_fir_norm_homomorphic.dat')
designer.save_coefficients(filters['minimum phase (hilbert)'], OUTPUT / 'coefficients_fir_norm_hilbert.dat')

print("Done!")
plt.show()
