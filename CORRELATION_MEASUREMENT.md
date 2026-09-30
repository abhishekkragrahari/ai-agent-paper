# CORRELATION_MEASUREMENT.md

## 1. Purpose

This framework replaces the provider-label proxy ("same model family ⇒ correlated," "different provider ⇒ independent") with measured, continuous pairwise correlation between agents' errors. Provider identity is retained only as one candidate *predictor* of measured correlation — to be tested, not assumed (Phase 11.4's required ablation).

## 2. Candidate measures

Let E_i, E_j ∈ {0,1} be binary error indicators for agents i, j on the same task (1 = output fails the ground-truth predicate g(t)), observed over a set of m shared tasks. Define the 2×2 contingency counts n₁₁ (both err), n₁₀ (i errs, j doesn't), n₀₁, n₀₀, with n = n₁₁+n₁₀+n₀₁+n₀₀ = m, and marginals n₁· = n₁₁+n₁₀ (i's error count), n·₁ = n₁₁+n₀₁ (j's error count).

| Measure | Formula | Range | What it captures |
|---|---|---|---|
| **Co-error probability** | P̂(E_i=1,E_j=1) = n₁₁/n | [0,1] | Raw joint error rate. Confounded by marginal rates — two high-error agents co-error often even if independent. |
| **Conditional co-error probability** | P̂(E_j=1 \| E_i=1) = n₁₁/n₁· | [0,1] | Absolute risk: "given i erred, how often did j." Directly interpretable, appears directly in the false-consensus derivation (§5), but asymmetric (P(j\|i) ≠ P(i\|j) in general) and still marginal-rate-confounded. |
| **Agreement-on-error rate (Jaccard)** | n₁₁/(n₁₁+n₁₀+n₀₁) | [0,1] | Overlap of error sets, ignoring joint non-errors (n₀₀). Useful when marginal error rates differ sharply between agents (avoids the "denominator dominated by n₀₀" issue phi has under rare, very unequal marginals). |
| **Phi coefficient (φ)** | (n₁₁n₀₀ − n₁₀n₀₁) / √(n₁·n₀·n·₁n·₀) | [−1,1] | Pearson correlation of two binary variables. The unique measure here that (a) is signed, (b) is normalized against both marginals, (c) equals zero exactly under independence, (d) is the same ρ that parametrizes the Beta-Binomial model in `FORMAL_RESULTS.md`. |
| **Mutual information (MI)** | I(E_i;E_j) = Σ p(x,y) log[p(x,y)/(p(x)p(y))] | [0, min(H(E_i),H(E_j))] | Detects any dependence, including non-monotonic/nonlinear. Unsigned (cannot distinguish positive from negative correlation) and, for sparse contingency tables (rare joint errors — the expected regime, since well-designed tasks should have low per-agent error rates), the plug-in MI estimator is known to be biased upward without correction (Miller–Madow or similar), inflating apparent dependence at small sample sizes. |

## 3. Primary measure: the phi coefficient

**Selection criterion and justification.**

1. **Direct correspondence to the theoretical model.** `FORMAL_RESULTS.md` derives a false-consensus bound in terms of a correlation parameter ρ from a Beta-mixture model, where ρ is by construction the intraclass correlation of the underlying Bernoulli variables. For a **pair** of agents, the phi coefficient is the sample Pearson correlation of their binary error indicators — the direct empirical estimator of exactly this parameter, not a related-but-different quantity. Using φ as the primary measure means the measurement layer and the theory layer share one consistent notion of "correlation," rather than requiring an ad hoc mapping between (e.g.) mutual information and a Beta-Binomial ρ.
2. **Signed and independence-centered.** φ = 0 exactly under independence, φ > 0 for positive (correlation-increasing, false-consensus-increasing) dependence, φ < 0 for negative (error-canceling) dependence — the sign is scientifically meaningful here (RQ1 is specifically about *positive* correlation raising false-consensus risk; a measure that cannot express sign cannot test the directional hypothesis).
3. **Known sampling distribution and significance test.** n·φ² is asymptotically the Pearson chi-square statistic for the 2×2 table (1 degree of freedom), and Fisher's exact test is available for small/sparse tables — both standard, off-the-shelf, and already implemented in `scipy.stats` (`scipy.stats.contingency.association` with `method="phi"`; chi-square and Fisher exact via `scipy.stats.chi2_contingency` / `scipy.stats.fisher_exact`). This gives φ a ready-made hypothesis-testing and confidence-interval apparatus (bootstrap CI as a robustness check, since the asymptotic chi-square approximation can be poor for small or sparse tables — flagged explicitly as a required check, not assumed valid).
4. **Lower estimation burden than MI under the expected data regime.** If per-agent error rates are low (the desirable, designed-for case — most tasks should be answerable correctly by a competent agent), joint-error cells are sparse, and plug-in MI estimation is known to be biased and high-variance under sparsity unless bias-corrected; φ, built from simple marginal/joint counts, degrades more gracefully and its estimator's bias is well characterized (a small-sample correction, e.g., using n−1 in the denominator or a continuity correction for Fisher's exact test, is a minor, well-understood adjustment rather than a nonstandard estimator).

