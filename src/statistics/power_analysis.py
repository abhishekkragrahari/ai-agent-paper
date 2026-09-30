"""
Reusable power-analysis functions. These are the exact functions used to
produce the numbers reported in POWER_ANALYSIS.md -- that document's numbers
are not hand-computed, they are this code's output (see
research/power_analysis.py, the script that generated them).
"""
from __future__ import annotations

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

_power_solver = NormalIndPower()


def required_n_per_group(p1: float, p2: float, power: float = 0.80, alpha: float = 0.05) -> float:
    """Required N per group for a two-proportion z-test to detect p1 vs p2
    at the given power and (two-sided) alpha. Returns Cohen's-h-based N."""
    h = proportion_effectsize(p2, p1)
    return _power_solver.solve_power(effect_size=h, alpha=alpha, power=power, alternative="two-sided")


def detectable_effect_size(n_per_group: int, power: float = 0.80, alpha: float = 0.05) -> float:
    """Minimum detectable Cohen's h at a given per-group N, power, alpha."""
    return _power_solver.solve_power(nobs1=n_per_group, alpha=alpha, power=power, alternative="two-sided")
