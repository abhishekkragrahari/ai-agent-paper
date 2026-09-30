"""
Core data model: tasks, agents, responses, and the Backend interface that
both the mock (synthetic validation) and real (API-backed) backends implement.

This module defines the contract only. See mock_backend.py for the
synthetic, clearly-labeled validation backend and real_backends.py for
API-backed implementations that require credentials not present in this
environment (see FINAL_RESEARCH_STATUS.md).
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TaskItem:
    """A single evaluation task with objective ground truth.

    domain: e.g. "gsm8k" or "squad2" — must match a scorer registered in
        src/metrics/.
    task_id: stable identifier (e.g. dataset row index / question id).
    prompt: the text given to the agent.
    gold: the ground-truth answer/label, in whatever form that domain's
        scorer expects (e.g. a string numeral for GSM8K, a set of
        acceptable answer strings for SQuAD 2.0, or the empty set / a
        sentinel for an unanswerable SQuAD 2.0 question).
    context: optional shared material (e.g. a SQuAD passage) — used by the
        structural/fault_basis module to decide whether two agents share
        an evidence-root dependency.
    """
    domain: str
    task_id: str
    prompt: str
    gold: object
    context: Optional[str] = None


@dataclass(frozen=True)
class Agent:
    """An agent participating in a quorum.

    agent_id: unique id within a quorum.
    provider: coarse provider/model-family label (e.g. "anthropic",
        "openai", "mock-lineage-A"). This is the label-based proxy that
        CORRELATION_MEASUREMENT.md explicitly argues should NOT be trusted
        as independence on its own — it is retained here only as a
        factor to compare against the measured phi-coefficient in the
        label-vs-behavioral ablation (Phase 11.4).
    model_name: specific model identifier.
    structural_dependencies: the set of modeled Epistemic-Fault-Basis
        roots (DAQC's term, arXiv:2609.02925) this agent's runtime touches
        for a given task — e.g. {"tool:shared_retriever"} or
        {"context:squad_passage_v1"}. Two agents that share any element of
        this set are NOT kappa_E-safe with respect to each other. This is
        a reimplementation from the published description of DAQC's
        admission criterion, not DAQC's own source code (which is not
        available in this environment).
    """
    agent_id: str
    provider: str
    model_name: str
    structural_dependencies: frozenset = field(default_factory=frozenset)


@dataclass(frozen=True)
class AgentResponse:
    agent_id: str
    task_id: str
    seed: int
    answer: object
    is_correct: Optional[bool]  # filled in by the domain scorer, not the backend
    raw_text: str = ""
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class Backend(abc.ABC):
    """Interface every backend (mock or real) must implement."""

    name: str = "unnamed-backend"

    @abc.abstractmethod
    def generate(self, agent: Agent, task: TaskItem, seed: int) -> AgentResponse:
        """Produce one response from `agent` to `task` under `seed`."""
        raise NotImplementedError

    def is_real(self) -> bool:
        """True iff this backend calls a real external LLM API.

        Used by experiment drivers to refuse to label output as research
        results when this is False (see experiments/run_factorial_experiment.py).
        """
        return False
