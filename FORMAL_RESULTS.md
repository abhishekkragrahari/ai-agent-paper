# FORMAL_RESULTS.md

All derivations below were checked two ways: symbolically (SymPy, exact algebraic simplification to zero-difference) and numerically (SciPy, exact Beta-Binomial CDF evaluation). Transcripts of both checks are reproducible via `research/verify_formal_results.py` (added to the repo). Nothing in this document is asserted without either a closed-form proof or a numerically-verified exact computation under a stated model; the distinction between the two is marked explicitly throughout.

## 1. Why this supersedes the earlier "Proposition 1"

The reviewer-simulated objection in `gap_analysis_and_manuscript_v2.md` (Part K) was correct: the earlier Proposition 1 was close to a restatement of κ_E's own definition — it said, informally, "structural independence doesn't bound non-structural correlation," which is true by construction and not a result. This document replaces it with a genuine quantitative model relating individual error rate, pairwise correlation, quorum size, and threshold to false-consensus probability, and a proven, non-trivial bound — the "non-trivial upper/lower bound" option, since the assumptions available do not support a clean exact theorem about an unknown real-world ρ (only about the *model's* behavior given ρ).

## 2. Model: common-cause (Beta-mixture) correlated Bernoulli errors

**Setup.** For a task t, let each of n quorum agents produce a binary error indicator E_i ∈ {0,1} (1 = the agent's output fails the ground-truth predicate g(t)). We model exchangeable positive correlation among {E_i} via a latent common-cause (Beta-mixture) construction, one of the three model families suggested for consideration and the one best matched to the substantive hypothesis under test — that agents share an unobserved, task-specific propensity to err (a "shared blind spot," whether structurally or parametrically induced):

- A latent task-level propensity Θ ~ Beta(α, β).
- Conditional on Θ = θ, E_1, ..., E_n are i.i.d. Bernoulli(θ).
- K = Σ E_i is then marginally **Beta-Binomial(n, α, β)**.

This is a standard model for overdispersed/clustered binary data, in use since Skellam (1948) for exactly this purpose (a shared latent cause inflating the variance of a count beyond the independent-Binomial case); it is not a model invented for this paper.

**Reparametrization.** Let p = α/(α+β) (marginal per-agent error rate) and ρ = 1/(α+β+1) (the model's intraclass correlation / overdispersion parameter — the standard reparametrization for this family, confirmed against independent literature). Then α = p(1-ρ)/ρ, β = (1-p)(1-ρ)/ρ for ρ ∈ (0,1); ρ→0 recovers independent Binomial(n,p); ρ→1 concentrates all agents on the same outcome (K=n w.p. p, K=0 w.p. 1-p).

**Why this model, and not the alternatives the process asked to consider:**
- *General exchangeable correlated Bernoulli* (specifying only pairwise correlations without a generative mechanism) is strictly more general but has no single natural n-agent joint distribution without additional constraints, and does not connect cleanly to a "shared cause" story.
- *Latent common-cause models* are what this **is** — the Beta-mixture is the simplest, most standard instance (single continuous latent factor, conjugate, closed form).
- A general copula-based model would allow more flexible dependence structure but at the cost of an extra, unjustified modeling choice (copula family) with no data yet to fit it to; premature given no experiment has been run.

This is a modeling **choice**, stated as such, not a proven-necessary representation of reality. Its main empirical claim — that observed agent errors are well-approximated by a single shared latent factor — is itself testable once real data exists (e.g., via a likelihood-ratio test against a two-latent-factor extension; noted as future work in §6).

## 3. Lemma 1 (mean invariance) — proven exactly

**Statement.** E[K] = np for all ρ ∈ [0,1).

**Proof.** E[K] = E[E[K|Θ]] = E[nΘ] = n·E[Θ] = n·α/(α+β) = np, by construction of the reparametrization. ∎

**Numerical confirmation.** For n=5, p=0.10: E[K] computed exactly via `scipy.stats.betabinom.mean` equals 0.5000 for ρ ∈ {0.01, 0.3, 0.7, 0.95} — invariant to machine precision, as the proof requires.

*Consequence:* correlation does not change the expected number of erring agents. It only changes how errors are distributed across draws — which is exactly the quantity that matters for a majority-threshold quorum.

## 4. Lemma 2 (variance inflation) — proven exactly

**Statement.** Var(K) = n·p(1-p)·[1 + (n-1)ρ].

**Proof.** By the law of total variance, Var(K) = E[Var(K|Θ)] + Var(E[K|Θ]). Given Θ, K is Binomial(n,Θ), so Var(K|Θ) = nΘ(1-Θ), giving E[Var(K|Θ)] = n·E[Θ] − n·E[Θ²] = n·p − n·(Var(Θ)+p²). For Θ~Beta(α,β), Var(Θ) = αβ/[(α+β)²(α+β+1)], which under the reparametrization simplifies exactly to p(1-p)ρ (verified symbolically, difference from claimed closed form = 0). Substituting: E[Var(K|Θ)] = np(1-p)(1-ρ). Also Var(E[K|Θ]) = Var(nΘ) = n²·Var(Θ) = n²p(1-p)ρ. Summing: Var(K) = np(1-p)(1-ρ) + n²p(1-p)ρ = np(1-p)[1+(n-1)ρ]. ∎

**Symbolic + numerical confirmation.** SymPy simplification of (derived expression) − (claimed closed form) = 0 exactly. `scipy.stats.betabinom.var` matches the closed form to machine precision (max absolute difference 6.7×10⁻¹⁶) across tested ρ ∈ {0.01,0.3,0.7,0.95}, n=5, p=0.1.

This is the standard "design effect" / variance-inflation-factor result for clustered binary data (consistent with the independently-verified literature summary obtained via search — the same ρ=1/(α+β+1) and 1+(n-1)ρ forms appear in the clustered-binary-data statistics literature, not invented for this document).

## 5. Theorem 1 (Correlation-Sensitive False-Consensus Bound) — proven

**Statement.** Let K ~ Beta-Binomial(n, α, β) under the model of §2, with mean np and variance V(ρ) = np(1-p)[1+(n-1)ρ] (Lemma 2). Let q be a quorum decision threshold (e.g., majority, q = ⌈(n+1)/2⌉) with q > np. Then:

P(K ≥ q) ≤ V(ρ) / [V(ρ) + (q − np)²]

and this bound is **strictly increasing in ρ** for fixed n, p, q (n > 1, p ∈ (0,1)).

**Proof.** The bound itself is Cantelli's inequality (the one-sided Chebyshev inequality), a standard, citable result applying to any random variable with finite mean and variance: for a random variable X with mean μ and variance V, and any d > 0, P(X − μ ≥ d) ≤ V/(V+d²). Apply with X=K, μ=np, d=q−np>0.

Monotonicity: V(ρ) is affine and strictly increasing in ρ for n>1 (coefficient np(1-p)(n-1) > 0 given p∈(0,1)). The map f(V) = V/(V+c) for fixed c=(q-np)²>0 has derivative f'(V) = c/(V+c)² > 0, so f is strictly increasing in V. By the chain rule, the bound is strictly increasing in ρ. (Symbolically verified: d(bound)/dρ simplifies to a ratio whose sign is determined by −n·p·(n−1)·(p−1)·(np−q)² in the numerator over a squared — hence non-negative — denominator; since (p−1)<0, n,p,(n-1)>0, and the squared term ≥0, the full numerator is ≥0, confirmed ≈0.215 > 0 at a representative parameter point n=5,p=0.1,ρ=0.3,q=3.) ∎

**Validity check (numerical).** Across 18 tested (n,q,ρ) combinations (n∈{3,5,7} at majority threshold, ρ from 0.01 to 0.9, p=0.10), the exact Beta-Binomial tail probability never exceeded the Cantelli bound — consistent with (not an independent proof of, but a non-falsification of) the inequality.

**What this theorem does and does not say.** It is a **model-conditional, correlation-agnostic-to-source** bound: it holds for *any* ρ, regardless of whether that correlation originates from a structural (shared evidence/tool/telemetry) cause or a non-structural (shared training lineage) cause, or any other latent common cause. It does not, by itself, prove anything about κ_E-safety or DAQC — that connection is the corollary below, which is a logical inference, not a new probabilistic claim.

**Corollary (interpretive, not a new theorem).** DAQC's own construction defines κ_E-safety as eliminating correlation attributable to shared *modeled fault-basis roots* (structural/evidence-root causes) — this is DAQC's result, re-used here, not re-derived. If a quorum is κ_E-safe by that criterion and a researcher nonetheless *measures* a positive ρ̂ among its agents' errors (via the estimators in `CORRELATION_MEASUREMENT.md`), then by elimination that residual ρ̂ cannot be attributed to the cut basis, and Theorem 1 applies to it exactly as it would to any other ρ — i.e., κ_E-safety does not exempt a quorum from the false-consensus inflation the theorem describes if residual correlation is measured. This reframes the earlier Proposition 1 as a consequence of (a) DAQC's own definition (not re-proven here) plus (b) Theorem 1 (proven here) — rather than as a standalone assumption-laden claim.

## 6. Worked numerical illustration (exact computation under the model — NOT empirical data)

**This table is a mathematical illustration of the model in §2, computed exactly via `scipy.stats.betabinom`. It uses an assumed, illustrative per-agent error rate (p=0.10) and a range of ρ values chosen to span the unit interval. It is not — and must never be cited as — a measurement of any real LLM-agent system.**

P(false consensus) = P(K ≥ majority threshold), p = 0.10:

| n | q (majority) | ρ=0 (independent) | ρ=0.1 | ρ=0.3 | ρ=0.5 | ρ=0.7 | ρ=0.9 |
|---|---|---|---|---|---|---|---|
| 3 | 2 | 0.0280 | 0.0470 | 0.0729 | 0.0880 | 0.0962 | 0.0996 |
| 5 | 3 | 0.0086 | 0.0294 | 0.0636 | 0.0842 | 0.0951 | 0.0995 |
| 7 | 4 | 0.0027 | 0.0212 | 0.0590 | 0.0824 | 0.0946 | 0.0995 |

**Two qualitative observations this exact computation supports** (mathematical facts about this model, stated as such — not claims about real systems until tested):

1. At fixed p, false-consensus probability rises sharply with ρ — roughly 3–8× from ρ=0 to ρ=0.3 across the tested (n,q) pairs, and approaches p itself as ρ→1 (matching the ρ→1 degenerate case derived analytically: K=n w.p. p).
2. **Increasing quorum size n is an effective mitigation only at low ρ.** At ρ=0, going from n=3 to n=7 cuts false-consensus probability by >10× (0.028→0.0027, the expected Chernoff-type decay classical BFT/quorum scaling relies on). At ρ=0.9, the same increase in n changes false-consensus probability by less than 0.1 percentage points (0.0996→0.0995) — quorum-size scaling has **essentially stopped working** as a mitigation once correlation is high. This is the model's formal account of why "just add more agents" (the structural remedy classical quorum systems rely on) is not expected to rescue a quorum from a highly-correlated error source, and is the direct formal counterpart to RQ2 in `gap_analysis_and_manuscript_v2.md` Part F — to be tested against real data, not assumed confirmed by this derivation.

## 7. What remains open (explicitly not claimed here)

- The model of §2 (single shared latent factor) is a simplifying choice. A more realistic model might posit **two** latent factors (a structural one, cut by κ_E, and a provider/parametric one, not cut by κ_E) — this two-factor extension is mathematically straightforward (a mixture of two independent Beta-mixtures) but is not derived here because it would require a decomposition assumption (how much of the total variance each factor contributes) that cannot currently be justified from data. This is flagged as future formal work, contingent on the correlation-measurement results in `CORRELATION_MEASUREMENT.md` being collected.
- Theorem 1 is a bound, not an exact tail formula — the exact Beta-Binomial tail (used to produce §6's table) is available in closed form via the incomplete Beta function and should be preferred over the Cantelli bound wherever the model's distributional assumption is trusted; the bound's value is that it is model-light (only mean/variance) and extends, with the same proof, to any distribution with the same mean/variance, not only the Beta-Binomial.
- No claim is made that real LLM-agent errors follow the Beta-Binomial model exactly — this must be checked empirically once real pairwise error data exists (a goodness-of-fit test, e.g., comparing observed K-count histograms against the fitted Beta-Binomial, is specified as a required diagnostic in the experimental pipeline, not assumed to pass).
