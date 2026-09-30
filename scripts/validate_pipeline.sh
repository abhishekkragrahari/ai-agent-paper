#!/usr/bin/env bash
# Runs every validation step this project currently supports, in order.
# Exits non-zero if any step fails. This is software validation (mock/
# synthetic data + proven math) -- it does NOT run any real experiment
# (no LLM API keys are required or used by this script).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1/5: Formal math verification (symbolic + numeric) =="
python3 research/verify_formal_results.py

echo
echo "== 2/5: Harness sanity check (positive/negative control) =="
python3 experiments/run_harness_validation.py

echo
echo "== 3/5: Factorial pipeline smoke test (mock backend, reduced N) =="
python3 experiments/run_factorial_experiment.py --backend mock --tasks-per-cell 30 --seeds 2

echo
echo "== 4/5: Statistical analysis + correlation matrix generation =="
python3 experiments/run_statistical_analysis.py

echo
echo "== 5/5: Ablation studies =="
python3 experiments/run_ablations.py

echo
echo "== Generating figures =="
python3 research/generate_figures.py

echo
echo "ALL VALIDATION STEPS PASSED."
echo "Reminder: this validates the SOFTWARE PIPELINE against proven math and"
echo "synthetic data with known ground truth. It produces NO findings about"
echo "real LLM-agent behavior. See FINAL_RESEARCH_STATUS.md."
