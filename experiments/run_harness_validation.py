#!/usr/bin/env python3
"""
HARNESS SANITY CHECK — software validation only, NOT a replication of any
real LLM finding (that is blocked: no API credentials in this environment,
see FINAL_RESEARCH_STATUS.md).

This script answers the literal question Phase 8 of the process asked:
"Does our harness reproduce a known correlation effect before we trust the
larger experiment?" — using POSITIVE and NEGATIVE CONTROLS with a KNOWN,
PLANTED ground-truth correlation (via CorrelatedMockBackend, which
implements exactly the model verified in FORMAL_RESULTS.md), rather than
real LLM data, which is unavailable here.

Negative control: plant rho=0 (independent agents). Expect: estimated phi
  coefficient consistent with 0; observed false-consensus rate consistent
  with the independent-Binomial prediction from FORMAL_RESULTS.md.
Positive control: plant rho=0.5. Expect: estimated phi coefficient
  consistent with 0.5; observed false-consensus rate consistent with the
  Beta-Binomial prediction from FORMAL_RESULTS.md Section 6's table.

If either control fails, the pipeline has a bug and the factorial
experiment must NOT be trusted until it is fixed. Results (pass/fail) are
reported honestly either way.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy.stats import betabinom, binom

from src.agents.base import Agent, TaskItem
from src.agents.mock_backend import CorrelatedMockBackend
from src.correlation.measures import phi_coefficient, bootstrap_ci
from src.metrics.mock_scoring import mock_scorer
from src.quorum.admission import Quorum


def load_gsm8k_tasks(n: int, offset: int = 0):
    path = REPO_ROOT / "datasets" / "gsm8k" / "test.jsonl"
    tasks = []
    with open(path) as f:
        lines = f.readlines()[offset: offset + n]
    for i, line in enumerate(lines):
        row = json.loads(line)
        gold = row["answer"].split("####")[-1].strip().replace(",", "")
        tasks.append(TaskItem(domain="gsm8k", task_id=f"gsm8k_{offset+i}",
                               prompt=row["question"], gold=gold))
    return tasks


def run_control(rho_planted: float, p: float, n_tasks: int, n_agents: int, seed: int):
    tasks = load_gsm8k_tasks(n_tasks)
    backend = CorrelatedMockBackend(p=p, rho=rho_planted)
    agents = [Agent(agent_id=f"a{i}", provider="sharedCluster", model_name="mock-model")
              for i in range(n_agents)]
    quorum = Quorum(agents)

    outcomes = []
    for t in tasks:
        outcomes.append(quorum.run(t, backend, seed=seed, scorer=mock_scorer))

    # pairwise phi between agent 0 and agent 1's error indicators across tasks
    err0 = np.array([not o.correctness[0] for o in outcomes])
    err1 = np.array([not o.correctness[1] for o in outcomes])
    phi_result = phi_coefficient(err0, err1)

    # observed false-consensus rate
    fc = np.array([o.is_false_consensus for o in outcomes], dtype=float)
    fc_point, fc_lo, fc_hi = bootstrap_ci(fc, statistic=np.mean)

    # theoretical prediction from FORMAL_RESULTS.md's exact model
    q = n_agents // 2 + 1
    if rho_planted <= 1e-9:
        theo_fc = 1 - binom.cdf(q - 1, n_agents, p)
    else:
        s = (1 - rho_planted) / rho_planted
        a, b = p * s, (1 - p) * s
        theo_fc = 1 - betabinom.cdf(q - 1, n_agents, a, b)

    return {
        "rho_planted": rho_planted,
        "p": p,
        "n_tasks": n_tasks,
        "n_agents": n_agents,
        "estimated_phi": phi_result.phi,
        "phi_p_value": phi_result.p_value,
        "observed_false_consensus_rate": fc_point,
        "fc_ci": (fc_lo, fc_hi),
        "theoretical_false_consensus_rate": theo_fc,
    }


def main():
    print("=" * 78)
    print("HARNESS SANITY CHECK -- SOFTWARE VALIDATION ONLY, NOT RESEARCH RESULTS")
    print("Uses real GSM8K questions but a SYNTHETIC mock backend with a KNOWN,")
    print("PLANTED correlation. This is NOT a replication of arXiv:2603.06612 or")
    print("any real LLM finding -- that replication is BLOCKED (no API access).")
    print("=" * 78)

    N_TASKS = 500
    N_AGENTS = 5
    P = 0.10

    results = {}
    for label, rho in [("NEGATIVE_CONTROL_rho=0", 0.0), ("POSITIVE_CONTROL_rho=0.5", 0.5)]:
        r = run_control(rho_planted=rho, p=P, n_tasks=N_TASKS, n_agents=N_AGENTS, seed=42)
        results[label] = r
        print(f"\n--- {label} ---")
        print(f"  planted rho                    = {r['rho_planted']}")
        print(f"  estimated phi (agents 0 vs 1)   = {r['estimated_phi']:.4f}  (p={r['phi_p_value']:.4g})")
        print(f"  observed false-consensus rate   = {r['observed_false_consensus_rate']:.4f}  "
              f"95% CI [{r['fc_ci'][0]:.4f}, {r['fc_ci'][1]:.4f}]")
        print(f"  theoretical false-consensus rate= {r['theoretical_false_consensus_rate']:.4f}")
        theo_in_ci = r['fc_ci'][0] <= r['theoretical_false_consensus_rate'] <= r['fc_ci'][1]
        print(f"  theoretical value inside observed 95% CI? {theo_in_ci}")

    print("\n" + "=" * 78)
    neg = results["NEGATIVE_CONTROL_rho=0"]
    pos = results["POSITIVE_CONTROL_rho=0.5"]
    neg_pass = abs(neg["estimated_phi"]) < 0.10  # near zero, loose tolerance at N=500
    pos_pass = abs(pos["estimated_phi"] - 0.5) < 0.15
    print(f"NEGATIVE CONTROL phi near 0?  {neg_pass}  (estimated={neg['estimated_phi']:.4f})")
    print(f"POSITIVE CONTROL phi near 0.5? {pos_pass}  (estimated={pos['estimated_phi']:.4f})")
    overall = neg_pass and pos_pass
    print(f"\nHARNESS SANITY CHECK: {'PASSED' if overall else 'FAILED'}")
    print("=" * 78)

    out_dir = REPO_ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "harness_validation_report.json", "w") as f:
        json.dump({
            "label": "SYNTHETIC VALIDATION DATA -- NOT RESEARCH RESULTS",
            "results": {k: {kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()}
                        for k, v in results.items()},
            "negative_control_passed": neg_pass,
            "positive_control_passed": pos_pass,
            "overall_passed": overall,
        }, f, indent=2)
    print(f"\nReport written to {out_dir / 'harness_validation_report.json'}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
