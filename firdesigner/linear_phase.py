"""
Linear-phase FIR types.

    Type I   symmetric,      odd length    no forced zeros
    Type II  symmetric,      even length   zero at Nyquist
    Type III antisymmetric,  odd length    zeros at DC and Nyquist
    Type IV  antisymmetric,  even length   zero at DC

A forced zero means the response is always 0 at that frequency, whatever the
coefficients, so e.g. a type II filter can never be a highpass.
"""
import numpy as np

FORCED_ZEROS = {1: (), 2: ('Nyquist',), 3: ('DC', 'Nyquist'), 4: ('DC',)}

# Frequencies where each response needs a non-zero gain.
NEEDS_GAIN = {'lowpass': ('DC',), 'highpass': ('Nyquist',),
              'bandpass': (), 'bandstop': ('DC', 'Nyquist')}


def type_for(numtaps, symmetric=True):
    """Linear-phase type produced by a design with this length and symmetry."""
    odd = numtaps % 2 == 1
    if symmetric:
        return 1 if odd else 2
    return 3 if odd else 4


def linear_phase_type(b, rtol=1e-8):
    """Return 1-4 for a linear-phase filter, None if the coefficients have no symmetry."""
    b = np.asarray(b, dtype=float)
    atol = rtol * np.max(np.abs(b))
    if np.allclose(b, b[::-1], rtol=0, atol=atol):
        return type_for(len(b), symmetric=True)
    if np.allclose(b, -b[::-1], rtol=0, atol=atol):
        return type_for(len(b), symmetric=False)
    return None


def check_gains(lp_type, needs):
    """Raise ValueError if a type has a forced zero where gain is needed."""
    clash = [f for f in needs if f in FORCED_ZEROS[lp_type]]
    if clash:
        raise ValueError(
            f"type {'I II III IV'.split()[lp_type - 1]} filters have a forced zero at "
            f"{' and '.join(clash)}, so they cannot pass it. "
            f"Use {'an odd' if lp_type == 2 else 'an even' if lp_type == 3 else 'another'} "
            f"number of taps or another symmetry.")


def check_response(lp_type, btype):
    """Raise ValueError if a type cannot implement a lowpass/highpass/bandpass/bandstop."""
    check_gains(lp_type, NEEDS_GAIN[btype])
