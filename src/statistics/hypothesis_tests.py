"""
Pre-registered statistical tests, per POWER_ANALYSIS.md Sections 1 and 7.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportions_ztest


@dataclass
class TwoProportionResult:
    p1: float
    p2: float
    n1: int
    n2: int
    z_stat: float
    p_value: float
    risk_difference: float
    risk_difference_ci: Tuple[float, float]


def two_proportion_test(successes1: int, n1: int, successes2: int, n2: int,
                         alpha: float = 0.05) -> TwoProportionResult:
    """Primary pre-registered test (POWER_ANALYSIS.md Section 1): two-proportion
    z-test comparing false-consensus rate between two correlation-level groups."""
    counts = np.array([successes1, successes2])
    nobs = np.array([n1, n2])
    z_stat, p_value = proportions_ztest(counts, nobs)

    p1, p2 = successes1 / n1, successes2 / n2
    rd = p2 - p1
    # Wald CI for risk difference (reporting only -- planning used Cohen's h, see POWER_ANALYSIS.md Section 7)
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    from scipy.stats import norm
    z_crit = norm.ppf(1 - alpha / 2)
    ci = (rd - z_crit * se, rd + z_crit * se)

    return TwoProportionResult(
        p1=p1, p2=p2, n1=n1, n2=n2,
        z_stat=float(z_stat), p_value=float(p_value),
        risk_difference=float(rd), risk_difference_ci=ci,
    )


def logistic_regression_false_consensus(df: pd.DataFrame, phi_col: str = "mean_pairwise_phi",
                                         outcome_col: str = "is_false_consensus",
                                         covariate_cols: List[str] = ("domain_code", "n_agents")):
    """Secondary/main effect-size model (POWER_ANALYSIS.md Section 7):
    logistic regression of the false-consensus outcome on measured
    correlation plus covariates. Returns the fitted statsmodels result;
    caller reports the phi coefficient as an odds ratio with a Wald CI."""
    cols = [phi_col] + list(covariate_cols)
    X = sm.add_constant(df[cols])
    y = df[outcome_col].astype(int)
    model = sm.Logit(y, X)
    return model.fit(disp=0)


def benjamini_hochberg(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """Benjamini-Hochberg FDR correction, per CORRELATION_MEASUREMENT.md
    Section 5. Returns a boolean list (same order as input) of which
    hypotheses are rejected at the given FDR level."""
    p = np.asarray(p_values)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    thresh = (np.arange(1, n + 1) / n) * alpha
    below = ranked <= thresh
    if not np.any(below):
        return [False] * n
    max_rank = np.max(np.where(below)[0])
    reject_sorted = np.zeros(n, dtype=bool)
    reject_sorted[: max_rank + 1] = True
    reject = np.zeros(n, dtype=bool)
    reject[order] = reject_sorted
    return reject.tolist()
