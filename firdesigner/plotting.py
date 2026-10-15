"""
Matplotlib plots for coefficients, filter responses and signals.

Every function draws on `ax` (the current axes by default) and returns it,
so plots can be combined in your own subplot layouts.
"""
import matplotlib.pylab as plt

from . import analysis
from .designer import design


# ---- Coefficients and responses ----------------------------------------------

def plot_coefficients(b, ax=None, **kwargs):
    ax = ax or plt.gca()
    ax.plot(b, **kwargs)
    ax.set_xlabel('Tap')
    ax.set_ylabel('Coefficient')
    return ax


def plot_frequency_response(b, fs, ax=None, db=True, **kwargs):
    ax = ax or plt.gca()
    f, mag = analysis.magnitude_db(b, fs)
    if not db:
        mag = 10 ** (mag / 20)
    ax.plot(f, mag, **kwargs)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude (dB)' if db else 'Magnitude')
    return ax


def plot_group_delay(b, fs, ax=None, **kwargs):
    ax = ax or plt.gca()
    f, gd = analysis.group_delay(b, fs)
    ax.plot(f, gd, **kwargs)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Group delay (samples)')
    return ax


def plot_impulse_response(b, ax=None, n=1000, **kwargs):
    ax = ax or plt.gca()
    ax.plot(analysis.impulse_response(b, n), **kwargs)
    ax.set_xlabel('Sample')
    return ax


def compare_windows(numtaps, cutoff, fs, windows, btype='bandpass'):
    """Plot coefficients and magnitude response for several windows."""
    fig, (ax_b, ax_h) = plt.subplots(2, 1)
    fig.suptitle('Coefficients and magnitude response per window')
    for w in windows:
        b = design(numtaps, cutoff, fs, btype, window=w)
        plot_coefficients(b, ax=ax_b, label=w)
        plot_frequency_response(b, fs, ax=ax_h, label=w)
    ax_b.legend()
    return fig


# ---- Signals -----------------------------------------------------------------

def plot_spectrum(x, fs, ax=None, log=False, **kwargs):
    ax = ax or plt.gca()
    f, mag = analysis.spectrum(x, fs)
    (ax.loglog if log else ax.plot)(f, mag, **kwargs)
    ax.set_xlabel('Frequency (Hz)')
    return ax


def plot_before_after(x, y, fs, log=False, xlim=None):
    """Time signals and spectra of the unfiltered (x) and filtered (y) signals."""
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(x)
    axs[0, 0].set_title('Unfiltered')
    axs[1, 0].plot(y)
    axs[1, 0].set_title('Filtered')
    if xlim:
        axs[0, 0].set_xlim(xlim)
        axs[1, 0].set_xlim(xlim)
    plot_spectrum(x, fs, ax=axs[0, 1], log=log)
    plot_spectrum(y, fs, ax=axs[1, 1], log=log)
    return fig
