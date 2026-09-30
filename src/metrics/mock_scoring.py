"""Pass-through scorer for CorrelatedMockBackend: the mock backend already
sets ground-truth correctness directly (it controls the planted parameters
by construction), so this scorer trusts the AgentResponse.is_correct field
and uses the answer itself as the canonical grouping key. Used only in
harness-validation experiments, never for reported results (see
FINAL_RESEARCH_STATUS.md).
"""
from __future__ import annotations

from typing import Tuple

from src.agents.base import TaskItem


def mock_scorer(raw_answer: object, task: TaskItem) -> Tuple[object, bool]:
    is_correct = (raw_answer == task.gold)
    return raw_answer, is_correct
