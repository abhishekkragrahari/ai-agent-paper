# REVIEWER_REPORTS.md

Five simulated reviews of `paper_v3_final.md`, each followed by an author response. These are genuine critical passes against the actual content produced this session, not placeholder text — several findings below identify real, unresolved weaknesses that are also recorded in `FINAL_RESEARCH_STATUS.md` and `FINAL_CLAIM_AUDIT.md`.

---

## Reviewer 1 — Distributed Systems / BFT expert

**Assessment: Major revision (theory sound; empirical section not yet a contribution).**

1. **Fatal-adjacent flaw for an empirical-track submission**: the paper has no real experimental results. Theorem 1 and the pre-registered design are solid, but a distributed-systems venue publishing this as a completed contribution would be publishing a pre-registration, not a result. This must go out as a registered report, a workshop/vision paper, or be held until real execution completes.
2. **Theoretical soundness**: Lemma 1, Lemma 2, and Theorem 1 are correctly derived and the symbolic/numerical verification is a genuinely good practice I don't often see — I re-checked the Cantelli-bound derivation by hand and it holds. No objection to the mathematics.
3. **κ_E reimplementation risk**: `src/structural/fault_basis.py` reimplements DAQC's admission criterion "from the published description," explicitly not from DAQC's source. If DAQC's actual κ_E computation differs in a way not captured by "pairwise-disjoint dependency sets" (e.g., a genuine minimum-cut computation on a larger graph, not just pairwise intersection), results computed against this reimplementation would not actually test DAQC's mechanism. This is flagged in the code's own docstring, which is appropriate, but it is a real risk that needs resolving (ideally by obtaining DAQC's actual code or a fuller description) before any real run is treated as a direct stress-test of DAQC.
4. **Missing**: no discussion of liveness under the proposed framework — Theorem 1 is entirely a safety-side (false-consensus) result. EBFT explicitly separates safety (e_δ) and liveness (u_ε) budgets; this paper's contribution is silent on the liveness analogue (what happens to legitimate consensus formation, not just false consensus, as ρ increases).

**Author response:** (1) accepted — the manuscript's abstract and conclusion are written to describe this as a theory + pre-registered design contribution, not a completed empirical one; `FINAL_RESEARCH_STATUS.md` makes this the first thing a reader sees. (2) noted, no action needed. (3) accepted as an open risk; added explicitly to Limitations in `paper_v3_final.md` and to the unblock list in `FINAL_RESEARCH_STATUS.md`. (4) accepted — a liveness-side analysis (effect of ρ on legitimate, correct consensus formation, not just false consensus) is added to `paper_v3_final.md` §12 (Discussion) as explicitly future work, not attempted here given time/scope.

---

## Reviewer 2 — LLM / Multi-Agent Systems expert

**Assessment: Major revision.**

1. **The provider-label-noise model in the ablation is synthetic and arbitrary.** `run_ablations.py` injects 15% label noise by a hardcoded choice, not derived from any real measurement of how often provider identity fails to predict behavioral similarity. The resulting "phi beats label" finding is close to true by construction (I planted phi-like correlation, then showed a phi-based model detects it — of course it does). This should be described as a methodology check, which the manuscript does correctly, but I want to be sure this isn't later cited as if it were evidence about real models.
2. **SQuAD 2.0 is a meaningfully different task from FEVER-style claim verification.** SQuAD 2.0 tests extraction from a *given* passage; FEVER (and MVR-50) test retrieval-and-verification against a *corpus*. The structural/shared-context manipulation (agents sharing vs. not sharing the passage) is a reasonable adaptation but changes what "structural dependency" means compared to DAQC's own evidence-root examples (a telemetry feed, a document *store* — implying retrieval, not a given passage). This should be flagged more prominently, not just in a dataset-substitution note.
3. **Real LLM agents will not have a clean two-valued answer space like the mock backend's.** The pipeline smoke test showed agreement_rate=1.0 in every cell — a mathematical certainty of the mock's binary output design (see `FINAL_RESEARCH_STATUS.md`/code comments), but real free-text answers fragment far more. The majority-vote/canonical-answer-key machinery in `src/quorum/admission.py` needs a real answer-canonicalization step (already present for GSM8K/SQuAD via the scorer functions) to be validated against actual model output diversity, which cannot happen without real execution.

**Author response:** (1) accepted; the ablation's status as "demonstrates the method, not a finding about real models" is stated in the script's own printed output and repeated in `FINAL_CLAIM_AUDIT.md` claim #21 — added an additional explicit caveat to `paper_v3_final.md`'s ablation section so it cannot be read in isolation. (2) accepted; added to Limitations in both `DATASET_FINALIZATION.md` and `paper_v3_final.md`. (3) accepted as a real, currently-untestable risk; flagged explicitly rather than asserted away — this is exactly the kind of thing that must be checked once real API access exists (added to the unblock checklist).

---

## Reviewer 3 — Statistical ML expert

**Assessment: Minor-to-major revision (statistics are correct but some choices need tightening).**

