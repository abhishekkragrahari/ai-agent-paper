# Structural vs. Parametric Epistemic Independence in LLM-Agent Quorums

**Draft v2 — theory and experimental design complete; results pending execution (see §9 disclosure)**

## Abstract

Recent work has formalized the failure mode in which a protocol-compliant, non-equivocating LLM-agent validator nonetheless endorses a semantically invalid decision — the *epistemic fault* (He & Yu, 2026) — and has shown that such faults correlate across agents that share runtime dependencies, a phenomenon formalized through Epistemic Fault Domains and a Structural Epistemic Cut (κ_E) enforced by a Dependency-Aware Quorum Controller, DAQC (He & Yu, 2026). Independently, empirical work in the machine-learning literature has shown that LLM output errors correlate across agents with *no shared runtime dependency at all* — different providers, different architectures, and even on adversarially decorrelated tasks — attributable to shared training corpora and optimization objectives rather than shared infrastructure (Kim et al., 2025; anonymous, 2026). These two lines of work have not, to our knowledge, been connected: it is not known whether achieving structural epistemic independence (κ_E-safety) is sufficient to bound false-consensus probability in an LLM-agent quorum, or whether a second, orthogonal correlation channel — which we term *parametric* correlation, arising from shared training lineage — persists regardless. We formalize this distinction, derive a conditional proposition characterizing when κ_E-safety is necessary but not sufficient, and specify a pre-registered factorial experimental design to test it. This paper reports the formal model and experimental design; execution and results are left for a follow-up report, consistent with the position that a null result (κ_E-safety proves practically sufficient) is as publishable an outcome as a positive one.

## 1. Introduction

[Problem, motivation, gap, RQ, contributions — drawing on Parts A–C of the companion gap analysis. Full prose to be expanded from the gap-analysis document before submission; retained here as an outline to avoid duplicating text across files at draft stage.]

- Problem: LLM-agent quorums are increasingly used as a reliability mechanism (voting, certification, admission control) for autonomous agent decisions.
- Gap: the two known correlation channels for agent error — structural (runtime-dependency-mediated) and parametric (training-lineage-mediated) — have been studied separately and have never been jointly tested against a single admission-control mechanism.
- RQ1 (primary): see gap analysis §F.
- Contributions: (1) a conditional formal proposition scoping what κ_E-safety does and does not bound; (2) a factorial experimental design and harness specification for testing it; (3) [pending execution] empirical results.

## 2. Background: Classical and Epistemic Fault Tolerance

2.1 Classical Byzantine agreement: agreement, validity, termination (safety/liveness), stated per a pinned primary source [citation to be finalized — Part H].

2.2 Epistemic Byzantine Fault Tolerance (He & Yu, 2026): epistemic fault defined as protocol-compliant, non-equivocating endorsement of a semantically invalid transition; EBFT bounds e_δ (coherent invalid endorsement rate) and u_ε (unusable support rate).

2.3 Epistemic Fault Domains and DAQC (He & Yu, 2026): a modeled Epistemic Fault Basis of exogenous fault roots (corrupted telemetry, poisoned tool output, compromised document store); Structural Epistemic Cut κ_E as the minimum number of fault roots whose activation compromises a decisive coalition; DAQC enforces κ_E-safety at admission time.

## 3. Problem Definition

Restated from the gap analysis, Part C: does κ_E-safety bound false-consensus probability, or only its structurally-mediated component?

## 4. System and Fault Model

