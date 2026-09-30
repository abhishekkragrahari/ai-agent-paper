"""
CorrelatedMockBackend: a deterministic, seeded synthetic backend implementing
EXACTLY the Beta-mixture common-cause model verified in FORMAL_RESULTS.md and
research/verify_formal_results.py.

================================================================================
THIS BACKEND PRODUCES NO RESEARCH RESULTS. It is software-validation
infrastructure only: a generator with a KNOWN, PLANTED ground-truth
correlation and error rate, used to check that the rest of the pipeline
(correlation estimators, quorum aggregation, metrics, statistics) correctly
recovers known parameters. Any CSV or figure produced by running this
backend must carry the "SYNTHETIC VALIDATION DATA" label and must never be
presented as a finding about real LLM-agent behavior. See
FINAL_RESEARCH_STATUS.md.
================================================================================

Model (matches FORMAL_RESULTS.md Section 2 exactly):
  - For each task, and each "correlation cluster" of agents (agents that
    share an unbroken latent-cause group -- see `cluster_key`), draw
    Theta ~ Beta(alpha, beta) once.
  - Each agent in that cluster is independently wrong with probability
    Theta (i.e. is_correct = Bernoulli(1-Theta)), conditional on Theta.
  - alpha, beta are derived from a per-cluster (p, rho) pair via
    alpha = p(1-rho)/rho, beta = (1-p)(1-rho)/rho (rho > 0), or the
    independent Binomial(n,p) limit at rho = 0.

Clustering: which agents share a Theta draw is controlled by
`cluster_key(agent)`, defaulting to (provider,) i.e. agents from the same
mock "provider" label share a latent cause -- this lets the harness
validation experiment plant a KNOWN rho for a KNOWN group of agents and
then check that the phi-coefficient estimator recovers it.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable, Dict, Tuple

import numpy as np

from .base import Agent, AgentResponse, Backend, TaskItem


def _stable_seed(*parts) -> int:
    """Deterministic 32-bit seed from arbitrary string parts (reproducibility)."""
    h = hashlib.sha256("||".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(h[:4], "big")


@dataclass
class CorrelatedMockBackend(Backend):
    """Synthetic backend with a planted (p, rho) correlated-error structure.

    p: per-agent marginal error rate (e.g. 0.10).
    rho: intraclass correlation among agents in the same cluster (0 = independent).
    cluster_key: function mapping an Agent to a hashable cluster id; agents
        with the same cluster id share one Theta draw per task. Defaults to
        grouping by `provider`, letting the validation experiment plant a
        rho specifically for e.g. "same-provider" agent groups.
    """
    p: float = 0.10
    rho: float = 0.0
    cluster_key: Callable[[Agent], object] = field(default=lambda a: a.provider)
    name: str = "mock-beta-mixture"

    def is_real(self) -> bool:
        return False

    def _theta_for(self, task: TaskItem, cluster_id, seed: int) -> float:
        rng = np.random.default_rng(_stable_seed("theta", task.task_id, cluster_id, seed))
        if self.rho <= 1e-9:
            return self.p  # independent limit: Theta degenerates to p (see generate())
        s = (1 - self.rho) / self.rho
        alpha, beta = self.p * s, (1 - self.p) * s
        return float(rng.beta(alpha, beta))

    def generate(self, agent: Agent, task: TaskItem, seed: int) -> AgentResponse:
        cluster_id = self.cluster_key(agent)
        theta = self._theta_for(task, cluster_id, seed)
        rng = np.random.default_rng(_stable_seed("agent", task.task_id, agent.agent_id, seed))
        if self.rho <= 1e-9:
            is_wrong = bool(rng.random() < self.p)
        else:
            is_wrong = bool(rng.random() < theta)
        answer = f"WRONG_SYNTHETIC_ANSWER::{task.task_id}" if is_wrong else task.gold
        return AgentResponse(
            agent_id=agent.agent_id,
            task_id=task.task_id,
            seed=seed,
            answer=answer,
            is_correct=not is_wrong,
            raw_text=f"[SYNTHETIC MOCK OUTPUT — NOT A REAL LLM RESPONSE] theta={theta:.4f}",
            latency_s=0.0,
            prompt_tokens=0,
            completion_tokens=0,
        )