**Decision: φ is the primary measure used for the main hypothesis test (H1) and the correlation term reported in all headline results. It is not claimed to be the uniquely correct measure — it is the one selected on the stated, falsifiable grounds above, and the selection itself is subject to the ablation in §4.**

## 4. Secondary / diagnostic measures — retained, not discarded

- **Conditional co-error probability** is reported alongside φ in every results table because it is the quantity a practitioner actually cares about operationally ("if one agent is wrong, how worried should I be about the others") even though it is not the primary inferential measure.
- **Co-error probability** (raw) is retained as an input to all other measures and reported for transparency.
- **Agreement-on-error / Jaccard** is retained specifically as a robustness check when per-agent error rates differ substantially between agent pairs (e.g., comparing a strong and a weak model), where φ's normalization can behave counterintuitively at extreme, unequal marginals.
- **Mutual information** is retained as an *exploratory, nonlinearity-detection diagnostic only* (required ablation, Phase 11), computed with an explicit bias-correction method (Miller–Madow, or a permutation-based null to establish significance) — precisely because of the sparsity concern in §3.4 — and used to check whether φ misses any dependence structure it is not designed to capture (e.g., a U-shaped relationship between two agents' confidence-conditioned error patterns). If MI and φ diverge substantially in ranking agent pairs by dependence strength, that divergence is itself reported as a finding, not suppressed.

## 5. Estimators, confidence intervals, and significance

For a pair (i,j) observed over m shared tasks:
- Point estimate: φ̂ from the 2×2 table.
- CI: **bootstrap** (resample tasks with replacement, B≥2000 resamples, percentile or BCa interval) as the primary CI method, because the chi-square-based asymptotic CI for φ is unreliable when n₁₁ is small (expected under low per-agent error rates) — this is decided in advance, not chosen post hoc based on which method gives a narrower interval.
- Significance test for H0: φ=0 — Fisher's exact test on the 2×2 table (exact, valid at any cell count, preferred over chi-square when any expected cell count <5, which is the likely regime here).
- **Multiple comparisons:** when correlation is estimated for every pairwise combination within a quorum of size n (C(n,2) pairs) and aggregated to a quorum-level correlation summary (e.g., mean pairwise φ), a Benjamini–Hochberg FDR correction is applied across the pairwise tests before any pair-level significance claim is made; the quorum-level aggregate statistic used in the main hypothesis test (H1) does not require this correction since it is a single pre-registered test, not C(n,2) separate tests (see `POWER_ANALYSIS.md`).

## 6. Quorum-level aggregation

The theory in `FORMAL_RESULTS.md` is parametrized by a single exchangeable ρ across all n agents in a quorum (the Beta-mixture/common-cause model). The empirical estimate used to instantiate ρ for a given quorum is the **mean pairwise φ̂ across all C(n,2) pairs** in that quorum. This is an approximation (the true dependence structure need not be exchangeable across all pairs), and the pipeline additionally reports the **range** (min/max pairwise φ̂) and flags quorums where pairwise φ̂ values are highly heterogeneous (e.g., interquartile range exceeding a pre-registered threshold) as cases where the exchangeable-model approximation should be treated with more caution — this diagnostic is run automatically by `src/statistics/hypothesis_tests.py` (see code) and reported alongside every quorum-level result, not hidden.

## 7. Behavioral similarity on a calibration set as a predictor — hypothesis, not fact

**Proposal (to be tested, not assumed true):** compute a Behavioral Similarity Score BSS(a_i, a_j) as the same φ̂ (or agreement rate) computed on a **held-out calibration task set**, disjoint from the evaluation task set used for the main experiment. The practical question this targets: can a cheap, one-time calibration-set measurement stand in for an expensive, repeated full-evaluation-set correlation measurement, by predicting held-out φ̂?

**Planned test (pending real data, specified now so it is not improvised post hoc):** simple linear regression of evaluation-set φ̂ on calibration-set BSS across all agent pairs, reporting R² and a held-out (cross-validated) prediction error, plus the trivial baseline (predicting evaluation-set φ̂ from the provider-label alone, i.e., a binary same/different-provider indicator) for direct comparison — this is exactly the "measured correlation vs. provider label" ablation (Phase 11.4), applied one level up (does *calibration-measured* correlation predict *evaluation-measured* correlation better than the provider label does).

**Status: hypothesis. No claim is made here that BSS is predictive — only that it is a well-specified, falsifiable thing to test once real pairwise error data exists.**

## 8. What this document does not do

It does not report any correlation value for any real agent pair — no experiment has been run. It specifies estimators, their justification, and their pre-registered use, so that when real data is collected (or if a future session has API access), the analysis is not chosen after seeing results.
