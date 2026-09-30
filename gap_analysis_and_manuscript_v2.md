# Salvage Analysis and Manuscript v2

*Working document. Produced in response to a directed second literature audit. Nothing in Parts F–onward reports executed results — see Step 6 disclosure.*

---

## PART A — Novelty Audit (Round 2)

### A.1 Verified closest works (checked against arXiv abstracts directly, not taken on trust)

| # | Paper | Verified | Core claim |
|---|---|---|---|
| 1 | He & Yu, "The Honest Quorum Problem: Epistemic Byzantine Fault Tolerance for Agentic Infrastructure," arXiv:2607.16109 (2026) | Yes | Defines *epistemic fault*: an authenticated, non-equivocating, protocol-compliant validator that still endorses a semantically invalid transition. Defines EBFT with two confidence-indexed bounds (e_δ for coherent invalid endorsements, u_ε for unusable support). States explicitly that "agreement alone does not guarantee semantic validity or execution safety" and that correlated epistemic faults arise because validators "share model weights, training distributions, prompts, or toolchains." |
| 2 | He & Yu, "The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums," arXiv:2609.02925 (2026) | Yes | Defines Epistemic Fault Domain (EFD): the set of agents structurally reachable from a single fault in an explicit, *modeled* Epistemic Fault Basis (e.g., corrupted telemetry, poisoned tool output, compromised document store). Defines Structural Epistemic Cut κ_E and a Dependency-Aware Quorum Controller (DAQC) that enforces cuts at admission time. Ships a frozen 120-task benchmark (5 operational categories, 16 unsafe/8 safe per category) built around *runtime provenance/dependency* — each task's evidence packages are rooted in distinct modeled evidence sources (e.g., CloudWatch metric vs. VPC flow log vs. DB transaction status). |
| 3 | Xu, Zhang, Ounis, Wang, "Hierarchical Certified Semantic Commitment for Byzantine-Resilient LLM-Agent Collaboration," arXiv:2606.07316 (2026) | Yes | H-CSC: a BFT-inspired protocol that converts embedding-derived finality signals over verdict-conditioned proposals into a typed outcome (semantic_commit / verdict_commit / typed abort). Evaluated on a real benchmark (MVR-50, 50 claim-verification tasks) under static and rushing Byzantine attacks; reports commit rates and honest-reference-invalid rates. This is an *engineered protocol with empirical evaluation*, not a fault-model paper. |
| 4 | Rodrigues, "Hallucination as Context Drift: Synchronization Protocols for Multi-Agent LLM Systems," arXiv:2606.21666 (2026) | Yes | Defines Context Divergence Score (CDS) and Shared State Verification Protocol (SSVP). Evaluated in two domains (travel planning, software project planning) with concrete numbers (naive full-broadcast sync *increases* hallucination 34% over no-sync; SSVP avoids this while cutting API calls 58% vs. full-broadcast). This is about *state staleness between agents*, not quorum voting under Byzantine/adversarial conditions. |
| 5 | Kim et al., "Correlated Errors in Large Language Models," ICML 2025 / arXiv:2506.07962 | Yes | Large-scale empirical study (350+ models, two leaderboards, one resume-screening task): LLM errors are substantially correlated (on one leaderboard, models agree 60% of the time *when both err*); correlation persists even across distinct architectures and providers once models are large/accurate, driven by shared training corpora and optimization objectives ("algorithmic monoculture"), not by shared runtime infrastructure. |
| 6 | "Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness," arXiv:2603.06612 (2026) | Yes | Across 5 benchmarks and multiple models, polling/self-consistency-style aggregation does not reliably improve accuracy over single-sample baselines even at 25× inference cost, and *amplifies* shared misconceptions. Shows correlation exists even on out-of-distribution random-string generation tasks — i.e., a source of correlation with **no runtime dependency whatsoever** (no shared tools, no shared context, no shared document store). Explicitly frames this as a failure of the "errors must be at most weakly correlated" assumption underlying crowd-wisdom methods. |

### A.2 What this does to the original claim

