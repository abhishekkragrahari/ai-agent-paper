# Structural vs. Provider-Basis Epistemic Independence in LLM-Agent Quorums

Research project: does DAQC-style structural (evidence-root) κ_E-safety leave LLM-agent quorums exposed to correlated false consensus via a second, named-but-untested basis (shared training lineage / "provider basis")?

**Start here:** `FINAL_RESEARCH_STATUS.md` — the single source of truth for what is proved, what is real, what is synthetic validation, and what is blocked. Then `paper_v3_final.md` for the manuscript.

## Document map

| File | What it is |
|---|---|
| `FINAL_RESEARCH_STATUS.md` | **Read first.** Status of every deliverable: completed / verified / blocked. |
| `FINAL_NOVELTY_GATE.md` | Literature audit against the 6 closest prior papers; the residual gap claim. |
| `CORRELATION_MEASUREMENT.md` | The phi-coefficient-based correlation measurement framework and its justification. |
| `FORMAL_RESULTS.md` | The proven theory (Lemma 1, Lemma 2, Theorem 1), symbolically and numerically verified. |
| `DATASET_FINALIZATION.md` | Real dataset acquisition (GSM8K, SQuAD 2.0) and the FEVER substitution, reported honestly. |
| `POWER_ANALYSIS.md` | Computed (not hand-estimated) sample-size requirements and pre-registered statistics. |
| `paper_v3_final.md` | The current manuscript. States plainly that the Results section is pending real execution. |
| `REVIEWER_REPORTS.md` | Five simulated reviews (4 technical + editor) and author responses. |
| `FINAL_CLAIM_AUDIT.md` | Every substantive claim, classified (fact / prior-work / theorem / experimental result / hypothesis). |
| `paper.md`, `gap_analysis_and_manuscript_v2.md`, `paper_v2_draft.md` | Earlier drafts in this project's history, kept (not deleted) because this project's own rules require reporting corrections rather than silently rewriting — see `gap_analysis_and_manuscript_v2.md` Part A.3 for a documented, load-bearing correction. |

## Code

```
src/
  agents/       Agent, TaskItem, Backend interface; CorrelatedMockBackend (synthetic,
                validation-only); AnthropicBackend/OpenAIBackend (real, genuinely
                implemented, unexercised -- no API keys in this environment)
  structural/   kappa_E-safety reimplementation (from DAQC's published description)
  quorum/       Majority-vote aggregation, false-consensus detection
  correlation/  phi coefficient (primary), co-error probability, Jaccard, mutual
                information (diagnostic), bootstrap CI
  metrics/      false_consensus_rate, semantic_accuracy, agreement_rate, real
                GSM8K/SQuAD2 scorers
  statistics/   power analysis, two-proportion test, logistic regression, BH-FDR
experiments/    run_harness_validation.py, run_factorial_experiment.py,
                run_statistical_analysis.py, run_ablations.py
configs/        experiment_design.yaml -- the pre-registered design
datasets/       REAL downloaded data: gsm8k/test.jsonl (1,319 items, MIT),
                squad2/dev-v2.0.json (11,873 questions, CC BY-SA 4.0)
results/        Output of running the code above -- see the label below
research/       verify_formal_results.py (math verification), generate_figures.py
scripts/        validate_pipeline.sh -- runs everything below end-to-end
```

## Running it

```bash
pip install -r requirements.txt
bash scripts/validate_pipeline.sh
```

This runs: formal-math verification, a harness sanity check (positive/negative control against a known planted correlation), a factorial pipeline smoke test, statistical analysis, and ablations — all on a synthetic mock backend, because **no LLM API credentials are available in this environment** (verified; see `FINAL_RESEARCH_STATUS.md`).

To run the real, pre-registered experiment once credentials exist:

```bash
export ANTHROPIC_API_KEY=...   # and/or OPENAI_API_KEY, etc.
python3 experiments/run_factorial_experiment.py --backend anthropic --tasks-per-cell 350 --seeds 3
```

## The one rule that matters most here

**Every file `results/` produces carries a `DATA_LABEL` column or an explicit banner saying whether it is `"SYNTHETIC VALIDATION DATA -- NOT RESEARCH RESULTS"` or real.** As of this commit, every single results file is synthetic. Do not cite any number from `results/` as a finding about real LLM-agent behavior until that label says otherwise.
