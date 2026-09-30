# Structural vs. Provider-Basis Epistemic Independence in LLM-Agent Quorums: A Formal Model, Measurement Framework, and Pre-Registered Study

**Status: theory, methodology, and pre-registered experimental design are complete and verified. The empirical results section is explicitly pending real execution — see the boxed notice in §9. This is disclosed on the first page, not buried, per this project's own non-negotiable rule against presenting synthetic or planned data as findings.**

## Abstract

Recent work formalizes a failure mode in LLM-agent quorums in which a protocol-compliant, non-equivocating validator nonetheless endorses a semantically invalid decision — an *epistemic fault* (He & Yu, 2026a) — and shows such faults correlate when agents share a modeled runtime dependency, formalized through an Epistemic Fault Domain and a Structural Epistemic Cut (κ_E) enforced by a Dependency-Aware Quorum Controller, DAQC (He & Yu, 2026b). DAQC's own framework names, but its reported benchmark does not appear to operationalize, a second basis type — the *provider basis*, covering shared model weights and training lineage — and its own text flags the real-model behavioral question for this basis as "left to endpoint execution." Independently, Kim et al. (2025) and a 2026 study on crowd-wisdom aggregation (arXiv:2603.06612) show LLM errors correlate across different providers and architectures via shared training data, including in conditions with zero shared runtime dependency — but neither connects this to a quorum admission-control mechanism. This paper (1) formalizes the distinction between structural and provider-basis epistemic independence within DAQC's own terms, (2) proves a model-conditional bound (Theorem 1) relating pairwise error correlation, quorum size, and false-consensus probability, verified both symbolically and numerically, (3) develops a measurement framework for observed semantic-error correlation that explicitly replaces a coarse provider-label proxy, and (4) specifies and partially executes (as a validated software pipeline, not yet real data) a pre-registered factorial study testing whether κ_E-safety alone is sufficient to bound false-consensus risk in practice. No claim in this paper about real LLM-agent behavior is asserted without either a proof or real experimental data; where neither exists, the paper says so explicitly rather than filling the gap with synthetic numbers.

## 1. Introduction

### 1.1 Problem

Distributed systems built from LLM agents increasingly rely on quorum-style aggregation (voting, certified commitment) as a reliability mechanism. Two recent strands of work show this mechanism can fail in ways classical Byzantine fault tolerance does not anticipate: agents can be fully protocol-compliant while jointly certifying a semantically wrong decision (He & Yu, 2026a, 2026b), and LLM errors are empirically correlated across models in ways a naive independence assumption misses (Kim et al., 2025; arXiv:2603.06612).

### 1.2 Gap

He & Yu's own framework (2026b) explicitly names a "provider basis" — correlation through shared model weights/training lineage — as a valid instantiation of their general Epistemic Fault Basis, alongside the evidence-root/runtime-dependency basis their reported 120-task benchmark actually tests. Their text states plainly that whether real models propagate a modeled fault into unsafe approvals "is an empirical question left to endpoint execution." As verified in `FINAL_NOVELTY_GATE.md` (§1–§2), no paper among the six closest works we identified reports an experiment that (a) varies the provider basis with real, differently-trained agents inside a quorum/admission-control framing, or (b) tests whether measured, continuous pairwise error correlation predicts false consensus better than a coarse provider-label proxy.

### 1.3 Precise research question

**Does enforcing structural (evidence-root) κ_E-safety — the basis DAQC's own reported benchmark exercises — leave a quorum exposed to false consensus through the provider/training-lineage basis that DAQC's theory names but does not, as far as we can verify, test with real agents?**

This is explicitly framed as closing a question DAQC's own paper states is open, not as identifying a gap in their theory (an earlier draft of this project's internal documents made that overclaim; it was corrected — see `gap_analysis_and_manuscript_v2.md` Part A.3, preserved rather than silently deleted).

### 1.4 Contributions