Your original manuscript's central claim — "protocol-compliant-but-meaning-corrupt is an unnamed fault class; classical BFT quorum guarantees silently fail under it" — is **fully anticipated and formalized, with sharper apparatus, by #1 and #2**. #1 names the fault (*epistemic fault*) and gives it a bound-based theory (EBFT) your manuscript did not have. #2 gives correlation a *structural* model (EFD/κ_E) your manuscript gestured at informally ("shared training/context makes errors correlated") without formalizing. #3 already builds and empirically evaluates a certified commit protocol for exactly this setting. #4 already treats the specific mechanism you cited (context drift) as a synchronization problem, with real numbers.

There is no honest path to claiming novelty for "a new fault class for protocol-compliant-but-semantically-wrong LLM agents." That framing is now well-trodden ground as of 2026. Your instinct to abandon defending it is correct.

### A.3 What is NOT yet covered by any of the six

This is the part that matters. Re-reading #1's and #2's own stated assumptions carefully:

- **EBFT (#1)** treats correlated epistemic faults as an empirical *given* it bounds probabilistically (e_δ, u_ε), not something it explains the *origin* of or distinguishes by *source*.
- **EFD/DAQC (#2)** formalizes correlation through an explicit, *modeled, observable* Epistemic Fault Basis — i.e., correlation that flows through **runtime provenance**: shared tool calls, shared telemetry sources, shared document stores. Its own benchmark is built entirely around this: each task's evidence packages are "rooted in distinct modeled evidence roots" (CloudWatch metric, VPC flow analyzer, DB transaction status — all runtime data sources). κ_E is defined over a dependency graph that DAQC can observe and cut at admission time.
- **#5 and #6**, however, independently demonstrate a *second, different* correlation channel: errors correlated **across agents with no shared runtime dependency at all** — different providers, different architectures, and in #6's strongest case, correlated even on adversarially decorrelated (random-string) tasks with no shared document, tool, or telemetry source in sight. This correlation is attributed to shared *training corpora and optimization objectives* — i.e., it is baked into model weights before the runtime dependency graph DAQC models even exists.

**Neither #1 nor #2 engages with #5/#6's finding.** Neither #5 nor #6 engages with #1/#2's quorum/fault-tolerance framing, DAQC's admission-control mechanism, or the question of whether a structural cut (κ_E) is sufficient once this second channel is accounted for. No paper in this set asks the direct question: *if DAQC enforces κ_E-safety (cuts every modeled structural dependency it knows about), does the quorum's false-consensus rate actually drop to the level its safety guarantee implies — or does weight-level correlation reassert itself through a channel the model doesn't see?*

That is the gap. It is precise, it is falsifiable, and it is a direct, citable extension/stress-test of #2's own stated threat model, not a rebranding of #1.

---

## PART B — What must be removed from the original manuscript

Explicitly obsolete or unsafe claims from `paper.md`, and why:

| Original claim | Disposition | Reason |
|---|---|---|
| "We call this a semantic Byzantine fault (SBF)... a fault the classical dichotomy does not capture" | **Remove.** | Directly anticipated by He & Yu's *epistemic fault* (#1), with a formal probabilistic bound your version lacked. Keeping this invites an immediate, correct desk-reject citing #1. |
| "This is, we believe, the precise formal reason why naive multi-agent voting... provide much weaker guarantees" | **Remove/replace.** | #6 already demonstrates this empirically and more rigorously (5 benchmarks, 25× compute scaling, explicit mechanism). Our version was speculative; theirs is measured. |
| "BFT assumes semantically independent oracles for truth... unless a primary source proves that claim" | **Remove as stated.** | No primary BFT source states this; it was an inference, not a textbook fact. The literature-verified formulation (Part D) is the only defensible version: BFT's *agreement* and *validity* properties are about the value being *proposed by some party and not conflicting*, not about the value's correspondence to external ground truth. Conflating "no two correct nodes disagree" with "the agreed value is true" is the actual error to name — not an unsupported claim about BFT's design assumptions. |
| "Quorum intersection fails under SBFs" | **Remove as stated; replace with precise version.** | Quorum intersection does exactly what it is specified to do (guarantee agreement/safety among *correct* nodes under the stated fault bound). It does not "fail" — it was never a truth oracle. The defensible claim is: *quorum intersection's safety guarantee does not transfer to a semantic-validity guarantee when "correct" (protocol-compliant) nodes can still jointly certify a semantically false value* — which is precisely what #1 and #2 already formalize. This point survives only as background, not as our contribution. |
| §5 (semantic quorum certificates, drift-aware view changes, semantic checksum) as "our proposed mechanisms" | **Remove as a contribution claim.** | These are now, respectively, close cousins of H-CSC's typed commit certificates (#3), a rough echo of SSVP's divergence-triggered synchronization (#4), and DAQC's admission-time cut (#2). Presenting them as novel mechanisms is no longer defensible. They can survive only as a related-work comparison table entry, not as §6 of a new manuscript. |
| Title: "Semantic Byzantine Faults: A New Fault Model..." | **Remove.** | "New fault model" is the exact claim #1 already owns. |

What survives, reframed as background rather than contribution: the *motivating observation* (protocol conformance ≠ semantic correctness) and the informal intuition about shared training driving correlation — both now correctly attributed to prior work and used to set up the actual gap in Part C.

---

## PART C — Selected contribution

**Primary contribution:**

> **An empirical and formal investigation of whether structural epistemic independence (as formalized by Epistemic Fault Domains / the Structural Epistemic Cut κ_E) is sufficient to bound false-consensus probability in LLM-agent quorums, or whether an orthogonal, non-structural correlation channel — parametric correlation induced by shared training lineage — persists even when all modeled runtime dependencies are cut, and must be treated as a second, independent admission-control dimension.**

Working name for the distinction: **structural epistemic independence** (what DAQC's κ_E targets: independence of tool calls, data sources, telemetry, document stores) vs. **parametric epistemic independence** (independence of training lineage: base model family, pretraining corpus, RLHF/alignment pipeline, fine-tuning data) — with the central testable hypothesis:

> **H1:** Holding structural independence fixed at κ_E-safe (no shared modeled fault root, per DAQC's own admission criterion), false-consensus rate is still significantly higher for agent sets drawn from the same training lineage than for agent sets drawn from independent training lineages.

Two bounded supporting contributions:

- **C1 (formal):** A proposition characterizing the relationship between κ_E-safety and false-consensus probability, showing the conditions under which κ_E-safety is necessary-but-not-sufficient (i.e., formalizing *why* H1 could be true without contradicting DAQC's own theorem, since DAQC's guarantee is stated relative to its *modeled* fault basis, and parametric correlation is by construction outside that basis).
- **C2 (methodological):** A fault-injection benchmark protocol that, unlike DAQC's benchmark (which varies structural provenance) and unlike #5/#6 (which don't use a quorum/admission-control framing), varies **both axes orthogonally** (structural × parametric) so the interaction, not just each main effect, can be measured.

### Why a reviewer who knows EBFT/DAQC/H-CSC could reasonably call this new

- It does not propose a new fault name — it takes DAQC's own fault basis formalism as given and asks a question DAQC's paper does not ask about its own mechanism: does cutting the modeled basis fully close the false-consensus gap, or only the structurally-mediated part of it?
- It is falsifiable in a direction that could also vindicate DAQC (if H1 is rejected — i.e., κ_E-safety turns out sufficient in practice because parametric correlation is small relative to structural correlation — that is itself a publishable, useful negative result bounding when DAQC's guarantee is practically tight).
- It sits at a genuine disciplinary seam: #5/#6 are ML-evaluation papers with no quorum/admission-control framing and no engagement with κ_E or DAQC; #1/#2/#3 are systems papers with no engagement with the ML-side finding that correlation exists without any modeled runtime dependency. Nobody has yet asked whether DAQC's guarantee, which is explicitly relative to *its own modeled basis*, is undermined by a channel that by construction cannot appear in that basis.

### What would kill this contribution (stated honestly, not hidden)

- If H-CSC's embedding-derived semantic certification (#3) already implicitly absorbs parametric correlation effects into its commit/abort decision in a way that makes the structural/parametric distinction practically moot — this needs to be checked against the full H-CSC paper (only the abstract/summary was verified here) before submission.
- If DAQC's Epistemic Fault Basis is, on reading the full paper, explicitly defined broadly enough to already include "shared model family" as a modeled fault root (the search summary did not surface this, but the full paper must be read, not just the abstract, before claiming the gap holds).
- **Action required before this is submission-safe:** obtain and read the full text of #2 and #3 (not just search-engine summaries) to confirm neither already defines a parametric/training-lineage fault root in its basis. This document does not yet do that and should not be treated as having done it.

---

## PART D — Formal model (revised, literature-checked)

### D.1 System model

- A set of agents A = {a_1, ..., a_n}, each a_i an LLM-backed process with a declared training lineage L(a_i) (base model family, training corpus class, alignment pipeline) and a declared runtime dependency set R(a_i) (tools invoked, data sources read, context shared with other agents).
- A task t with an authoritative ground-truth predicate g(t) — used only for offline evaluation, not assumed available to agents at runtime (consistent with DAQC's benchmark design, which supplies an executable predicate per task for evaluation purposes only).
- Each agent produces a protocol-conformant output m_i(t): a value plus supporting rationale, always well-formed (never malformed, never off-protocol — by construction of the experiment, agents are never given a reason to violate protocol; this isolates the phenomenon under study from ordinary crash/equivocation faults, which are already well handled by classical BFT and are explicitly out of scope).

### D.2 The two independence axes

- **Structural independence** between a_i, a_j: R(a_i) ∩ R(a_j) = ∅ at the level of DAQC's Epistemic Fault Basis — i.e., no shared modeled fault root. This is exactly DAQC's κ_E condition, imported unchanged; we do not redefine it.
- **Parametric independence** between a_i, a_j: L(a_i) ≠ L(a_j) at a coarse level (different base model family and, where knowable, different major pretraining/alignment lineage). We do **not** claim this is a complete or principled formalization of "training similarity" — it is an operational proxy (model family/provider as a coarse label), and this limitation must be stated plainly in the manuscript, not hidden. A finer-grained notion (e.g., embedding-space distance between models' output distributions, as used for unrelated purposes in #3) is future work, not assumed here.

### D.3 Precise statement of what classical BFT and EBFT/DAQC do and do not guarantee

Verified against the definitions surfaced in the literature check (Part A), classical Byzantine agreement guarantees, for n ≥ 3f+1 with at most f Byzantine nodes:

- **Agreement:** every correct node outputs the same value.
- **Validity:** the agreed value was proposed by some party (not a guarantee of external truth).
- **Termination/liveness:** correct nodes eventually decide.

None of these three properties is a guarantee that the agreed value corresponds to ground truth in an open-world sense — this was never BFT's job, and the literature (#1's own framing) makes the same point explicitly: *"agreement alone does not guarantee semantic validity or execution safety."*

EBFT (#1) extends this by bounding, probabilistically, the rate of coherent-but-invalid endorsement (e_δ). DAQC (#2) extends this further by bounding correlated failure *relative to a modeled structural fault basis* via κ_E. Neither claims to bound correlation arising outside that basis — and to our knowledge (pending the full-text check flagged in Part C) neither engages the possibility.

### Proposition 1 (formal, our contribution — conditional)

*Statement.* Let a quorum Q of size 2f+1 be κ_E-safe under DAQC's admission criterion (no shared modeled fault root among any decisive coalition in Q). Let ρ_struct and ρ_param denote the marginal contributions of structural and parametric correlation, respectively, to the joint probability that a majority of Q endorses a common semantically invalid value, under a factorization assumption that these two correlation sources act through distinguishable causal channels (data flow vs. weight-level prior). Then κ_E-safety provably bounds only the ρ_struct component; the residual false-consensus probability is bounded below by a term proportional to ρ_param, which κ_E-safety does not constrain.

*Status.* This is a **conditional, structural** proposition — a consequence of how κ_E is defined (over a specific modeled basis) plus an assumption (channel distinguishability) that is plausible given #5/#6's random-string result (correlation surviving even absent any shared data-flow path) but not proven in general. It is **not** a claim that we can currently bound ρ_param's magnitude — that is an empirical question, addressed in Part F, not a theorem. The proof obligation that remains is showing the factorization assumption holds, or characterizing when it doesn't; this is flagged as an open technical risk, not resolved here.

This replaces the previous manuscript's unsupported "quorum intersection fails" claim with a scoped, literature-consistent statement: **the guarantee is sound relative to its stated basis; the question is whether that basis is complete, and Proposition 1 gives a structural reason to expect it is not, pending empirical confirmation in Part F.**

---

## PART E — Proposed method (scope-appropriate)

Given C1/C2, the "method" this paper needs is not a new protocol competing with H-CSC/DAQC — it is a **measurement instrument**: a dual-axis fault-injection harness that can be layered on top of an existing admission-control mechanism (DAQC, or a simplified reimplementation of its admission criterion) to test Proposition 1.

**Components:**
1. A task suite with ground truth and executable verification (reuse/adapt an existing public benchmark with verifiable answers — see Part G; do not build a new one from scratch without strong justification, to avoid the well-known risk of an underpowered, non-comparable benchmark).
2. An agent pool spanning ≥3 distinct model families/providers (parametric axis) × ≥2 runtime-dependency configurations per task (shared vs. independent tools/context; structural axis), giving a 2×3 (minimum) design, ideally finer-grained.
3. A κ_E-style admission check (reimplemented at the level described in DAQC's abstract; full-text needed before committing to an exact reimplementation — see Part C risk note).
4. Measurement of false-consensus rate, semantic accuracy, and agreement rate within each cell of the design.

This is deliberately modest in engineering scope relative to H-CSC or DAQC's own systems — the contribution is the *measurement*, not a new production protocol, which is an honest match to what is actually novel here.

---

## PART F — Experimental design

### Research questions (revised from your RQ list, scoped to what this contribution can actually answer)

- **RQ1 (primary):** Holding structural independence at κ_E-safe, does false-consensus rate differ significantly between same-lineage and cross-lineage agent quorums? (Tests H1 / Proposition 1.)
- **RQ2:** Does increasing quorum size (2f+1 → larger) reduce false-consensus rate when only structural independence is enforced, versus when both structural and parametric independence are enforced?
- **RQ3:** Is the magnitude of the parametric-correlation effect (if any) large enough to be practically relevant relative to DAQC's reported structural-correlation effect, or is it a second-order correction?
- **RQ4 (secondary/exploratory):** Does task difficulty or domain (factual recall vs. multi-step reasoning vs. tool-use verification) modulate the size of the parametric-correlation effect?

Explicitly dropped from your original RQ list as not addressable by this scoped contribution without much larger engineering investment: RQ5/RQ6 (evidence-diversity vs. agent-count tradeoffs, verification cost tradeoffs) — these are H-CSC's and DAQC's territory already; re-deriving them would be redundant, not novel.

### Design table

| Factor | Levels |
|---|---|
| Structural independence | shared context/tools (κ_E-unsafe) vs. independent (κ_E-safe) |
| Parametric independence | same model family vs. cross-family (≥3 families) |
| Quorum size | 2f+1 at f=1 (n=3), f=2 (n=5) — minimum two points to see a size trend |
| Task domain | at least 2 domains from Part G, to test RQ4 |

Minimum viable design: 2 (structural) × 3 (parametric, pairwise same-vs-cross across 3 families) × 2 (quorum size) × 2 (domain) = 24 cells, each run with enough tasks and seeds for a statistically defensible estimate (power analysis needed before finalizing N — not yet done; flagged as required pre-registration step, not skipped silently).

### Metrics

Semantic accuracy; agreement rate; **false-consensus rate** (quorum reaches agreement on a value that fails g(t)) — the primary outcome metric for RQ1; fault detection rate / false positive / false negative of the κ_E admission check itself; latency; token cost; communication overhead. 95% confidence intervals via bootstrap over tasks; ≥3 random seeds per cell (temperature/sampling seed, not a claim of full determinism, which LLM APIs do not generally provide).

---

## PART G — Baselines and datasets

**Baselines (real, not invented):**
- Single-agent baseline (no aggregation).
- Unweighted majority voting (the "crowd wisdom" baseline shown to fail by #6 — reusing their protocol description, not reinventing it).
- DAQC-style structural-only admission control (#2) — reimplemented at the level of published detail; this is the paper we are directly stress-testing.
- H-CSC-style semantic commit certification (#3) — included as a second, stronger baseline if implementation detail in the full paper permits faithful reimplementation; otherwise cited/discussed but not reimplemented, stated honestly rather than faked.

**Datasets — candidates, not yet finalized:**
- A factual QA benchmark with unambiguous ground truth (e.g., an existing open QA benchmark with verifiable short-answer ground truth) for RQ1/RQ2's cleanest signal.
- A claim-verification-style task resembling MVR-50's structure (#3) for comparability with H-CSC's evaluation, if MVR-50 itself is publicly released; otherwise an equivalent public claim-verification set, cited exactly.
- A multi-step reasoning/tool-use task for RQ4, to test whether the effect (if any) generalizes beyond single-shot factual recall.

Exact dataset selection, licenses, and citations are a pre-registration step that must be completed and verified against primary sources before any run — not asserted here.

---

## PART H — Verified literature table

| Claim used in this manuscript | Source | Verified how |
|---|---|---|
| Epistemic fault defined; EBFT bounds (e_δ, u_ε); "agreement alone does not guarantee semantic validity" | He & Yu, arXiv:2607.16109 | Abstract/summary confirmed via direct search of arXiv listing (title + authors + arXiv ID match) |
| EFD, κ_E, DAQC, 120-task benchmark, 5 categories/16+8 split | He & Yu, arXiv:2609.02925 | Same |
| H-CSC, MVR-50, commit rates 0.90/0.92, honest-reference-invalid 0.02/0.00 | Xu, Zhang, Ounis, Wang, arXiv:2606.07316 | Same |
| CDS, SSVP, +34% hallucination under naive full-broadcast, −58% API calls | Rodrigues, arXiv:2606.21666 | Same |
| Correlated errors across 350+ models, 60% co-error agreement, algorithmic monoculture | Kim et al., ICML 2025 / arXiv:2506.07962 | Same |
| Polling amplifies shared misconceptions; fails even on random-string OOD tasks; 25× compute, 5 benchmarks | arXiv:2603.06612 | Same |
| Classical Byzantine agreement/validity/termination definitions | Standard distributed-computing literature (Lamport-Shostak-Pease lineage; confirmed via general search, not a single pinned textbook citation) | Cross-checked phrasing against multiple independent summaries; **a single canonical textbook/paper citation (e.g., Cachin, Guerraoui & Rodrigues, "Introduction to Reliable and Secure Distributed Programming") should be pinned before submission** rather than left as a general citation |

**Flag:** every entry above was verified via search-engine-surfaced abstracts/summaries, not by reading full PDFs end-to-end in this session. Before submission, the full text of #1–#4 in particular must be read directly to (a) confirm the gap in Part C still holds and (b) extract precise notation/theorem statements rather than paraphrased summaries.

---

## PART I — Target journal/venue fit

Given the contribution is now a *measurement study extending a specific prior formal model*, not a foundational new theory, appropriate venues are empirically-oriented systems/dependability venues rather than purely theoretical ones.

1. **Primary:** *IEEE Transactions on Dependable and Secure Computing* — scope explicitly covers fault tolerance and dependability of distributed/AI-integrated systems; publishes both formal and empirical dependability work; would expect the full experimental design in Part F executed, not just designed.
2. **Second:** *ACM Transactions on Autonomous and Adaptive Systems* — fits the multi-agent/autonomous-systems framing; more tolerant of a measurement-study contribution alongside a bounded formal proposition than a pure theory venue would be.
3. **Third (workshop/earlier-stage fallback):** A systems workshop such as HotOS or a dependability workshop (e.g., associated with DSN — Dependable Systems and Networks) as a venue for the formal proposition (Part D) and design (Part F) *before* full execution, explicitly as a work-in-progress/vision contribution — consistent with your own Step 9's demand that we not overclaim venue fit.

No claim is made here about impact factor, indexing status, or acceptance likelihood beyond scope fit — that would need current verification against each venue's own site, which was not done in this pass.

---

## PART J — Rewritten manuscript (draft, theory + design only — see disclosure)

See `paper_v2_draft.md` (companion file) for the full rewritten manuscript text using the structure you specified (Introduction → ... → Conclusion), built around Parts B–I above, with **Results and Ablation sections left as explicit placeholders**, per Step 6, because no experiment has been run.

---

## PART K — Reviewer #1 (Distributed Systems / BFT expert) — simulated

**Report:**
- The formal contribution (Proposition 1) is a useful scoping statement but is *conditional* on a factorization assumption that is asserted, not proven. As written, this is closer to a well-motivated hypothesis than a theorem. Either prove the factorization holds under stated conditions, or relabel Proposition 1 as a conjecture and be explicit that Part F is designed to test it, not to confirm it.
- Reusing DAQC's κ_E without access to the full paper's formal definitions is risky — if DAQC's Epistemic Fault Basis already permits modeling "shared model family" as a fault root, this paper's central gap claim collapses. This must be resolved before submission, not after.
- The classical BFT background section must clearly separate "agreement/validity as BFT defines them" from "semantic/external validity" using the standard textbook vocabulary (safety/liveness), which the current draft does correctly per Part D but should cite a single pinned primary source, not general web summaries.

**Author response:** Agreed on all three points. Proposition 1 is relabeled explicitly as a *conditional structural proposition*, not a theorem, in the rewritten manuscript (Part D, restated in `paper_v2_draft.md`). Confirming DAQC's exact fault-basis definition against the full paper is added as a blocking pre-submission action item (Part C, Part H flag). A single primary BFT citation will be pinned (recommend Cachin, Guerraoui & Rodrigues) rather than left general.

## PART L — Reviewer #2 (LLM / Agent Systems expert) — simulated

**Report:**
- "Same model family" as an operational proxy for parametric correlation is coarse — two deployments of the "same family" can differ substantially in fine-tuning, and two different providers' flagship models may share more pretraining-data overlap with each other than with their own smaller siblings. This proxy needs either justification or a finer-grained measure (e.g., output-distribution similarity on a calibration set) before the empirical claim is trustworthy.
- The dataset selection in Part G is still a placeholder list, not a decision. A reviewer will not accept "candidates, not yet finalized" in a submitted paper.
- Given #6 already shows the random-string OOD result, this paper should explicitly replicate a small slice of that condition as a sanity check that the experimental harness reproduces a known effect before trusting it on the new factorial design.

**Author response:** Accepted. The manuscript will (a) report the coarse proxy as an explicit, stated limitation with the finer-grained alternative named as future work, not silently used as if precise; (b) finalize dataset selection before submission — this document correctly does not pretend that step is done; (c) add a replication sub-experiment reproducing a small-scale version of #6's random-string finding as a validity check on the harness, added to Part F's design as a required first phase.

## PART M — Reviewer #3 (AI Reliability / Trustworthy AI expert) — simulated

**Report:**
- The paper risks being "a stress test of someone else's benchmark" rather than a self-standing contribution if RQ3 ("is the effect practically relevant") comes back negative. The authors should pre-commit to publishing a null result honestly (Step 6's spirit) rather than quietly dropping the paper if H1 is rejected.
- Statistical power analysis is promised but not done (Part F says so honestly) — this needs to happen before any run, not be treated as an afterthought, or the CI claims in Part F's metrics section will not be defensible.
- "Ground truth" for reasoning/tool-use tasks (RQ4) is often itself contested or partially subjective; the paper needs a concrete, defensible ground-truth procedure for each dataset chosen, not an assumption that g(t) is unproblematic.

**Author response:** Accepted. The manuscript commits explicitly (Discussion/Limitations sections, `paper_v2_draft.md`) to reporting a null result for H1 as a valid outcome, framed as bounding when DAQC's guarantee is practically tight rather than as a failed paper. Power analysis is added as a required, blocking pre-registration step before Part F executes. Ground-truth procedure per dataset will be specified per-dataset once Part G's selection is finalized, rather than assumed uniform.

## PART N — Editor assessment — simulated

A conditional, scoped empirical-measurement contribution layered on two specific, recent, verified prior works (EBFT/DAQC) with a connection to an independent, also-verified ML finding (#5/#6) that neither engages with, is a defensible basis for review *if and only if*: (1) the full text of #2 confirms the claimed gap still exists (blocking risk, Part C/K), (2) the experiment in Part F is actually executed with the pre-registered design (power analysis, dataset finalization, harness validation against #6), and (3) Proposition 1 is presented as conditional throughout, not inflated into a theorem. As a theory-only submission with no results, this is not yet ready for the primary or second target journal in Part I; it is appropriately positioned, in its current state, only for the workshop/vision-paper fallback (Part I, target 3), pending execution of Part F.

## PART O — Final claim audit

| Claim | Evidence | Citation | Type |
|---|---|---|---|
| Classical BFT agreement/validity do not guarantee external/semantic truth | Standard distributed-computing definitions | Lamport-Shostak-Pease lineage (pin exact source pre-submission) | Fact |
| Epistemic faults / EBFT exist and are formalized with e_δ, u_ε | Paper abstract, confirmed | arXiv:2607.16109 | Fact (about prior work) |
| κ_E / DAQC formalize structural correlation via a modeled fault basis | Paper abstract, confirmed | arXiv:2609.02925 | Fact (about prior work) — **full text not yet read; gap claim conditional on this** |
| LLM errors correlate across providers/architectures via shared training, even OOD | Paper abstracts, confirmed | arXiv:2506.07962; arXiv:2603.06612 | Fact (about prior work) |
| κ_E-safety bounds only structural correlation, not parametric | Our derivation from the above | — | Original, **conditional proposition, not proven theorem** |
| H1 (same-lineage quorums show higher false-consensus than cross-lineage at fixed κ_E-safety) | Not yet tested | — | Hypothesis — explicitly unconfirmed |
| Any specific accuracy/false-consensus/cost number for our method | **None exist** | — | Not claimed; placeholders only (see `paper_v2_draft.md` §9) |

No instance of "clearly," "obviously," "for the first time," "completely novel," "proven superior" describing our own contribution appears in the rewritten manuscript; all are either removed or replaced with "conditional," "designed to test," or "not yet established."

---

## PART P — Final submission checklist (status, not a promise)

- [ ] Read full text of arXiv:2609.02925 and arXiv:2606.07316 to confirm Part C's gap survives contact with their actual definitions (**blocking — not done in this pass**)
- [ ] Pin a single primary BFT citation for agreement/validity/termination definitions
- [ ] Finalize dataset selection with exact citations/licenses (Part G)
- [ ] Run power analysis before any experiment (Part F)
- [ ] Implement harness; validate against #6's random-string replication before trusting factorial results
- [ ] Execute Part F design; fill `paper_v2_draft.md` §9/§10 with real numbers, including null-result reporting if H1 is rejected
- [ ] Re-run Parts K–N reviewer simulation against the version with real results, not just design
- [ ] Only then consider submission to Part I's primary/second target; until results exist, workshop/vision-paper track only

---

## Final novelty sentence (Step 10)

**"The contribution that remains novel after accounting for the 2026 literature is: an empirical and formal test of whether DAQC's structural Epistemic Fault Domain model (κ_E) — which bounds correlated failure only relative to a modeled runtime-dependency basis — is sufficient to bound false-consensus probability in LLM-agent quorums, or whether parametric correlation from shared training lineage (independently demonstrated, but never connected to quorum admission control, by Kim et al. 2025 and arXiv:2603.06612) persists outside that basis and must be treated as a second, orthogonal admission-control dimension — a question neither the epistemic-fault-tolerance systems literature (EBFT, DAQC, H-CSC) nor the correlated-error ML literature currently asks jointly."**

This sentence is falsifiable, is not a renamed existing concept, and its truth is not yet known — which is the honest state of the project at this point.
