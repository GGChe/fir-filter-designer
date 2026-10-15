"""
Numerical analysis of FIR coefficients and filtered signals (no plotting).

Coefficient analysis: frequency response, group delay, impulse response,
linear-phase type, and design measurements (ripple, attenuation, cutoffs).
Signal analysis: one-sided amplitude spectrum.
Plots of all of these live in firdesigner.plotting.
"""
import numpy as np
from scipy import signal

from .filter import FIRFilter
from .linear_phase import linear_phase_type

__all__ = ['frequency_response', 'magnitude_db', 'group_delay', 'impulse_response',
           'linear_phase_type', 'passband_ripple', 'stopband_attenuation',
           'crossings', 'summary', 'spectrum']


# ---- Coefficient analysis ----------------------------------------------------

def frequency_response(b, fs, n=8192):
    """Return (f in Hz, complex response H)."""
    return signal.freqz(b, worN=n, fs=fs)


def magnitude_db(b, fs, n=8192):
    """Return (f in Hz, magnitude in dB, 0 dB = gain of 1)."""
    f, h = frequency_response(b, fs, n)
    return f, 20 * np.log10(np.maximum(np.abs(h), 1e-12))


def group_delay(b, fs, n=8192):
    """Return (f in Hz, group delay in samples)."""
    return signal.group_delay((b, 1), w=n, fs=fs)


def impulse_response(b, n=1000, delay=10):
    """Impulse response measured by running an impulse through FIRFilter."""
    impulse = np.zeros(n)
    impulse[delay] = 1
    return FIRFilter(b).filter(impulse)


def _in_band(f, band):
    return (f >= band[0]) & (f <= band[1])


def passband_ripple(b, fs, band, n=8192):
    """Peak-to-peak magnitude variation in dB inside band = (f1, f2) Hz."""
    f, mag = magnitude_db(b, fs, n)
    m = mag[_in_band(f, band)]
    return float(m.max() - m.min())


def stopband_attenuation(b, fs, band, n=8192):
    """Worst-case attenuation in dB inside band = (f1, f2) Hz (positive number)."""
    f, mag = magnitude_db(b, fs, n)
    return float(-mag[_in_band(f, band)].max())


def crossings(b, fs, level_db=-3, n=8192):
    """Frequencies in Hz where the magnitude crosses level_db, e.g. the -3 dB points."""
    f, mag = magnitude_db(b, fs, n)
    d = mag - level_db
    idx = np.nonzero(np.sign(d[:-1]) * np.sign(d[1:]) < 0)[0]
    # Linear interpolation between the two bins around each crossing.
    return f[idx] + (f[idx + 1] - f[idx]) * d[idx] / (d[idx] - d[idx + 1])


def summary(b, fs, passbands=(), stopbands=()):
    """Key figures of a design as a dict; bands are (f1, f2) tuples in Hz."""
    lp_type = linear_phase_type(b)
    return {
        'taps': len(b),
        'linear_phase_type': lp_type,
        'delay_samples': (len(b) - 1) / 2 if lp_type else None,
        '-3dB_Hz': crossings(b, fs, -3).round(2).tolist(),
        'passband_ripple_dB': [round(passband_ripple(b, fs, p), 3) for p in passbands],
        'stopband_attenuation_dB': [round(stopband_attenuation(b, fs, s), 1) for s in stopbands],
    }


# ---- Signal analysis ---------------------------------------------------------

def spectrum(x, fs):
    """One-sided amplitude spectrum, normalised by 1/N. Returns (f in Hz, |X|)."""
    n = len(x)
    return np.fft.rfftfreq(n, 1 / fs), np.abs(np.fft.rfft(x)) / n