As specified in the gap analysis, Part D: agents with declared training lineage L(·) and runtime dependency set R(·); structural independence (κ_E, imported unchanged from DAQC); parametric independence (operational proxy: distinct model family/provider, stated explicitly as a coarse proxy per Reviewer #2's objection, Part L).

## 5. Proposed Measurement Method

As specified in the gap analysis, Part E: dual-axis fault-injection harness layered on a reimplemented κ_E-style admission check, not a new production protocol.

## 6. Theoretical Analysis

**Proposition 1 (conditional).** [Full statement as in gap analysis Part D.] Presented explicitly as conditional on a channel-distinguishability assumption, not as a proven theorem, per Reviewer #1's objection (Part K).

**Discussion of validity/agreement/semantic-truth distinction**, per gap analysis Part D.3, replacing the withdrawn "BFT assumes semantic independence" claim.

## 7. Experimental Methodology

Full factorial design, metrics, baselines, and datasets as specified in gap analysis Parts F and G. **Required pre-registration steps not yet completed:** power analysis; final dataset selection; harness validation against the random-string replication check (Reviewer #2, Part L).

## 8. Results

> **NOT YET AVAILABLE.** No experiment has been executed. This section will report, per cell of the design in §7:
>
> | Structural | Parametric | Quorum size | Domain | Semantic accuracy (95% CI) | Agreement rate | False-consensus rate (95% CI) | FP / FN of κ_E check |
> |---|---|---|---|---|---|---|---|
> | safe | same-lineage | n=3 | domain A | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` |
> | safe | cross-lineage | n=3 | domain A | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` |
> | unsafe | same-lineage | n=3 | domain A | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` |
> | unsafe | cross-lineage | n=3 | domain A | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` | `PLACEHOLDER` |
> | *(remaining cells: n=5 × 2 domains, same structure)* | | | | | | | |
>
> Procedure for filling this table: execute the harness per §7; compute metrics per task per cell with bootstrap CIs over tasks and ≥3 seeds; run the significance test specified in the (not-yet-written) pre-registration document comparing same- vs. cross-lineage false-consensus rate at fixed structural safety (RQ1); report effect size, not only p-value.

## 9. Ablation and Sensitivity Analysis

> **NOT YET AVAILABLE**, pending §8. Planned ablations: (a) coarse vs. fine-grained parametric-independence proxy (Reviewer #2); (b) quorum size sweep beyond the two points in the minimum design; (c) domain-specificity of the effect (RQ4).

## 10. Discussion

To be written once §8 exists. Must explicitly address both possible outcomes: if H1 holds, implications for DAQC's practical sufficiency; if H1 is rejected, this is reported as a valid bound on when structural admission control is practically adequate, not suppressed (Reviewer #3, Part M).

## 11. Threats to Validity

- Operational proxy for parametric independence is coarse (model family/provider), not a validated measure of training-data overlap.
- Ground-truth procedure per dataset not yet finalized (Reviewer #3).
- Reimplementation of κ_E admission logic from published description, not original code — fidelity risk pending author confirmation or code release.
- LLM API non-determinism limits exact reproducibility; mitigated by multi-seed reporting, not eliminated.

## 12. Limitations

This manuscript, in its current state, reports a formal model and experimental design, not results. The central hypothesis (H1) is untested. Proposition 1 is conditional on an unproven factorization assumption. The gap claim (Part C) is conditional on a full-text check of arXiv:2609.02925 and arXiv:2606.07316 not yet performed in this session (flagged as blocking in the companion gap-analysis document, Part P).

## 13. Conclusion

[To be finalized once the blocking pre-submission items in Part P are resolved and §8 is populated.]

## References

1. He, J., Yu, D. "The Honest Quorum Problem: Epistemic Byzantine Fault Tolerance for Agentic Infrastructure." arXiv:2607.16109, 2026.
2. He, J., Yu, D. "The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums." arXiv:2609.02925, 2026.
3. Xu, H., Zhang, L., Ounis, I., Wang, X. "Hierarchical Certified Semantic Commitment for Byzantine-Resilient LLM-Agent Collaboration." arXiv:2606.07316, 2026.
4. Rodrigues, C. "Hallucination as Context Drift: Synchronization Protocols for Multi-Agent LLM Systems." arXiv:2606.21666, 2026.
5. Kim, et al. "Correlated Errors in Large Language Models." ICML 2025 / arXiv:2506.07962, 2025.
6. "Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness." arXiv:2603.06612, 2026.
7. Byzantine agreement/validity/termination — primary citation to be pinned (candidate: Cachin, C., Guerraoui, R., Rodrigues, L. *Introduction to Reliable and Secure Distributed Programming*, 2nd ed., Springer, 2011 — verify exact edition/chapter before citing).

*Author/title details for references 1–6 were obtained from arXiv listings and search-engine-surfaced abstracts, cross-checked for title/author/ID consistency. Full-text verification of the specific claims attributed to references 2 and 3 in §3–§6 is a blocking pre-submission action (see companion gap-analysis document, Part P).*
