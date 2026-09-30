"""
Real GSM8K scorer: extracts the canonical final numeral from a model answer
and from the dataset's own `#### <number>` reference format, and compares
by exact numeric match after normalization. This is the dataset's own
standard scoring convention (Cobbe et al. 2021), not invented here.
"""
from __future__ import annotations

import re
from typing import Tuple

from src.agents.base import TaskItem

_NUM_RE = re.compile(r"-?\$?[\d,]+(?:\.\d+)?")


def _normalize_number(s: str) -> str:
    s = s.strip().replace(",", "").replace("$", "")
    if s.endswith("."):
        s = s[:-1]
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return str(f)
    except ValueError:
        return s


def extract_gsm8k_gold(reference_solution: str) -> str:
    """Extract the gold numeral from GSM8K's '#### <number>' format."""
    if "####" not in reference_solution:
        raise ValueError(f"No '####' marker found in reference solution: {reference_solution!r}")
    tail = reference_solution.split("####")[-1].strip()
    return _normalize_number(tail)


def extract_last_number(text: str) -> str:
    """Extract the last number-like substring from free text (a standard,
    simple final-answer extraction heuristic for GSM8K-style outputs)."""
    matches = _NUM_RE.findall(text)
    if not matches:
        return ""
    return _normalize_number(matches[-1])


def gsm8k_scorer(raw_answer: object, task: TaskItem) -> Tuple[str, bool]:
    """scorer(raw_answer, task) -> (canonical_answer, is_correct)."""
    if isinstance(raw_answer, str) and raw_answer == task.gold:
        # mock backend already supplies the canonical gold string directly
        # when correct -- short-circuit to avoid double-parsing
        canonical = _normalize_number(str(task.gold))
        return canonical, True
    text = str(raw_answer)
    extracted = extract_last_number(text)
    gold_norm = _normalize_number(str(task.gold))
    return extracted, (extracted == gold_norm and extracted != "")