1. A formal model (Theorem 1, §7) proving that quorum-level false-consensus probability is bounded above by a quantity strictly increasing in pairwise error correlation ρ, under a standard (Skellam, 1948) common-cause correlated-Bernoulli model — verified both symbolically and numerically, not merely asserted.
2. A measurement framework (§6) that replaces "same provider ⇒ correlated" with a measured, justified correlation estimator (the phi coefficient, chosen and defended against four alternatives).
3. A fully implemented, end-to-end-validated experimental pipeline (§8) — real dataset loaders (GSM8K, SQuAD 2.0, both genuinely downloaded), a reimplemented κ_E structural-safety check, the correlation measurement framework, and a pre-registered statistical analysis plan — with its correctness demonstrated via positive/negative controls on synthetic data with known ground truth (§8.4), not yet applied to real LLM agents.
4. A candid accounting (§9, and the standalone `FINAL_RESEARCH_STATUS.md`) of exactly what is proved, what is measured on synthetic data, and what remains an open empirical question.

## 2. Background: Classical and Epistemic Fault Tolerance

Classical Byzantine agreement (Lamport, Shostak & Pease, 1982) guarantees, for n≥3f+1 with at most f Byzantine nodes: **agreement** (correct nodes output the same value), **validity** (the agreed value was proposed by some party), and **termination**. None of these three is a guarantee that the agreed value corresponds to external ground truth — this was never classical BFT's job, and we do not claim otherwise anywhere in this paper. The correct, literature-consistent formulation, which we adopt throughout in place of an earlier and less careful phrasing in this project's own history, is: *classical BFT provides agreement under its stated fault assumptions, but agreement alone is insufficient to establish application-level semantic validity when validity judgments are stochastic and correlated* — a formulation we checked against the properties above and against He & Yu's (2026a) own explicit statement that "agreement alone does not guarantee semantic validity."

EBFT (He & Yu, 2026a) extends this with two confidence-indexed bounds separating semantic-safety risk (e_δ) from liveness degradation (u_ε). DAQC (He & Yu, 2026b) extends this further with a **Structural Epistemic Cut** κ_E, computed relative to an explicit, modeled Epistemic Fault Basis, and an admission controller enforcing cuts against that basis at runtime.

## 3. Related Work and Contribution Defense

| Prior work | What it solves | What it does not (verified) solve | How this paper differs |
|---|---|---|---|
| EBFT (He & Yu, 2026a) | Names epistemic faults; bounds e_δ, u_ε | Does not decompose correlation by source | We decompose by basis type (structural vs. provider) and bound false-consensus probability as an explicit function of measured ρ, not just an abstract budget |
| DAQC / EFD (He & Yu, 2026b) | Formalizes structural/evidence-root correlation; κ_E admission control; real benchmark (evidence-root basis) | Reported benchmark does not, as far as verified, operationalize the provider basis their own theory names; flags this as open | We build and validate (on synthetic data; real execution pending) a pipeline that specifically tests the provider-basis case, crediting DAQC's own naming of it rather than claiming to discover it |
| H-CSC (Xu et al., 2026) | Embedding-certified typed commit protocol; real evaluation on MVR-50 | No structural-vs-provider factorial framing; baselines are majority/confidence-weighted voting, not a basis-type manipulation | Different question (a measurement/diagnosis question, not a new commit protocol); complementary, not competing |
| SSVP / Context Drift (Rodrigues, 2026) | Treats hallucination as state staleness; real two-domain evaluation | Not a quorum/admission-control framing; does not address κ_E or correlated *error*, specifically state *divergence* | Different mechanism (correlated error vs. state staleness); both could co-occur in a real system, noted as future integration work |
| Correlated Errors in LLMs (Kim et al., 2025) | Real, large-scale (350+ models) evidence of cross-provider correlated error | No quorum/consensus framing at all | We are, as far as verified, the first to connect this specific empirical finding to a κ_E-style admission-control mechanism |
| Consensus is Not Verification (arXiv:2603.06612) | Real evidence that polling amplifies correlated error, even OOD | No quorum/admission-control framing; no continuous correlation measurement compared against a label proxy | We add the measurement layer (§6) and the basis-type framing (§4) this work does not attempt |

