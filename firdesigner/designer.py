"""
Coefficient design for FIR filters.

All frequencies are given in Hz together with the sample rate fs. Three
methods are available:

    design / lowpass / ...   window method (scipy.signal.firwin)
    kaiser                   window method from a spec: the number of taps is
                             computed from attenuation and transition width
    equiripple               Parks-McClellan (scipy.signal.remez)
    least_squares            least-squares error (scipy.signal.firls)

Every design is checked against the linear-phase type it produces, so an
impossible request (e.g. an even-length highpass) fails with a clear message.
"""
import numpy as np
from scipy import signal

from .linear_phase import NEEDS_GAIN, check_gains, check_response, type_for

PASS_ZERO = {'lowpass': True, 'highpass': False, 'bandpass': False, 'bandstop': True}


# ---- Window method -----------------------------------------------------------

def design(numtaps, cutoff, fs, btype='lowpass', window=None, width=None):
    """Window-method FIR design.

    numtaps : number of coefficients
    cutoff  : cutoff in Hz (scalar for low/highpass, [f1, f2] for band filters)
    fs      : sample rate in Hz
    btype   : 'lowpass', 'highpass', 'bandpass' or 'bandstop'
    window  : any window accepted by scipy.signal.get_window (default 'hamming')
    width   : transition width in Hz; designs a Kaiser window instead,
              so it cannot be combined with `window`
    """
    if window is not None and width is not None:
        raise ValueError("give either window or width: with width, firwin "
                         "designs a Kaiser window and ignores window")
    if window is None:
        window = 'hamming'
    check_response(type_for(numtaps), btype)
    return signal.firwin(numtaps, cutoff, pass_zero=PASS_ZERO[btype],
                         window=window, width=width, fs=fs)


def lowpass(numtaps, cutoff, fs, **kwargs):
    return design(numtaps, cutoff, fs, 'lowpass', **kwargs)


def highpass(numtaps, cutoff, fs, **kwargs):
    return design(numtaps, cutoff, fs, 'highpass', **kwargs)


def bandpass(numtaps, f1, f2, fs, **kwargs):
    return design(numtaps, [f1, f2], fs, 'bandpass', **kwargs)


def bandstop(numtaps, f1, f2, fs, **kwargs):
    return design(numtaps, [f1, f2], fs, 'bandstop', **kwargs)


def kaiser(cutoff, fs, btype='lowpass', attenuation_db=60, width=None):
    """Window-method design from a spec instead of a tap count.

    attenuation_db : required stopband attenuation (also sets passband ripple)
    width          : transition width in Hz

    The number of taps comes from scipy.signal.kaiserord, made odd when the
    response needs gain at Nyquist (highpass, bandstop).
    """
    if width is None:
        raise ValueError("kaiser design needs a transition width in Hz")
    numtaps, beta = signal.kaiserord(attenuation_db, width / (fs / 2))
    if 'Nyquist' in NEEDS_GAIN[btype] and numtaps % 2 == 0:
        numtaps += 1
    return design(numtaps, cutoff, fs, btype, window=('kaiser', beta))


# ---- Optimal methods ---------------------------------------------------------

def _band_gains_needed(bands, desired, fs):
    """Which of DC / Nyquist must have non-zero gain for these bands."""
    needs = []
    if bands[0] == 0 and desired[0] != 0:
        needs.append('DC')
    if bands[-1] == fs / 2 and desired[-1] != 0:
        needs.append('Nyquist')
    return needs


def equiripple(numtaps, bands, desired, fs, weight=None, kind='bandpass'):
    """Parks-McClellan (equiripple) design.

    bands   : band edges in Hz, two per band, e.g. [0, 40, 60, fs/2]
    desired : one gain per band, e.g. [1, 0]
    weight  : optional relative weight per band (higher = less ripple there)
    kind    : 'bandpass' (symmetric, types I/II), or 'differentiator' /
              'hilbert' (antisymmetric, types III/IV)
    """
    if kind == 'bandpass':
        check_gains(type_for(numtaps), _band_gains_needed(bands, desired, fs))
    return signal.remez(numtaps, bands, desired, weight=weight, type=kind, fs=fs)


def least_squares(numtaps, bands, desired, fs, weight=None):
    """Least-squares design (scipy.signal.firls), always type I.

    bands, desired and weight as in equiripple(). numtaps must be odd.
    """
    if numtaps % 2 == 0:
        raise ValueError("least_squares needs an odd number of taps (type I)")
    # firls wants a gain at each band edge, so each band's gain is used twice.
    return signal.firls(numtaps, bands, np.repeat(desired, 2), weight=weight, fs=fs)


# ---- Transformations and storage ---------------------------------------------

def to_minimum_phase(b, method='homomorphic'):
    """Minimum-phase version of a linear-phase filter ('homomorphic' or 'hilbert').

    The result has roughly half the taps of the input and is no longer linear phase.
    """
    return signal.minimum_phase(b, method=method)


def save_coefficients(b, path):
    np.savetxt(path, b, fmt='%.18e')


def load_coefficients(path):
    return np.loadtxt(path)
