"""Design, run and analyse FIR filters.

Plots are in firdesigner.plotting, which is not imported here so the rest
of the package works without matplotlib.
"""
from .filter import FIRFilter, FIR_filter, LinearPhaseFIR
from . import analysis, designer, linear_phase

__all__ = ['FIRFilter', 'FIR_filter', 'LinearPhaseFIR', 'analysis', 'designer', 'linear_phase']
