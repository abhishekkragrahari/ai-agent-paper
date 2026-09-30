# POWER_ANALYSIS.md

All numbers below were computed with `statsmodels.stats.power` / `statsmodels.stats.proportion` (code in `research/power_analysis.py`), not estimated by hand. This is completed **before** any experiment, per the pre-registration requirement, and the sample sizes below are binding on the experimental design in `configs/experiment_design.yaml` — the design was sized to this analysis, not the other way around.

## 1. Primary hypothesis and endpoint (pre-registered)

**Primary hypothesis (H1):** Among κ_E-safe (structurally independent) quorums, quorum-level false-consensus rate is higher under a high measured mean-pairwise-φ condition than under a low measured mean-pairwise-φ condition.

**Primary endpoint:** false-consensus rate — a binary per-task indicator (1 = quorum majority output fails g(t), 0 = otherwise), aggregated as a proportion within each condition.

**Primary statistical test:** two-proportion z-test (Cohen's h effect size), comparing false-consensus rate between the low-correlation and high-correlation condition within the κ_E-safe stratum, at α=0.05 two-sided. This is deliberately the simplest, most conservative pre-registered test; the manuscript's **reported effect model** is a logistic regression of the binary false-consensus outcome on continuous measured φ (plus domain and quorum size as covariates), which uses more information and is expected to have higher effective power per task than the two-proportion test — the two-proportion test sets a floor, not a ceiling, on required N.

## 2. Effect-size anchor and its status

No real effect size exists yet. To avoid picking an arbitrary N, the anchor effect size is taken directly from the model-exact numbers computed and verified in `FORMAL_RESULTS.md` (§6): at p=0.10, n=5, q=3 (majority), the model predicts false-consensus rate 0.0294 at ρ=0.1 ("low") versus 0.0842 at ρ=0.5 ("high"). **This is a theory-derived planning anchor, not an empirical estimate of the real effect** — it is used only to size the study, and is explicitly flagged as revisable once the harness-sanity-check step (§4 of `FINAL_RESEARCH_STATUS.md`) produces any real pilot data.

Computed (via `proportion_effectsize`): Cohen's h = 0.2446 for the low-vs-high (ρ=0.1 vs ρ=0.5) contrast at n=5.

## 3. Sample size requirements (computed)

| Contrast | Cohen's h | N per group, power=0.80, α=0.05 | N per group, power=0.90, α=0.05 |
|---|---|---|---|
| Low (ρ=0.1) vs. High (ρ=0.5), n=5, q=3 | 0.2446 | **263** | 351 |
| Low (ρ=0.1) vs. Medium (ρ=0.3), n=5, q=3 | 0.1657 | 572 | 765 |
| Low (ρ=0.1) vs. High (ρ=0.5), n=3, q=2 | 0.1654 | 574 | 768 |

With Bonferroni correction for the 3 planned pairwise correlation-level contrasts (α_adj = 0.05/3 = 0.0167): low-vs-high (n=5) requires **350** per group at power 0.80; low-vs-medium requires 762.

**Decision:** the primary pre-registered test (low-vs-high, κ_E-safe, pooled across domain and both quorum sizes) is powered at **N=350 tasks per correlation-level group** (power ≥0.80 even after Bonferroni correction for the 3 planned contrasts). The medium-correlation and dose-response (continuous φ) analyses are pre-registered as secondary/exploratory and are not guaranteed to be adequately powered at this N — this is stated now, not discovered after a null result.

## 4. Task-pool size vs. required N — a clarification that changes the feasibility picture

The design in `gap_analysis_and_manuscript_v2.md` (Part F) is a **crossed factorial**: each task can be run under every design cell (the same GSM8K/FEVER item, re-posed to differently-configured quorums), not a between-items split requiring disjoint item subsets per condition. This means the binding constraint is **not** dataset size (GSM8K's 1,319-item test pool is far larger than any single-cell N requirement) but **total API call volume**, computed next.

## 5. Full design sizing and API call budget (for when execution is possible)

Design: 2 (structural: κ_E-unsafe / κ_E-safe) × 3 (correlation level: low/medium/high, realized via agent-pool composition) × 2 (quorum size: n=3, n=5) × 2 (domain: GSM8K, FEVER) = 24 cells.

Recommended subsample size per cell to meet the §3 power requirement for the primary contrast while bounding cost: **N=350 tasks per cell** (meeting the Bonferroni-adjusted power-0.80 requirement for the primary low-vs-high contrast; medium-correlation cells inherit this same N and are explicitly underpowered for their own pairwise contrast per §3 — flagged, not hidden), × **3 seeds/repetitions per task** (temperature/sampling variation, not full determinism) × n agents per quorum.

Total agent-level API calls ≈ Σ over cells of (350 tasks × 3 seeds × n_cell):
- n=3 cells (12 of the 24): 350 × 3 × 3 = 3,150 calls/cell × 12 = 37,800
- n=5 cells (12 of the 24): 350 × 3 × 5 = 5,250 calls/cell × 12 = 63,000
- **Total ≈ 100,800 agent-level LLM API calls**, plus a smaller number of admission-controller/κ_E-check evaluations (non-LLM, cheap) and any retrieval-tool calls for FEVER's shared-evidence condition.

This is reported so that, when API access is available, the user can decide whether to fund the full design or reduce it (e.g., drop the medium-correlation cells, or reduce quorum-size levels to n=5 only) — a reduction menu is given in `FINAL_RESEARCH_STATUS.md` rather than silently shrinking the design here.

## 6. Repetitions/seeds

3 seeds per task-cell is the minimum for reporting a bootstrap CI with non-degenerate resampling (per `CORRELATION_MEASUREMENT.md` §5's bootstrap CI requirement) and is **not** a claim of capturing full LLM sampling variance — a sensitivity check with 5 seeds on a 10% subsample is specified as a required robustness check before trusting 3-seed headline numbers.

## 7. Confidence intervals and effect-size reporting (pre-registered, not post hoc)

- False-consensus rate per condition: Wilson score interval (more reliable than the normal-approximation interval at the proportions expected here, which are in the 0.01–0.10 range — a regime where the normal approximation used for the a priori power calculation itself is known to be imperfect at the boundary, which is why the Wilson interval, not the normal interval, is used for **reporting**, while the normal-approximation Cohen's-h calculation above is used only for **planning**, a standard and deliberate asymmetry between planning and reporting statistics).
- Primary contrast: risk difference and risk ratio, each with a bootstrap CI (2,000 resamples), alongside the z-test p-value — per the non-negotiable rule against relying on p-values alone.
- Logistic regression (secondary/main effect-size model): coefficient on φ reported as an odds ratio with a Wald CI, plus a likelihood-ratio test against the covariate-only (domain + quorum size, no φ) model.

## 8. What this document does not do

It does not report a power analysis result *from real data* — no data exists. It fixes, in advance, the primary test, effect-size anchor (explicitly labeled as theory-derived, not empirical), required N, and reporting statistics, so none of these are chosen after seeing outcomes.
