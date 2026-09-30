"""
Pairwise semantic-error correlation measures, per CORRELATION_MEASUREMENT.md.

All functions take two equal-length boolean arrays (error indicators: True
= agent was WRONG on that task) over the same set of shared tasks, and
return either a point estimate or (estimate, ci_low, ci_high, p_value)
as documented per function. phi_coefficient is the primary measure (see
CORRELATION_MEASUREMENT.md Section 3 for the justification); the others are
retained as diagnostics (Section 4).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.stats import chi2_contingency, fisher_exact


def pairwise_error_table(err_i: np.ndarray, err_j: np.ndarray) -> np.ndarray:
    """2x2 contingency table [[n11,n10],[n01,n00]] for two boolean error arrays."""
    err_i = np.asarray(err_i, dtype=bool)
    err_j = np.asarray(err_j, dtype=bool)
    if err_i.shape != err_j.shape:
        raise ValueError("error arrays must be the same length (same shared tasks)")
    n11 = int(np.sum(err_i & err_j))
    n10 = int(np.sum(err_i & ~err_j))
    n01 = int(np.sum(~err_i & err_j))
    n00 = int(np.sum(~err_i & ~err_j))
    return np.array([[n11, n10], [n01, n00]])


def co_error_probability(err_i: np.ndarray, err_j: np.ndarray) -> float:
    tbl = pairwise_error_table(err_i, err_j)
    n = tbl.sum()
    return tbl[0, 0] / n if n > 0 else float("nan")


def conditional_co_error_probability(err_i: np.ndarray, err_j: np.ndarray) -> Tuple[float, float]:
    """Returns (P(j wrong | i wrong), P(i wrong | j wrong)) -- asymmetric, both reported."""
    tbl = pairwise_error_table(err_i, err_j)
    n11, n10, n01, n00 = tbl[0, 0], tbl[0, 1], tbl[1, 0], tbl[1, 1]
    n1_ = n11 + n10  # i wrong
    n_1 = n11 + n01  # j wrong
    p_j_given_i = n11 / n1_ if n1_ > 0 else float("nan")
    p_i_given_j = n11 / n_1 if n_1 > 0 else float("nan")
    return p_j_given_i, p_i_given_j


def jaccard_agreement_on_error(err_i: np.ndarray, err_j: np.ndarray) -> float:
    tbl = pairwise_error_table(err_i, err_j)
    n11, n10, n01 = tbl[0, 0], tbl[0, 1], tbl[1, 0]
    denom = n11 + n10 + n01
    return n11 / denom if denom > 0 else float("nan")


@dataclass
class PhiResult:
    phi: float
    p_value: float
    test_used: str
    n: int


def phi_coefficient(err_i: np.ndarray, err_j: np.ndarray) -> PhiResult:
    """Pearson correlation of two binary variables (the primary measure).

    Significance: Fisher's exact test when any expected cell count < 5
    (the likely regime under low per-agent error rates, per
    CORRELATION_MEASUREMENT.md Section 5), else Pearson chi-square.
    """
    tbl = pairwise_error_table(err_i, err_j)
    n = tbl.sum()
    n11, n10, n01, n00 = tbl[0, 0], tbl[0, 1], tbl[1, 0], tbl[1, 1]
    n1_, n0_ = n11 + n10, n01 + n00
    n_1, n_0 = n11 + n01, n10 + n00
    denom = np.sqrt(n1_ * n0_ * n_1 * n_0)
    phi = (n11 * n00 - n10 * n01) / denom if denom > 0 else 0.0

    # expected cell counts for the chi-square-vs-exact decision
    expected = np.outer([n1_, n0_], [n_1, n_0]) / n if n > 0 else np.zeros((2, 2))
    use_exact = n == 0 or np.any(expected < 5)
    if use_exact:
        _, p = fisher_exact(tbl)
        test_used = "fisher_exact"
    else:
        _, p, _, _ = chi2_contingency(tbl, correction=True)
        test_used = "chi2"
    return PhiResult(phi=float(phi), p_value=float(p), test_used=test_used, n=int(n))


def mutual_information_binary(err_i: np.ndarray, err_j: np.ndarray, bias_correct: bool = True) -> float:
    """Plug-in mutual information for two binary variables, with an optional
    Miller-Madow bias correction (+ (k-1)/(2n ln 2) in bits, k = number of
    non-empty cells), per CORRELATION_MEASUREMENT.md Section 3.4's
    explicit flag that the uncorrected plug-in estimator is biased under
    sparse joint-error counts. Diagnostic/secondary measure only -- see
    module docstring and CORRELATION_MEASUREMENT.md Section 4.
    """
    tbl = pairwise_error_table(err_i, err_j).astype(float)
    n = tbl.sum()
    if n == 0:
        return float("nan")
    p_xy = tbl / n
    p_x = p_xy.sum(axis=1, keepdims=True)
    p_y = p_xy.sum(axis=0, keepdims=True)
    mi = 0.0
    nonzero_cells = 0
    for a in range(2):
        for b in range(2):
            if p_xy[a, b] > 0 and p_x[a, 0] > 0 and p_y[0, b] > 0:
                mi += p_xy[a, b] * np.log2(p_xy[a, b] / (p_x[a, 0] * p_y[0, b]))
                nonzero_cells += 1
    if bias_correct and n > 0:
        mi += (nonzero_cells - 1) / (2 * n * np.log(2))
    return float(mi)


def bootstrap_ci(values: np.ndarray, statistic=np.mean, n_boot: int = 2000,
                  alpha: float = 0.05, seed: int = 0) -> Tuple[float, float, float]:
    """Generic percentile bootstrap CI. Returns (point_estimate, ci_low, ci_high)."""
    values = np.asarray(values)
    rng = np.random.default_rng(seed)
    point = float(statistic(values))
    if len(values) == 0:
        return point, float("nan"), float("nan")
    boots = np.empty(n_boot)
    n = len(values)
    for b in range(n_boot):
        sample = values[rng.integers(0, n, size=n)]
        boots[b] = statistic(sample)
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)
