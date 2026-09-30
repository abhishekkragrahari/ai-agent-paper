"""
Reimplementation, from the published description, of the admission
criterion He & Yu's Dependency-Aware Quorum Controller (DAQC) applies at
the evidence-root / structural basis (arXiv:2609.02925). This is NOT a copy
of DAQC's source code (not available to this environment — see
FINAL_NOVELTY_GATE.md §0) and is deliberately restricted to the basis type
their own reported benchmark exercises: shared runtime evidence roots
(tools, telemetry, document/context stores) — NOT the provider/training-
lineage basis, which this project's whole contribution is about testing
separately (see src/correlation/measures.py and CORRELATION_MEASUREMENT.md).

Definitions used here (consistent with FINAL_NOVELTY_GATE.md §1):
  - An Epistemic Fault Basis element ("fault root") is any single named
    runtime dependency an agent's output could be contaminated through:
    a shared tool, a shared document store, a shared telemetry feed, a
    shared context string.
  - A quorum (or any decisive coalition within it) is kappa_E-safe (at the
    structural/evidence-root basis) iff no two of its agents share a fault
    root, i.e. their structural_dependencies sets are pairwise disjoint.
    This is the minimum-cut / "no shared root reaches a decisive
    coalition" criterion at its simplest (cut size 1 suffices to violate
    safety), matching the described behavior of kappa_E for a basis where
    each task supplies evidence packages "rooted in distinct modeled
    evidence roots" (as DAQC's own benchmark is described).
"""
from __future__ import annotations

from itertools import combinations
from typing import FrozenSet, Iterable, Set, Tuple

from src.agents.base import Agent


def shared_fault_roots(a: Agent, b: Agent) -> FrozenSet[str]:
    """The set of structural fault-basis roots agents a and b have in common."""
    return frozenset(a.structural_dependencies) & frozenset(b.structural_dependencies)


def kappa_E_safe(quorum: Iterable[Agent]) -> Tuple[bool, Set[Tuple[str, str, str]]]:
    """Is this quorum kappa_E-safe at the evidence-root/structural basis?

    Returns (is_safe, violations) where violations is a set of
    (agent_id_1, agent_id_2, shared_root) triples for every pair that
    shares at least one modeled fault root. is_safe is True iff
    violations is empty (i.e. every pairwise intersection of structural
    dependency sets is empty — the standard, conservative "any shared
    root among any pair breaks safety" reading of a Structural Epistemic
    Cut of size 1, appropriate for the minimum-viable reimplementation
    used here; a graph-theoretic minimum-cut generalization for larger
    kappa_E values is noted as a possible refinement in
    gap_analysis_and_manuscript_v2.md's limitations but is not needed for
    this project's 2-level structural factor, which only needs a binary
    safe/unsafe distinction).
    """
    agents = list(quorum)
    violations = set()
    for a, b in combinations(agents, 2):
        shared = shared_fault_roots(a, b)
        for root in shared:
            violations.add((a.agent_id, b.agent_id, root))
    return (len(violations) == 0, violations)
