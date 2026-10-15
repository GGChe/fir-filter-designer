"""
    Band-pass filter a generated mix of 1, 50 and 350 Hz sine waves sample by sample.
    Author. Gabriel Galeote Checa
    email: gabriel@imse-cnm.csic.es
    GNU license
"""
from pathlib import Path

import matplotlib.pylab as plt
import numpy as np

from firdesigner import FIRFilter, designer, plotting

OUTPUT = Path(__file__).resolve().parent.parent / 'output'

SAMPLE_RATE = 2000  # Hertz
DURATION = 5  # Seconds
NTAPS = 1000


def generate_sine_wave(freq, sample_rate, duration, magnitude):
    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = magnitude * np.sin((2 * np.pi) * frequencies)
    return x, y


x, sine1 = generate_sine_wave(1, SAMPLE_RATE, DURATION, 1)
_, noise = generate_sine_wave(50, SAMPLE_RATE, DURATION, 0.5)
_, noise2 = generate_sine_wave(350, SAMPLE_RATE, DURATION, 2)
mysignal = sine1 + noise + noise2

b = designer.bandpass(NTAPS, 0.5, 45, SAMPLE_RATE, window='blackman')
y = FIRFilter(b).filter(mysignal)

plotting.plot_before_after(mysignal, y, SAMPLE_RATE)

OUTPUT.mkdir(exist_ok=True)
designer.save_coefficients(b, OUTPUT / 'coefficients.dat')

plt.show()
