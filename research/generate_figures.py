#!/usr/bin/env python3
"""Generates results/figures/*.png.

fig1_theory_false_consensus_vs_rho.png: EXACT computation under the model
    verified in FORMAL_RESULTS.md -- a real mathematical result, not
    synthetic/empirical data.
fig2_validation_phi_recovers_planted_rho.png: SYNTHETIC VALIDATION DATA from
    experiments/run_ablations.py's label-vs-phi ablation -- shows the phi
    estimator correctly tracks the KNOWN planted correlation parameter.
    Clearly labeled; not a research finding about real agents.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import betabinom, binom


def fig1():
    p = 0.10
    rhos = np.linspace(0.0, 0.95, 40)
    fig, ax = plt.subplots(figsize=(7, 5))
    for n, q in [(3, 2), (5, 3), (7, 4)]:
        vals = []
        for rho in rhos:
            if rho <= 1e-9:
                v = 1 - binom.cdf(q - 1, n, p)
            else:
                s = (1 - rho) / rho
                a, b = p * s, (1 - p) * s
                v = 1 - betabinom.cdf(q - 1, n, a, b)
            vals.append(v)
        ax.plot(rhos, vals, marker="", linewidth=2, label=f"n={n} (majority q={q})")
    ax.set_xlabel(r"Pairwise error correlation $\rho$")
    ax.set_ylabel("P(false consensus)  [exact, Beta-Binomial model]")
    ax.set_title("EXACT model computation (FORMAL_RESULTS.md) — not empirical data\n"
                  r"$p=0.10$ per-agent error rate; quorum-size scaling collapses as $\rho \to 1$",
                  fontsize=10)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = REPO_ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "fig1_theory_false_consensus_vs_rho.png", dpi=150)
    plt.close(fig)
    print(f"Wrote {out / 'fig1_theory_false_consensus_vs_rho.png'}")


def fig2():
    path = REPO_ROOT / "results" / "ablation_label_vs_phi.csv"
    if not path.exists():
        print("results/ablation_label_vs_phi.csv not found -- run experiments/run_ablations.py first.")
        return
    df = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df["planted_rho"], df["measured_mean_phi"], alpha=0.7,
               c=df["provider_same_label"], cmap="coolwarm", edgecolor="k", linewidth=0.5)
    lims = [0, max(df["planted_rho"].max(), df["measured_mean_phi"].max()) * 1.05]
    ax.plot(lims, lims, "k--", alpha=0.5, label="y = x (perfect recovery)")
    ax.set_xlabel(r"Planted (ground-truth) $\rho$ — known by construction")
    ax.set_ylabel(r"Measured mean pairwise $\hat\phi$")
    ax.set_title("SYNTHETIC VALIDATION DATA — NOT RESEARCH RESULTS\n"
                  "Does the phi estimator recover a known planted correlation? "
                  "(color = coarse provider label)", fontsize=10)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = REPO_ROOT / "results" / "figures"
    fig.savefig(out / "fig2_validation_phi_recovers_planted_rho.png", dpi=150)
    plt.close(fig)
    print(f"Wrote {out / 'fig2_validation_phi_recovers_planted_rho.png'}")


if __name__ == "__main__":
    fig1()
    fig2()
