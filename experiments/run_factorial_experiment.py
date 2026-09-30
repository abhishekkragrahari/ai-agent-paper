#!/usr/bin/env python3
"""
Driver for the pre-registered factorial design in configs/experiment_design.yaml.

This script is REAL and RUNNABLE against a real backend (AnthropicBackend /
OpenAIBackend) the moment credentials are provisioned -- pass --backend
anthropic|openai. It refuses to run a real backend without the matching API
key (raises MissingCredentialsError from src/agents/real_backends.py rather
than silently substituting mock behavior).

Run with --backend mock (the default) to execute a SOFTWARE PIPELINE SMOKE
TEST at a REDUCED task count (not the pre-registered N=350/cell -- that
would require real API access to be worth running at full cost). Output
from a mock run is written with an unambiguous "SYNTHETIC VALIDATION DATA"
label in every file and must never be read as a research finding.
"""
import argparse
import csv
import itertools
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import yaml

from src.agents.base import Agent, TaskItem
from src.agents.mock_backend import CorrelatedMockBackend
from src.agents.real_backends import AnthropicBackend, OpenAIBackend, MissingCredentialsError
from src.correlation.measures import phi_coefficient
from src.metrics.gsm8k_scoring import gsm8k_scorer, extract_gsm8k_gold
from src.metrics.squad_scoring import squad2_scorer
from src.metrics.mock_scoring import mock_scorer
from src.quorum.admission import Quorum


def load_gsm8k(n, offset=0):
    path = REPO_ROOT / "datasets" / "gsm8k" / "test.jsonl"
    with open(path) as f:
        lines = f.readlines()[offset: offset + n]
    tasks = []
    for i, line in enumerate(lines):
        row = json.loads(line)
        gold = extract_gsm8k_gold(row["answer"])
        tasks.append(TaskItem(domain="gsm8k", task_id=f"gsm8k_{offset+i}", prompt=row["question"], gold=gold))
    return tasks


def load_squad2(n, offset=0):
    path = REPO_ROOT / "datasets" / "squad2" / "dev-v2.0.json"
    with open(path) as f:
        data = json.load(f)
    flat = []
    for article in data["data"]:
        for para in article["paragraphs"]:
            for qa in para["qas"]:
                gold_answers = tuple(a["text"] for a in qa.get("answers", []))
                is_impossible = qa.get("is_impossible", False)
                flat.append((qa["id"], qa["question"], para["context"], gold_answers, is_impossible))
    flat = flat[offset: offset + n]
    return [TaskItem(domain="squad2", task_id=qid, prompt=q, gold=(ga, imp), context=ctx)
            for qid, q, ctx, ga, imp in flat]


def build_agent_pool(n_agents, structural_level, correlation_level, domain_context=None):
    """Builds an agent pool realizing the requested structural and
    correlation-level FACTORS. The correlation_level controls provider
    CLUSTER COMPOSITION only (a controllable input to the mock backend's
    clustering); the ACTUAL realized correlation is measured after the
    fact (src/correlation/measures.py), never assumed from this label --
    this is the pipeline-level enforcement of CORRELATION_MEASUREMENT.md's
    core methodological rule."""
    agents = []
    for i in range(n_agents):
        if correlation_level == "low":
            provider = f"cluster{i}"          # every agent its own cluster
        elif correlation_level == "high":
            provider = "cluster0"              # all agents share one cluster
        else:  # medium
            provider = f"cluster{i % 2}"       # two clusters, mixed

        if structural_level == "kappa_E_unsafe" and domain_context is not None:
            deps = frozenset({"context:shared_passage"})
        elif structural_level == "kappa_E_unsafe":
            deps = frozenset({"tool:shared_retriever"})
        else:
            deps = frozenset({f"tool:isolated_retriever_{i}"})  # each agent's own, non-overlapping

        agents.append(Agent(agent_id=f"a{i}", provider=provider, model_name="mock-model",
                             structural_dependencies=deps))
    return agents


RHO_BY_LEVEL = {"low": 0.02, "medium": 0.20, "high": 0.55}  # mock backend planted rho per label,
# chosen only to realize a monotonic low<medium<high MEASURED correlation in the
# smoke test -- never presented as an empirical finding about real correlation magnitudes.


