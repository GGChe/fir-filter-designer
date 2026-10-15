"""
    The four linear-phase FIR types, their forced zeros, and the folded
    LinearPhaseFIR implementation compared against the direct form.
"""
import matplotlib.pylab as plt
import numpy as np

from firdesigner import FIRFilter, LinearPhaseFIR, designer, plotting

FS = 2000  # Hertz

types = {
    'I   (symmetric, 101 taps, lowpass)': designer.lowpass(101, 200, FS),
    'II  (symmetric, 100 taps, lowpass)': designer.lowpass(100, 200, FS),
    'III (antisymmetric, 101 taps, hilbert)': designer.equiripple(101, [50, 950], [1], FS, kind='hilbert'),
    'IV  (antisymmetric, 100 taps, hilbert)': designer.equiripple(100, [50, 1000], [1], FS, kind='hilbert'),
}

x = np.random.default_rng(0).standard_normal(5000)
for name, b in types.items():
    folded = LinearPhaseFIR(b)
    err = np.abs(folded.filter(x) - FIRFilter(b).filter(x)).max()
    print(f"{name:40s} detected type {folded.type}, "
          f"{folded.multiplications} multiplications instead of {len(b)}, "
          f"max difference to direct form {err:.1e}")
    plotting.plot_frequency_response(b, FS, label=name)

# An impossible request fails with an explanation instead of a SciPy error.
try:
    designer.highpass(100, 500, FS)
except ValueError as e:
    print("highpass with 100 taps:", e)

plt.ylim(-100, 5)
plt.legend()
plt.title('Type II is 0 at Nyquist, III at DC and Nyquist, IV at DC')
plt.show()
