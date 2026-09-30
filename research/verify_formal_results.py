"""
Reproducible verification of every claim in FORMAL_RESULTS.md.

This script re-derives (symbolically, via SymPy) and re-checks (numerically,
via SciPy's exact Beta-Binomial implementation) the lemmas and theorem stated
in FORMAL_RESULTS.md. It produces no research results about any real system;
it verifies mathematics about a stated model.

Run: python3 research/verify_formal_results.py
"""
import sympy as sp
import numpy as np
from scipy.stats import betabinom, binom


def alpha_beta(p, rho):
    s = (1 - rho) / rho
    return p * s, (1 - p) * s


def exact_false_consensus(n, q, p, rho):
    """Exact P(K >= q) under Beta-Binomial(n, alpha(p,rho), beta(p,rho))."""
    if rho <= 1e-9:
        return 1 - binom.cdf(q - 1, n, p)
    a, b = alpha_beta(p, rho)
    return 1 - betabinom.cdf(q - 1, n, a, b)


def cantelli_bound(n, q, p, rho):
    """One-sided Chebyshev (Cantelli) upper bound on P(K >= q), q > n*p."""
    var_K = n * p * (1 - p) * (1 + (n - 1) * rho)
    mean_K = n * p
    if q <= mean_K:
        return 1.0
    d = q - mean_K
    return var_K / (var_K + d ** 2)


def symbolic_checks():
    print("=" * 70)
    print("SYMBOLIC VERIFICATION (SymPy, exact algebra)")
    print("=" * 70)
    a, b, s, p, rho, n_, q_ = sp.symbols('a b s p rho n q', positive=True)

    # Var(Theta) for Theta ~ Beta(a,b), reparametrized by p=a/(a+b), rho=1/(a+b+1)
    var_theta = a * b / ((a + b) ** 2 * (a + b + 1))
    var_theta_sub = var_theta.subs({a: p * s, b: (1 - p) * s})
    var_theta_rho = sp.simplify(var_theta_sub.subs(s, (1 - rho) / rho))
    diff1 = sp.simplify(var_theta_rho - p * (1 - p) * rho)
    print(f"Var(Theta) - p(1-p)rho  = {diff1}   [expect 0]")
    assert diff1 == 0

    # Var(K) = E[Var(K|Theta)] + Var(E[K|Theta])  vs claimed n p(1-p)[1+(n-1)rho]
    E_VarK_given_Theta = sp.simplify(n_ * p - n_ * (p * (1 - p) * rho + p ** 2))
    Var_EK_given_Theta = n_ ** 2 * p * (1 - p) * rho
    VarK_total = sp.simplify(E_VarK_given_Theta + Var_EK_given_Theta)
    claimed = n_ * p * (1 - p) * (1 + (n_ - 1) * rho)
    diff2 = sp.simplify(VarK_total - claimed)
    print(f"Var(K) - n*p(1-p)[1+(n-1)rho] = {diff2}   [expect 0]")
    assert diff2 == 0

    # Monotonicity of Cantelli bound in rho
    var_expr = n_ * p * (1 - p) * (1 + (n_ - 1) * rho)
    d = q_ - n_ * p
    bound_expr = var_expr / (var_expr + d ** 2)
    dbound_drho = sp.simplify(sp.diff(bound_expr, rho))
    test_val = float(dbound_drho.subs({n_: 5, p: 0.1, rho: 0.3, q_: 3}))
    print(f"d(Cantelli bound)/d(rho) at (n=5,p=0.1,rho=0.3,q=3) = {test_val:.6f}   [expect > 0]")
    assert test_val > 0
    print("All symbolic checks PASSED.\n")


def numeric_checks():
    print("=" * 70)
    print("NUMERICAL VERIFICATION (SciPy, exact Beta-Binomial)")
    print("=" * 70)
    p = 0.10

    # Mean invariance
    n = 5
    print("Mean invariance E[K]=n*p:")
    for rho in [0.01, 0.3, 0.7, 0.95]:
        a, b = alpha_beta(p, rho)
        mean_K = betabinom.mean(n, a, b)
        assert abs(mean_K - n * p) < 1e-9
        print(f"  rho={rho}: E[K]={mean_K:.6f} (n*p={n*p})  OK")

    # Variance closed form
    print("\nVariance closed form Var(K)=n*p(1-p)[1+(n-1)rho]:")
    for rho in [0.01, 0.3, 0.7, 0.95]:
        a, b = alpha_beta(p, rho)
        var_K = betabinom.var(n, a, b)
        closed = n * p * (1 - p) * (1 + (n - 1) * rho)
        assert abs(var_K - closed) < 1e-9
        print(f"  rho={rho}: Var(K)={var_K:.6f} closed_form={closed:.6f}  diff={abs(var_K-closed):.2e}  OK")

    # Cantelli bound validity (never violated) across grid
    print("\nCantelli bound validity (exact P(FC) <= bound) across grid:")
    all_valid = True
    rows = []
    for n, q in [(3, 2), (5, 3), (7, 4)]:
        for rho in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
            exact = exact_false_consensus(n, q, p, rho)
            bound = cantelli_bound(n, q, p, rho)
            valid = exact <= bound + 1e-9
            all_valid &= valid
            rows.append((n, q, rho, exact, bound, valid))
    for n, q, rho, exact, bound, valid in rows:
        print(f"  n={n} q={q} rho={rho:.2f}: exact={exact:.6f} bound={bound:.6f} valid={valid}")
    assert all_valid
    print("\nAll numeric checks PASSED.")
    return rows


if __name__ == "__main__":
    symbolic_checks()
    numeric_checks()
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE: all claims in FORMAL_RESULTS.md reproduced.")
    print("=" * 70)