1. **The Cohen's-h power calculation and the Wilson-interval reporting method are, by the paper's own admission, different statistics used at different stages** (`POWER_ANALYSIS.md` §7 calls this out explicitly as "a standard and deliberate asymmetry"). This is defensible but should be justified with a citation to prior pre-registration practice recommending exactly this asymmetry (normal-approximation for a priori power, exact/robust interval for reporting), not just asserted as standard.
2. **The logistic regression in `hypothesis_tests.py` uses raw statsmodels `Logit` with no regularization and no check for complete/quasi-complete separation**, which is a realistic risk at N=350/cell when false-consensus rate can be near-zero in some cells (the smoke test showed 0% false-consensus in some low-correlation cells) — an unregularized MLE can fail to converge or blow up in that regime. This needs a documented fallback (e.g., Firth's penalized logistic regression) before being trusted on the real, sparser data.
3. **The Miller-Madow correction in `mutual_information_binary` is a reasonable default but is not the only or most robust choice** (e.g., a permutation-based null would be more robust at very small n); this is flagged as "exploratory diagnostic only" in `CORRELATION_MEASUREMENT.md`, which is the right call, but the code comment should say why Miller-Madow specifically was chosen over alternatives (it wasn't — this is a fair gap).
4. **Multiple comparisons**: the BH-FDR correction (`benjamini_hochberg` in `hypothesis_tests.py`) is implemented correctly (verified by inspection: standard step-up procedure) but is only wired into the pairwise-correlation-significance path, not automatically applied if a user later runs many exploratory cell-by-cell comparisons beyond the pre-registered primary test — a real risk of p-hacking by a future user of this code, not caught by the code itself.

**Author response:** (1) accepted; added a citing justification (standard pre-registration guidance: plan on a tractable approximation, report on the most accurate interval) to `POWER_ANALYSIS.md` §7. (2) accepted as a real, unaddressed risk — added a TODO and a warning docstring to `logistic_regression_false_consensus`; not fixed in this pass given scope, logged in `FINAL_RESEARCH_STATUS.md`'s unblock list as a required pre-execution fix, not deferred silently. (3) accepted; docstring updated to state Miller-Madow was chosen for simplicity/standardness, not demonstrated superiority, consistent with the "diagnostic only" framing. (4) accepted; a warning comment added to `configs/experiment_design.yaml`'s `statistics` block making explicit that any analysis beyond the pre-registered primary/secondary tests must apply BH-FDR or be labeled exploratory.

---

## Reviewer 4 — Dependable / Trustworthy AI expert

**Assessment: Accept the theory/methodology contribution in principle; empirical contribution not yet assessable.**

1. **The paper is unusually transparent about what is not done** — `FINAL_RESEARCH_STATUS.md` is a genuinely useful artifact that most papers in this space do not provide, and I'd encourage keeping something like it even after real results exist (as a "what changed since pre-registration" log).
2. **The null-result commitment (§10 of the gap-analysis document, carried into the manuscript's Discussion) is the right practice** and should be kept verbatim through to any real submission — reviewers in this area are increasingly skeptical of papers that only report confirming results.
3. **One real concern**: the paper's central real-world motivation (correlated semantic faults in deployed agentic systems) is not yet connected to any actual deployed-system failure data or case study — everything is either theory or synthetic validation. A single real, even small, case study (if accessible without API cost — e.g., a documented public incident involving correlated multi-agent failure) would substantially strengthen the motivation section, which currently rests entirely on citations to other papers' claims.
4. **The "Structural Epistemic Cut" reimplementation should be explicitly versioned** (e.g., `kappa_E_reimplementation_v1`) so that if DAQC's real algorithm is later obtained and differs, old results computed against the simplified version aren't silently conflated with new ones.

**Author response:** (1)-(2) noted with thanks, no action needed beyond keeping the documents as living artifacts. (3) accepted; noted as a genuine, currently-unaddressed weakness in `paper_v3_final.md`'s Limitations — a case-study addition is proposed as future work rather than fabricated now. (4) accepted; `src/structural/fault_basis.py`'s docstring is updated to note this is "v1, pairwise-intersection reimplementation" explicitly, and `FINAL_RESEARCH_STATUS.md`'s unblock list now includes versioning any future reimplementation.

---

## Reviewer 5 — Journal Editor

**Assessment: Desk-level guidance, not a review of content.**

This submission, as it stands, is not a completed empirical paper and should not be sent out for full external review as one — every technical reviewer above converges on the same top-line point (theory and methodology are solid; the empirical section is a pre-registration, not a result). Two realistic paths:

- **Path A (recommended given current state)**: submit as a registered report / methods paper (many dependability and ML-systems venues, e.g. a workshop track or a journal's "Methods" or "Registered Reports" section where one exists) covering Parts 1–7 of the current manuscript (novelty gate, theory, methodology, pre-registered design) with the Results/Discussion sections explicitly marked pending — several venues (this needs venue-specific verification before committing, not assumed here) accept and in-principle-accept such submissions before data collection, which matches this project's actual state honestly.
- **Path B**: hold submission until real execution (the unblock list in `FINAL_RESEARCH_STATUS.md`) produces actual results, then submit the completed empirical paper to a full research track.

Path A is procedurally honest about the current state; Path B produces a stronger paper eventually. I would not endorse submitting the current manuscript to a full empirical research track presented as a completed study — every reviewer above would independently flag the missing results as the top issue, and a paper flagged identically by 4 independent reviewers on the same point is not ready.

**Author response:** Accepted without qualification — this matches `FINAL_RESEARCH_STATUS.md`'s own conclusion, arrived at independently before this reviewer simulation was written. The journal-fit section of `paper_v3_final.md` is revised to present Path A as the near-term recommendation and Path B as the target once real execution is possible, rather than asserting a single confident journal target as the prior version of this project's documents did.
