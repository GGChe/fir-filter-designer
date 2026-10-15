import numpy as np

from .linear_phase import linear_phase_type


class FIRFilter:
    """
    Direct-form FIR filter that processes a signal in realtime mode, one sample at a time.

    The last N input samples are kept in a circular buffer. Each sample is
    written twice, at position p and p + N, so Buffer[p:p + N] always holds
    the history newest-first as one contiguous slice and the output is a
    single dot product with the coefficients (N multiplications per sample).
    """
    def __init__(self, coefficients):
        self.coefficients = np.asarray(coefficients, dtype=float)
        self.NTAPS = len(self.coefficients)
        self.reset()

    def reset(self):
        """Clear the delay line so the filter can be reused on a new signal."""
        self.Buffer = np.zeros(2 * self.NTAPS)
        self.offset = 0

    def _push(self, v):
        """Store a new sample and return the history x[n], x[n-1], ... x[n-N+1]."""
        self.offset = (self.offset - 1) % self.NTAPS
        self.Buffer[self.offset] = v
        self.Buffer[self.offset + self.NTAPS] = v
        return self.Buffer[self.offset:self.offset + self.NTAPS]

    @property
    def multiplications(self):
        """Multiplications per output sample."""
        return self.NTAPS

    def dofilter(self, v):
        return float(np.dot(self.coefficients, self._push(v)))

    def filter(self, x):
        """Run a whole signal through dofilter() sample by sample."""
        y = np.zeros(len(x))
        for i in range(len(x)):
            y[i] = self.dofilter(x[i])
        return y


class LinearPhaseFIR(FIRFilter):
    """
    Folded FIR filter for linear-phase coefficients (types I to IV).

    Symmetric (I, II) or antisymmetric (III, IV) coefficients satisfy
    h[k] = +-h[N-1-k], so pairs of samples are added (or subtracted) before
    multiplying: about N/2 multiplications per sample instead of N. This is
    the structure used in hardware; in NumPy the speed is about the same.
    """
    def __init__(self, coefficients):
        super().__init__(coefficients)
        self.type = linear_phase_type(self.coefficients)
        if self.type is None:
            raise ValueError("coefficients are neither symmetric nor antisymmetric")
        self._sign = 1 if self.type in (1, 2) else -1
        self._half = self.NTAPS // 2
        self._fold_coefficients = self.coefficients[:self._half]
        # Type III's centre tap is 0, so only type I uses it.
        self._center = self.coefficients[self._half] if self.type == 1 else 0.0

    @property
    def multiplications(self):
        return self._half + (self.type == 1)

    def dofilter(self, v):
        w = self._push(v)
        n, m = self.NTAPS, self._half
        folded = w[:m] + self._sign * w[n - 1:n - 1 - m:-1]
        result = np.dot(self._fold_coefficients, folded)
        if self._center:
            result += self._center * w[m]
        return float(result)


class FIR_filter(FIRFilter):
    """Old name kept for existing scripts: FIR_filter(coefficients, NTAPS)."""
    def __init__(self, coefficients, NTAPS=None):
        if NTAPS is not None and NTAPS != len(coefficients):
            raise ValueError(f"NTAPS={NTAPS} but {len(coefficients)} coefficients were given")
        super().__init__(coefficients)
