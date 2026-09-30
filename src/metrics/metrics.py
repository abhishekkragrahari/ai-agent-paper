"""
Quorum-level and pipeline-level metrics computed over a list of QuorumOutcome
objects (src/quorum/admission.py). Pure functions over already-produced
outcomes -- no LLM calls here.
"""
from __future__ import annotations

from typing import List

import numpy as np

from src.correlation.measures import bootstrap_ci
from src.quorum.admission import QuorumOutcome


def false_consensus_rate(outcomes: List[QuorumOutcome]) -> dict:
    vals = np.array([o.is_false_consensus for o in outcomes], dtype=float)
    point, lo, hi = bootstrap_ci(vals, statistic=np.mean)
    return {"rate": point, "ci_low": lo, "ci_high": hi, "n": len(outcomes)}


def semantic_accuracy(outcomes: List[QuorumOutcome]) -> dict:
    """Fraction of *individual agent responses* (not quorum decisions) that
    were correct -- the base rate the theory's `p` parameter refers to."""
    all_correct = [c for o in outcomes for c in o.correctness]
    vals = np.array(all_correct, dtype=float)
    point, lo, hi = bootstrap_ci(vals, statistic=np.mean)
    return {"rate": point, "ci_low": lo, "ci_high": hi, "n": len(all_correct)}


def agreement_rate(outcomes: List[QuorumOutcome]) -> dict:
    vals = np.array([o.reached_consensus for o in outcomes], dtype=float)
    point, lo, hi = bootstrap_ci(vals, statistic=np.mean)
    return {"rate": point, "ci_low": lo, "ci_high": hi, "n": len(outcomes)}


def admission_check_confusion(outcomes: List[QuorumOutcome], true_safe_label: List[bool]) -> dict:
    """FP/FN of the kappa_E structural admission check against a KNOWN
    ground-truth safety label (only computable in a validation setting
    where the true structural configuration is known by construction --
    e.g. the harness-sanity-check experiment, which plants it)."""
    pred_safe = np.array([o.structurally_safe for o in outcomes])
    true_safe = np.array(true_safe_label)
    tp = int(np.sum(pred_safe & true_safe))
    tn = int(np.sum(~pred_safe & ~true_safe))
    fp = int(np.sum(pred_safe & ~true_safe))
    fn = int(np.sum(~pred_safe & true_safe))
    total = len(outcomes)
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn, "n": total,
        "false_positive_rate": fp / (fp + tn) if (fp + tn) > 0 else float("nan"),
        "false_negative_rate": fn / (fn + tp) if (fn + tp) > 0 else float("nan"),
    }


def cost_summary(outcomes: List[QuorumOutcome]) -> dict:
    total_latency = sum(o.total_latency_s for o in outcomes)
    total_prompt = sum(o.total_prompt_tokens for o in outcomes)
    total_completion = sum(o.total_completion_tokens for o in outcomes)
    n_calls = sum(len(o.responses) for o in outcomes)
    return {
        "total_latency_s": total_latency,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "n_agent_calls": n_calls,
        "mean_latency_per_call_s": total_latency / n_calls if n_calls else float("nan"),
    }
