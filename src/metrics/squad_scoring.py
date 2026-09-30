"""
SQuAD 2.0 scorer using the dataset's own official normalization/exact-match
convention (Rajpurkar et al. 2016/2018), extended for the is_impossible
("no answer") case introduced in v2.0.

TaskItem.gold for a SQuAD 2.0 item is expected to be a tuple:
    (tuple_of_acceptable_answer_strings, is_impossible: bool)
For an answerable question, tuple_of_acceptable_answer_strings holds the
(possibly several) annotator-provided gold answer strings (exact match
against ANY of them counts as correct, per the official SQuAD convention).
For an unanswerable question, tuple_of_acceptable_answer_strings is empty
and is_impossible is True; the model is correct iff it abstains.
"""
from __future__ import annotations

import re
import string
from typing import Tuple

from src.agents.base import TaskItem

_ABSTAIN_MARKERS = {"", "unanswerable", "no answer", "cannot be determined", "not answerable"}


def normalize_answer(s: str) -> str:
    """Official SQuAD normalization: lowercase, remove punctuation, articles,
    and extra whitespace."""
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def is_abstention(text: str) -> bool:
    return normalize_answer(text) in _ABSTAIN_MARKERS


def squad2_scorer(raw_answer: object, task: TaskItem) -> Tuple[str, bool]:
    """scorer(raw_answer, task) -> (canonical_answer, is_correct)."""
    gold_answers, is_impossible = task.gold

    # mock backend short-circuit: it supplies task.gold verbatim when correct
    if raw_answer == task.gold:
        canonical = "UNANSWERABLE" if is_impossible else normalize_answer(gold_answers[0])
        return canonical, True

    text = str(raw_answer)
    if is_impossible:
        correct = is_abstention(text)
        canonical = "UNANSWERABLE" if correct else normalize_answer(text)
        return canonical, correct

    if is_abstention(text):
        return "UNANSWERABLE", False  # wrongly abstained on an answerable question

    norm_pred = normalize_answer(text)
    norm_golds = {normalize_answer(g) for g in gold_answers}
    correct = norm_pred in norm_golds
    return norm_pred, correct
