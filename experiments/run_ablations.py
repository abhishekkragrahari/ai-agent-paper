#!/usr/bin/env python3
"""
Ablation: measured correlation (phi) vs. provider LABEL as a predictor of
false consensus (Phase 11.4 -- the most important ablation per the process
instructions). Runs on the mock backend at smoke-test scale: SYNTHETIC
VALIDATION DATA. This demonstrates the ANALYSIS METHOD correctly detects
that a phi-based model fits better than a label-based model when the true
generative process is phi-like by construction (a positive-control-style
check of the comparison methodology) -- it does NOT show that this holds
for real LLM-agent data, which requires real execution (blocked; see
FINAL_RESEARCH_STATUS.md).

Also runs the quorum-size sweep, structural-dependence ablation, and
task-domain ablation as simple slices of the factorial smoke-test output
(results/summary_results.csv, produced by run_factorial_experiment.py --
run that first).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.agents.base import Agent, TaskItem
from src.agents.mock_backend import CorrelatedMockBackend
from src.correlation.measures import phi_coefficient
from src.metrics.gsm8k_scoring import extract_gsm8k_gold
from src.metrics.mock_scoring import mock_scorer
from src.quorum.admission import Quorum

LABEL = "SYNTHETIC VALIDATION DATA -- NOT RESEARCH RESULTS"


def load_gsm8k(n):
    path = REPO_ROOT / "datasets" / "gsm8k" / "test.jsonl"
    with open(path) as f:
        lines = f.readlines()[:n]
    tasks = []
    for i, line in enumerate(lines):
        row = json.loads(line)
        gold = extract_gsm8k_gold(row["answer"])
        tasks.append(TaskItem(domain="gsm8k", task_id=f"gsm8k_{i}", prompt=row["question"], gold=gold))
    return tasks


def label_vs_behavioral_ablation():
    """Compare: does provider-SAME-LABEL or MEASURED mean-pairwise-phi
    better predict quorum-level false consensus, across many quorums with
    varying, KNOWN, planted correlation structure?"""
    n_agents = 5
    n_tasks = 150
    quorums_config = []
    # sweep planted rho across many synthetic "quorums" (each a distinct run)
    rng = np.random.default_rng(0)
    for trial in range(40):
        rho = rng.uniform(0.0, 0.7)
        same_label = rho > 0.35  # a NOISY, coarse label: true only ~roughly correlated with rho
        # deliberately add label noise so label and phi are not perfectly co-linear,
        # mirroring the real-world worry (Reviewer #2) that provider label is a
        # coarse, imperfect proxy for true behavioral correlation
        if rng.random() < 0.15:
            same_label = not same_label
        quorums_config.append((trial, rho, same_label))

    tasks_pool = load_gsm8k(n_tasks)
    rows = []
    for trial, rho, same_label in quorums_config:
        provider = "clusterX" if same_label else None
        agents = [
            Agent(agent_id=f"a{i}", provider=(provider if provider else f"cluster{i}"), model_name="mock")
            for i in range(n_agents)
        ]
        backend = CorrelatedMockBackend(p=0.10, rho=rho, cluster_key=lambda a: a.provider)
        quorum = Quorum(agents)

        per_agent_err = {a.agent_id: [] for a in agents}
        fc_flags = []
        for t in tasks_pool:
            outcome = quorum.run(t, backend, seed=trial, scorer=mock_scorer)
            for a, c in zip(agents, outcome.correctness):
                per_agent_err[a.agent_id].append(not c)
            fc_flags.append(outcome.is_false_consensus)

        # measured mean pairwise phi for this quorum
        ids = list(per_agent_err.keys())
        phis = []
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                r = phi_coefficient(np.array(per_agent_err[ids[i]]), np.array(per_agent_err[ids[j]]))
                phis.append(r.phi)
        mean_phi = float(np.mean(phis))

        rows.append({
            "trial": trial, "planted_rho": rho, "provider_same_label": int(same_label),
            "measured_mean_phi": mean_phi, "false_consensus_rate": float(np.mean(fc_flags)),
        })

    df = pd.DataFrame(rows)

    # Model A: predict false_consensus_rate from provider_same_label (coarse label)
    Xa = sm.add_constant(df[["provider_same_label"]])
    # Model B: predict from measured_mean_phi (continuous, behavioral)
    Xb = sm.add_constant(df[["measured_mean_phi"]])
    y = df["false_consensus_rate"]

    model_a = sm.OLS(y, Xa).fit()
    model_b = sm.OLS(y, Xb).fit()

    return df, model_a, model_b


def quorum_size_and_structural_ablation():
    summary_path = REPO_ROOT / "results" / "summary_results.csv"
    if not summary_path.exists():
        print("results/summary_results.csv not found -- run run_factorial_experiment.py first.")
        return None
    df = pd.read_csv(summary_path)
    by_size = df.groupby("n_agents")["false_consensus_rate"].mean().reset_index()
    by_structural = df.groupby("structural")["false_consensus_rate"].mean().reset_index()
    by_domain = df.groupby("domain")["false_consensus_rate"].mean().reset_index()
    return by_size, by_structural, by_domain


def main():
    print("=" * 78)
    print(f"ABLATION STUDIES [{LABEL}]")
    print("=" * 78)

    print("\n--- Ablation 4 (Phase 11.4): measured phi vs. provider label as predictor ---")
    df, model_a, model_b = label_vs_behavioral_ablation()
    print(f"Model A (label-only):  R^2={model_a.rsquared:.4f}  AIC={model_a.aic:.2f}")
    print(f"Model B (measured phi): R^2={model_b.rsquared:.4f}  AIC={model_b.aic:.2f}")
    better = "measured phi" if model_b.aic < model_a.aic else "provider label"
    print(f"Lower-AIC model (better fit, in THIS synthetic construction): {better}")
    print("NOTE: this demonstrates the comparison methodology works correctly when the ")
    print("true generative process is phi-like by construction. It does NOT establish ")
    print("this holds for real LLM-agent data -- that test is BLOCKED (no API access).")

    out_dir = REPO_ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    df["DATA_LABEL"] = LABEL
    df.to_csv(out_dir / "ablation_label_vs_phi.csv", index=False)

    print("\n--- Quorum-size / structural / domain ablations (slices of factorial smoke test) ---")
    res = quorum_size_and_structural_ablation()
    if res:
        by_size, by_structural, by_domain = res
        print("\nBy quorum size:\n", by_size.to_string(index=False))
        print("\nBy structural condition:\n", by_structural.to_string(index=False))
        print("\nBy domain:\n", by_domain.to_string(index=False))

    print(f"\nWrote {out_dir / 'ablation_label_vs_phi.csv'}")


if __name__ == "__main__":
    main()
