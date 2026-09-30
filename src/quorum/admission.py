"""
Quorum aggregation: run n agents on a task, apply a structural (kappa_E)
admission check, aggregate by majority vote over a domain-specific
*canonical* answer key (not raw text — see `scorer` argument), and report
whether the quorum reached a false consensus (a strict majority certifying
the same wrong canonical answer).
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from src.agents.base import Agent, AgentResponse, Backend, TaskItem
from src.structural.fault_basis import kappa_E_safe

# scorer(raw_answer, task) -> (canonical_answer: hashable, is_correct: bool)
Scorer = Callable[[object, TaskItem], Tuple[object, bool]]


def majority_threshold(n: int) -> int:
    """Strict majority: smallest q with q > n/2, i.e. q = floor(n/2) + 1."""
    return n // 2 + 1


@dataclass
class QuorumOutcome:
    task_id: str
    n: int
    structurally_safe: bool
    structural_violations: set
    responses: List[AgentResponse]
    canonical_answers: List[object]
    correctness: List[bool]
    majority_answer: Optional[object]
    majority_count: int
    reached_consensus: bool          # strict majority agreed on ONE canonical answer
    majority_is_correct: Optional[bool]
    is_false_consensus: bool         # reached_consensus AND majority answer is wrong
    total_latency_s: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0


class Quorum:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.n = len(agents)
        self.q = majority_threshold(self.n)

    def run(self, task: TaskItem, backend: Backend, seed: int, scorer: Scorer) -> QuorumOutcome:
        safe, violations = kappa_E_safe(self.agents)

        responses: List[AgentResponse] = []
        canon: List[object] = []
        correct: List[bool] = []
        for agent in self.agents:
            resp = backend.generate(agent, task, seed)
            canonical, is_correct = scorer(resp.answer, task)
            responses.append(resp)
            canon.append(canonical)
            correct.append(is_correct)

        counts = Counter(canon)
        majority_answer, majority_count = counts.most_common(1)[0]
        reached_consensus = majority_count >= self.q

        majority_is_correct = None
        is_false_consensus = False
        if reached_consensus:
            # invariant check: all responses sharing the majority canonical
            # answer should agree on correctness; warn (don't silently
            # trust) if not, since this signals a scorer bug.
            idxs = [i for i, c in enumerate(canon) if c == majority_answer]
            maj_correct_flags = {correct[i] for i in idxs}
            if len(maj_correct_flags) > 1:
                raise AssertionError(
                    f"Scorer inconsistency on task {task.task_id}: responses "
                    f"sharing canonical answer {majority_answer!r} disagree on "
                    f"correctness ({maj_correct_flags}). Fix the scorer before "
                    f"trusting downstream metrics."
                )
            majority_is_correct = maj_correct_flags.pop()
            is_false_consensus = not majority_is_correct

        return QuorumOutcome(
            task_id=task.task_id,
            n=self.n,
            structurally_safe=safe,
            structural_violations=violations,
            responses=responses,
            canonical_answers=canon,
            correctness=correct,
            majority_answer=majority_answer if reached_consensus else None,
            majority_count=majority_count,
            reached_consensus=reached_consensus,
            majority_is_correct=majority_is_correct,
            is_false_consensus=is_false_consensus,
            total_latency_s=sum(r.latency_s for r in responses),
            total_prompt_tokens=sum(r.prompt_tokens for r in responses),
            total_completion_tokens=sum(r.completion_tokens for r in responses),
        )