def make_backend(args):
    if args.backend == "mock":
        return CorrelatedMockBackend(p=0.10, rho=0.0)  # rho overridden per-cell below via cluster_key trick
    elif args.backend == "anthropic":
        return AnthropicBackend()
    elif args.backend == "openai":
        return OpenAIBackend()
    raise ValueError(args.backend)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["mock", "anthropic", "openai"], default="mock")
    ap.add_argument("--smoke-test", action="store_true", default=True,
                     help="Reduced task count for pipeline validation, NOT the pre-registered N.")
    ap.add_argument("--tasks-per-cell", type=int, default=30,
                     help="Default 30 = smoke-test size. Pre-registered N is 350 (configs/experiment_design.yaml).")
    ap.add_argument("--seeds", type=int, default=2)
    args = ap.parse_args()

    design = yaml.safe_load(open(REPO_ROOT / "configs" / "experiment_design.yaml"))

    is_real = args.backend != "mock"
    if is_real:
        try:
            make_backend(args)
        except Exception:
            pass  # credential check happens per-call; we still want the loop below to raise clearly

    label = "REAL EXPERIMENT RESULTS" if is_real else "SYNTHETIC VALIDATION DATA -- NOT RESEARCH RESULTS"
    print("=" * 78)
    print(f"FACTORIAL EXPERIMENT DRIVER -- backend={args.backend}  [{label}]")
    if not is_real:
        print(f"Running a PIPELINE SMOKE TEST at N={args.tasks_per_cell}/cell "
              f"(pre-registered N is {design['sample_size']['tasks_per_cell']}/cell -- "
              f"see POWER_ANALYSIS.md). This validates that the pipeline runs end-to-end")
        print("and produces correctly-shaped output. It is NOT a powered experiment and")
        print("NOT a finding about real LLM-agent behavior.")
    print("=" * 78)

    gsm8k_pool = load_gsm8k(args.tasks_per_cell + 5)
    squad_pool = load_squad2(args.tasks_per_cell + 5)

    raw_rows = []
    for structural, corr_level, n_agents, domain in itertools.product(
        design["factors"]["structural"]["levels"],
        design["factors"]["correlation_level"]["levels"],
        design["factors"]["quorum_size"]["levels"],
        design["factors"]["domain"]["levels"],
    ):
        tasks = (gsm8k_pool if domain == "gsm8k" else squad_pool)[: args.tasks_per_cell]
        scorer = gsm8k_scorer if domain == "gsm8k" else squad2_scorer

        for seed in design["sample_size"]["seed_values"][: args.seeds]:
            agents = build_agent_pool(n_agents, structural, corr_level,
                                       domain_context=True if domain == "squad2" else None)
            quorum = Quorum(agents)

            if args.backend == "mock":
                rho = RHO_BY_LEVEL[corr_level]
                backend = CorrelatedMockBackend(p=0.10, rho=rho,
                                                 cluster_key=lambda a: a.provider)
                use_scorer = mock_scorer
                # mock backend's `gold` short-circuit compares raw_answer==task.gold;
                # that still works for squad2's tuple gold and gsm8k's string gold.
            else:
                backend = make_backend(args)
                use_scorer = scorer

            for t in tasks:
                try:
                    outcome = quorum.run(t, backend, seed=seed, scorer=use_scorer)
                except MissingCredentialsError as e:
                    print(f"\nBLOCKED: {e}")
                    sys.exit(2)

                err_flags = [not c for c in outcome.correctness]
                raw_rows.append({
                    "domain": domain, "structural": structural, "correlation_level": corr_level,
                    "n_agents": n_agents, "seed": seed, "task_id": t.task_id,
                    "structurally_safe": outcome.structurally_safe,
                    "reached_consensus": outcome.reached_consensus,
                    "is_false_consensus": outcome.is_false_consensus,
                    "majority_is_correct": outcome.majority_is_correct,
                    "n_agent_errors": sum(err_flags),
                    "total_latency_s": outcome.total_latency_s,
                    "n_agent_calls": len(outcome.responses),
                })

    out_dir = REPO_ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    raw_path = out_dir / "raw_results.csv"
    with open(raw_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()) + ["DATA_LABEL"])
        writer.writeheader()
        for row in raw_rows:
            row["DATA_LABEL"] = label
            writer.writerow(row)

    # summary by cell
    import pandas as pd
    df = pd.DataFrame(raw_rows)
    summary = df.groupby(["domain", "structural", "correlation_level", "n_agents"]).agg(
        n_tasks=("task_id", "count"),
        false_consensus_rate=("is_false_consensus", "mean"),
        agreement_rate=("reached_consensus", "mean"),
        structurally_safe_rate=("structurally_safe", "mean"),
    ).reset_index()
    summary["DATA_LABEL"] = label
    summary_path = out_dir / "summary_results.csv"
    summary.to_csv(summary_path, index=False)

    print(f"\nWrote {len(raw_rows)} raw rows to {raw_path}")
    print(f"Wrote {len(summary)} summary rows to {summary_path}")
    print(f"\nAll output files are labeled: {label}")
    print("\nSummary (false-consensus rate by cell):")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