**Why this is not "just another multi-agent voting paper":** the contribution is not a new voting or commitment rule (that is H-CSC's and DAQC's territory, and we do not compete with them on that ground) — it is a measurement and diagnosis contribution asking whether an *existing*, *named*, *specific* admission-control guarantee (κ_E-safety, as DAQC's own reported benchmark tests it) is sufficient once a second basis type their own theory names is accounted for.

## 4. Problem Definition

Given a quorum of n LLM agents answering a task t with ground truth g(t), and given that the quorum is κ_E-safe relative to the evidence-root/structural Epistemic Fault Basis (DAQC's own tested criterion): is the quorum's false-consensus probability (the probability that a strict majority certifies a value failing g(t)) still elevated when agents share a provider/training-lineage basis, relative to when they do not — and is this elevation better predicted by a measured, continuous pairwise correlation estimator than by the coarse provider label itself?

## 5. System and Fault Model

An agent a_i is characterized by a provider/training-lineage label (a coarse, explicitly-flagged-as-imperfect proxy, §6.3) and a set of structural dependencies (runtime evidence roots: tools, shared context, document stores). A task t has ground truth g(t). An agent's error indicator E_i ∈ {0,1} is 1 iff its canonical answer fails g(t). Agents are assumed protocol-compliant throughout (no crash or classical-Byzantine equivocation) — this isolates the semantic-fault phenomenon from faults classical BFT already handles, consistent with EBFT's and DAQC's own scoping.

A quorum is **structural-basis (κ_E) safe** iff no two agents in a decisive coalition share a structural-dependency root (`src/structural/fault_basis.py`, a v1 pairwise-intersection reimplementation from DAQC's published description, not DAQC's own code — flagged explicitly as an open fidelity risk, Reviewer 1's point 3, `REVIEWER_REPORTS.md`).

## 6. Correlation Measurement Framework

Full specification: `CORRELATION_MEASUREMENT.md`. Summary: five candidate pairwise measures (co-error probability, conditional co-error probability, Jaccard agreement-on-error, phi coefficient, mutual information) are defined; the **phi coefficient** is selected as primary on four grounds — direct correspondence to the theoretical model's ρ parameter, signedness (needed for the directional hypothesis), a standard significance/CI apparatus, and lower estimation burden than mutual information under the expected low-error-rate, sparse-contingency-table regime. Mutual information is retained as an exploratory, Miller–Madow-bias-corrected diagnostic only. A behavioral-similarity-on-a-calibration-set proposal is specified as a testable hypothesis, not asserted.

## 7. Formal Analysis

Full derivations and proofs: `FORMAL_RESULTS.md`; machine-checked reproduction: `research/verify_formal_results.py` (re-executed this session; all symbolic and numeric assertions passed).

**Lemma 1.** Under a Beta-mixture common-cause correlated-Bernoulli model (Θ~Beta(α,β); E_1,...,E_n | Θ i.i.d. Bernoulli(Θ)), E[K] = np for K=ΣE_i, invariant to the correlation parameter ρ=1/(α+β+1).

**Lemma 2.** Var(K) = np(1-p)[1+(n-1)ρ] — the standard variance-inflation/design-effect result for clustered binary data (Skellam, 1948).

**Theorem 1 (Correlation-Sensitive False-Consensus Bound).** For a majority threshold q>np, P(K≥q) ≤ V(ρ)/[V(ρ)+(q-np)²] (Cantelli's inequality applied to Lemma 2's variance), strictly increasing in ρ.

**Worked illustration** (exact model computation, not empirical data — Figure 1): at p=0.10, false-consensus probability rises from 0.0086 (ρ=0, n=5, majority) to 0.0842 (ρ=0.5) — roughly a 10× increase — and, critically, **increasing quorum size stops mitigating false consensus once ρ is high**: at ρ=0.9, going from n=3 to n=7 changes false-consensus probability by less than 0.1 percentage points, versus a >10× reduction at ρ=0. This is the formal account of why "add more agents" (classical quorum scaling) is not expected to rescue a highly-correlated quorum — a claim about the model, to be tested against real data, not yet established as a fact about real systems.

**Corollary (interpretive).** Since DAQC's own construction defines κ_E-safety as eliminating correlation attributable to the cut structural basis, any positive ρ measured empirically among a κ_E-safe quorum cannot, by elimination, be attributed to that basis — and Theorem 1 applies to it regardless of source. This reframes what was an unproven, definitional "Proposition 1" in an earlier draft of this project (`gap_analysis_and_manuscript_v2.md` Part K, Reviewer 1's objection) as a corollary of a proven theorem plus DAQC's own prior result, not a standalone assumption.

**What Theorem 1 does not establish**: it says nothing about the *liveness* side (legitimate consensus formation under correlation) — flagged by Reviewer 1 (`REVIEWER_REPORTS.md`) as missing and left as explicit future work, not attempted here.

## 8. Experimental Methodology

### 8.1 Datasets (real, downloaded; `DATASET_FINALIZATION.md`)

GSM8K (1,319 test items, MIT license) and SQuAD 2.0 dev (11,873 questions, 5,945 unanswerable, CC BY-SA 4.0) — both genuinely fetched from their primary sources this session (`datasets/gsm8k/`, `datasets/squad2/`). **FEVER, the dataset originally selected for direct comparability with H-CSC's MVR-50 claim-verification framing, could not be downloaded — `fever.ai` is blocked by this environment's network policy** — and SQuAD 2.0 is a documented substitution with reduced task-style comparability to H-CSC (extractive QA vs. 3-way claim classification; Reviewer 2's point 2).

### 8.2 Design (pre-registered; `configs/experiment_design.yaml`)

2 (structural: κ_E-safe/unsafe) × 3 (correlation level: low/medium/high agent-pool composition) × 2 (quorum size: n=3,5) × 2 (domain) = 24 cells. Correlation level controls agent-pool *composition* only; realized correlation is always measured (§6), never assumed from the label — enforced at the pipeline level (`build_agent_pool` in `experiments/run_factorial_experiment.py`).

### 8.3 Power analysis (computed; `POWER_ANALYSIS.md`)

Primary test: two-proportion z-test, false-consensus rate, low-vs-high correlation groups, within the κ_E-safe stratum. Required N=350/group (power≥0.80, Bonferroni-corrected for 3 planned pairwise contrasts), computed via `statsmodels`, anchored to Theorem 1's model-exact numbers (explicitly labeled a planning anchor, not an empirical estimate — `POWER_ANALYSIS.md` §2). Full-design cost estimate: ≈100,800 agent-level API calls (§5 of that document) — currently unfunded (no API keys in this environment).

### 8.4 Pipeline validation (executed this session — software correctness, not a scientific finding)

Because real LLM execution is blocked, "does our harness reproduce a known correlation effect" (the process's own Phase 8 question) is answered with **positive and negative controls against a known, planted ground truth**, not a replication of any real LLM finding:

- **Negative control** (planted ρ=0, N=500 GSM8K tasks, n=5 agents): estimated φ̂=0.0418 (near zero, as expected); observed false-consensus rate 0.0160 [95% CI 0.0060, 0.0280], containing the theoretical prediction 0.0086.
- **Positive control** (planted ρ=0.5): estimated φ̂=0.6124; observed false-consensus rate 0.0780 [0.0540, 0.1040], containing the theoretical prediction 0.0842.

Both controls passed (full output: `results/harness_validation_report.json`). We note φ̂ and the model's ρ parameter are related but not numerically identical quantities under asymmetric marginals (p=0.10) — φ̂=0.61 against planted ρ=0.5 is consistent with this known, expected relationship, not a pipeline error; the false-consensus-rate cross-check (same units, directly comparable) is the stronger validation and matched theory closely in both controls.

A full 24-cell **pipeline smoke test** (N=30/cell, not the pre-registered N=350) was also run end-to-end (`results/raw_results.csv`, `results/summary_results.csv`) to confirm the complete pipeline — data loading, quorum aggregation, structural-safety checking, scoring, statistics — runs without error and produces correctly-shaped, internally-consistent output (e.g., false-consensus rate rose monotonically with the mock's planted correlation level in every domain/structural/n combination, and structural safety showed zero effect on the mock's outcome — exactly as expected, since the mock's synthetic generative process does not depend on structural dependencies by construction; this is a demonstration that the two factors are correctly isolated in the pipeline, not a finding about real quorums).

## 9. Results

> **THIS SECTION IS DELIBERATELY EMPTY OF REAL FINDINGS. No real LLM has been queried in this project (verified: no API credentials are configured in this environment — `FINAL_RESEARCH_STATUS.md`). The primary hypothesis H1 has not been tested. Every number in §8.4 above is either a proven exact computation under a stated model, or synthetic validation data explicitly labeled as such in every output file (`DATA_LABEL` column in every CSV, explicit banners in every script's printed output). This is stated here, prominently, rather than filled with invented numbers, per this project's non-negotiable constraint.**

When real execution becomes possible (unblock list: `FINAL_RESEARCH_STATUS.md`), this section is filled by running `experiments/run_factorial_experiment.py --backend anthropic` (or `openai`) at `--tasks-per-cell 350` against the pre-registered design, with no other code changes required — the pipeline is complete and validated (§8.4).

## 10. Statistical Analysis

The analysis code (`src/statistics/hypothesis_tests.py`) is implemented and was exercised end-to-end on synthetic data (`results/statistical_tests.csv`, `results/correlation_matrix.csv`) to confirm it runs correctly and produces sensible output (e.g., the synthetic low-vs-high contrast at smoke-test scale, N=200/group, gave z=-4.82, p=1.4×10⁻⁶, risk difference 0.125 [0.076, 0.174] — a real computation, explicitly labeled as underpowered-by-smoke-test-design and not a finding, since 200/group is below the pre-registered 350/group and the underlying data is synthetic). No real statistical inference about real LLM agents has been performed.

## 11. Ablation Studies

Four ablations specified in `gap_analysis_and_manuscript_v2.md`/this project's process were exercised on synthetic data to validate the analysis methodology (§8.4's caveats apply throughout; `results/ablation_label_vs_phi.csv`, `results/figures/fig2_validation_phi_recovers_planted_rho.png`):

- **Label-vs-behavioral-correlation ablation** (the most important, per Reviewer feedback): in a synthetic construction where the true generative process is φ-like and the provider label carries 15% artificial noise, a measured-φ predictor model fit the (synthetic) false-consensus rate better than a label-only model (AIC −195.70 vs. −189.03). This demonstrates the comparison methodology is sound and sufficiently sensitive to detect the difference when it is present by construction. **It does not show this holds for real LLM-agent data** — stated explicitly in the script's own output and repeated here.
- Quorum-size, structural-dependence, and domain ablations were run as slices of the smoke-test factorial output and behaved exactly as the pipeline's construction predicts (§8.4) — software-correctness confirmations, not findings.

## 12. Discussion

Contingent on real execution: if H1 is supported, this would mean DAQC's structural-basis κ_E-safety guarantee — sound and useful as proven relative to its own stated basis — is, in the specific case where agents share training lineage, practically insufficient on its own for bounding false-consensus risk, and a joint structural+provider admission criterion would be needed. If H1 is **not** supported (κ_E-safety turns out practically sufficient because provider-basis correlation is small relative to structural correlation in real deployments), that is an equally valid, useful, publishable outcome — it would bound when DAQC's existing guarantee is practically tight, which is valuable information DAQC's own paper does not currently provide. **This paper commits, in advance, to reporting either outcome with equal prominence** — a commitment Reviewer 4 (`REVIEWER_REPORTS.md`) specifically endorsed keeping through to any real submission.

The formal model also predicts (Theorem 1's worked illustration, §7) that naively increasing quorum size is not an effective mitigation once correlation is high — if confirmed on real data, this would have direct, practical implications for how much a deployed system should be willing to pay (in API calls) to scale up a quorum as a reliability measure, versus investing in reducing correlation (e.g., via genuine provider diversity) instead.

## 13. Threats to Validity

- **Construct validity**: the provider label is a coarse proxy for "training lineage"; the measurement framework (§6) is designed specifically to not rely on it, but real validation of φ as a better predictor than the label remains untested on real data.
- **Internal validity**: the κ_E reimplementation (§5) is from a published description, not DAQC's source; a fidelity gap would mean any real result is not a direct test of DAQC's actual mechanism (Reviewer 1, point 3).
- **External validity**: two datasets, one (SQuAD 2.0) a substitution for the originally-intended FEVER with reduced task-style comparability to the closest prior systems paper (Reviewer 2, point 2); results (once they exist) would need replication on a claim-verification-style task before generalizing the comparison to H-CSC.
- **Statistical validity**: unregularized logistic regression risk under sparse/separated data at real N (Reviewer 3, point 2) is identified but not yet fixed in code — required before real execution, logged in `FINAL_RESEARCH_STATUS.md`.

## 14. Limitations

This paper's empirical contribution does not yet exist. Its contribution, as things stand, is: (a) a proven, verified formal model and bound; (b) a justified, implemented measurement framework; (c) a fully built, validated (on synthetic data) experimental pipeline and pre-registered design; (d) a corrected, narrowed, and defensible account of what remains unaddressed by the closest six prior works, including an honest record of an earlier overclaim in this same project's history and its correction. It is not yet: a paper with real findings about real LLM-agent quorums. The single highest-priority open risk is the unresolved full-text check of DAQC's and H-CSC's complete papers (arXiv access blocked in this environment) to confirm the residual gap claimed in §1.2/§3 survives contact with their full text, not just search-indexed excerpts.

## 15. Conclusion

We have formalized, proven, and built — but not yet run at scale against real agents — a specific, narrow, and (as far as verifiable in this environment) genuinely open empirical question left by the closest six prior works: whether DAQC's structural-basis κ_E-safety guarantee, sound as proven relative to its own stated fault basis, is practically sufficient once a second, named-but-untested basis (provider/training-lineage correlation, independently measured at the model-output level by Kim et al. and arXiv:2603.06612) is accounted for. The theory (Theorem 1) and measurement framework are complete and verified; the empirical answer is not yet known, and this paper does not pretend otherwise.

## References

He, J., Yu, D. (2026a). "The Honest Quorum Problem: Epistemic Byzantine Fault Tolerance for Agentic Infrastructure." arXiv:2607.16109.
He, J., Yu, D. (2026b). "The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums." arXiv:2609.02925.
Xu, H., Zhang, L., Ounis, I., Wang, X. (2026). "Hierarchical Certified Semantic Commitment for Byzantine-Resilient LLM-Agent Collaboration." arXiv:2606.07316.
Rodrigues, C. (2026). "Hallucination as Context Drift: Synchronization Protocols for Multi-Agent LLM Systems." arXiv:2606.21666.
Kim, et al. (2025). "Correlated Errors in Large Language Models." ICML 2025 / arXiv:2506.07962.
"Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness." (2026). arXiv:2603.06612.
Lamport, L., Shostak, R., Pease, M. (1982). "The Byzantine Generals Problem." ACM TOPLAS.
Skellam, J.G. (1948). Foundational reference for the Beta-Binomial distribution (clustered/overdispersed binary data).
Cobbe, K. et al. (2021). "Training Verifiers to Solve Math Word Problems." arXiv:2110.14168. [GSM8K]
Rajpurkar, P., Jia, R., Liang, P. (2018). "Know What You Don't Know: Unanswerable Questions for SQuAD." ACL 2018 / arXiv:1806.03822. [SQuAD 2.0]
Thorne, J. et al. (2018). "FEVER: a large-scale dataset for Fact Extraction and VERification." NAACL-HLT 2018. [FEVER — cited for comparison; not used, see §8.1]

*All arXiv/search-based citations above were verified via targeted search against title, author, and specific numeric claims (`FINAL_NOVELTY_GATE.md` §0–§1); full-PDF verification was not possible in this environment (network policy — see `FINAL_RESEARCH_STATUS.md`) and remains the top blocking item before this manuscript is submission-ready.*
