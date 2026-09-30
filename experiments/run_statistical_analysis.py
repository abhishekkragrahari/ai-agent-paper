#!/usr/bin/env python3
"""
Produces results/statistical_tests.csv and results/correlation_matrix.csv
from a pipeline smoke-test run (mock backend, reduced N -- see
run_factorial_experiment.py's banner). SYNTHETIC VALIDATION DATA, not
research results -- labeled throughout.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import json
import numpy as np
import pandas as pd

from src.agents.base import Agent
from src.agents.mock_backend import CorrelatedMockBackend
from src.correlation.measures import phi_coefficient
from src.metrics.mock_scoring import mock_scorer
from src.metrics.gsm8k_scoring import extract_gsm8k_gold
from src.agents.base import TaskItem
from src.quorum.admission import Quorum
from src.statistics.hypothesis_tests import two_proportion_test

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


def run_condition(n_tasks, n_agents, rho, seed):
    tasks = load_gsm8k(n_tasks)
    agents = [Agent(agent_id=f"a{i}", provider="cluster0" if rho > 0.3 else f"cluster{i}",
                     model_name="mock") for i in range(n_agents)]
    backend = CorrelatedMockBackend(p=0.10, rho=rho, cluster_key=lambda a: a.provider)
    quorum = Quorum(agents)
    per_agent_correct = {a.agent_id: [] for a in agents}
    false_consensus_count = 0
    for t in tasks:
        outcome = quorum.run(t, backend, seed=seed, scorer=mock_scorer)
        for a, c in zip(agents, outcome.correctness):
            per_agent_correct[a.agent_id].append(c)
        false_consensus_count += int(outcome.is_false_consensus)
    return per_agent_correct, false_consensus_count, n_tasks


def main():
    out_dir = REPO_ROOT / "results"
    out_dir.mkdir(exist_ok=True)

    N_TASKS = 200
    N_AGENTS = 5

    low_correct, low_fc, low_n = run_condition(N_TASKS, N_AGENTS, rho=0.02, seed=20260930)
    high_correct, high_fc, high_n = run_condition(N_TASKS, N_AGENTS, rho=0.55, seed=20260930)

    # --- statistical_tests.csv: primary pre-registered two-proportion test ---
    test_result = two_proportion_test(low_fc, low_n, high_fc, high_n)
    stats_rows = [{
        "test_name": "primary_H1_two_proportion_ztest",
        "group1": "low_correlation", "group1_successes": low_fc, "group1_n": low_n,
        "group2": "high_correlation", "group2_successes": high_fc, "group2_n": high_n,
        "p1": test_result.p1, "p2": test_result.p2,
        "z_stat": test_result.z_stat, "p_value": test_result.p_value,
        "risk_difference": test_result.risk_difference,
        "risk_difference_ci_low": test_result.risk_difference_ci[0],
        "risk_difference_ci_high": test_result.risk_difference_ci[1],
        "note": "Smoke-test N (200/group), NOT the pre-registered N=350/group from POWER_ANALYSIS.md -- "
                "underpowered by design; demonstrates the analysis code runs correctly end-to-end.",
        "DATA_LABEL": LABEL,
    }]
    pd.DataFrame(stats_rows).to_csv(out_dir / "statistical_tests.csv", index=False)

    # --- correlation_matrix.csv: pairwise phi for the high-correlation condition (5x5) ---
    agent_ids = list(high_correct.keys())
    rows = []
    for i, ai in enumerate(agent_ids):
        for j, aj in enumerate(agent_ids):
            if i >= j:
                continue
            erri = np.array([not c for c in high_correct[ai]])
            errj = np.array([not c for c in high_correct[aj]])
            res = phi_coefficient(erri, errj)
            rows.append({
                "agent_i": ai, "agent_j": aj, "condition": "high_correlation_cluster",
                "phi": res.phi, "p_value": res.p_value, "test_used": res.test_used, "n": res.n,
                "DATA_LABEL": LABEL,
            })
    for i, ai in enumerate(agent_ids):
        for j, aj in enumerate(agent_ids):
            if i >= j:
                continue
            erri = np.array([not c for c in low_correct[ai]])
            errj = np.array([not c for c in low_correct[aj]])
            res = phi_coefficient(erri, errj)
            rows.append({
                "agent_i": ai, "agent_j": aj, "condition": "low_correlation_independent",
                "phi": res.phi, "p_value": res.p_value, "test_used": res.test_used, "n": res.n,
                "DATA_LABEL": LABEL,
            })
    pd.DataFrame(rows).to_csv(out_dir / "correlation_matrix.csv", index=False)

    print(f"[{LABEL}]")
    print(f"Primary test: z={test_result.z_stat:.3f}, p={test_result.p_value:.4g}, "
          f"risk_diff={test_result.risk_difference:.4f} "
          f"[{test_result.risk_difference_ci[0]:.4f}, {test_result.risk_difference_ci[1]:.4f}]")
    print(f"(low_fc={low_fc}/{low_n}={low_fc/low_n:.4f}, high_fc={high_fc}/{high_n}={high_fc/high_n:.4f})")
    print(f"NOTE: N={N_TASKS}/group is the smoke-test size, not the pre-registered N=350 -- "
          f"this p-value is illustrative of the pipeline, not a powered inferential result.")
    print(f"\nWrote {out_dir / 'statistical_tests.csv'}")
    print(f"Wrote {out_dir / 'correlation_matrix.csv'}")
    mean_phi_high = np.mean([r["phi"] for r in rows if r["condition"] == "high_correlation_cluster"])
    mean_phi_low = np.mean([r["phi"] for r in rows if r["condition"] == "low_correlation_independent"])
    print(f"\nMean pairwise phi, high-correlation condition: {mean_phi_high:.4f}")
    print(f"Mean pairwise phi, low-correlation condition:  {mean_phi_low:.4f}")


if __name__ == "__main__":
    main()
