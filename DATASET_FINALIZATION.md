# DATASET_FINALIZATION.md

Two datasets are finalized (not left as candidates), chosen to give two objective-ground-truth domains (Phase 9's minimum). **Both were actually downloaded and verified in this session** (not just cited) — see §3 for a real, executed dataset-acquisition substitution that happened along the way and is reported here rather than silently corrected.

## Dataset 1 — GSM8K (reasoning / objective numeric ground truth) — ACQUIRED, VERIFIED

| Field | Value |
|---|---|
| Exact name | GSM8K ("Grade School Math 8K") |
| Citation | Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., Schulman, J. "Training Verifiers to Solve Math Word Problems." arXiv:2110.14168, 2021. |
| Source (actually used) | `https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl` — downloaded directly in this session (huggingface.co, the more commonly cited mirror, is blocked by this environment's network policy — see §3) |
| License | MIT — **confirmed by directly fetching and reading the repository's own `LICENSE` file** (`datasets/gsm8k/LICENSE`), not by secondary citation |
| Size | **1,319 lines, counted directly from the downloaded file** (`wc -l datasets/gsm8k/test.jsonl` = 1319), matching the previously search-verified figure independently |
| File location in repo | `datasets/gsm8k/test.jsonl` (real data, committed) |
| Scoring procedure | Each problem's reference solution ends in `#### <number>`. g(t) is exact-match on the extracted final numeral after normalization (strip `,`, whitespace). Implemented and unit-tested in `src/metrics/gsm8k_scoring.py` against the real downloaded file (see `research/verify_dataset_loaders.py`). Fully objective — no LLM-judge required. |
| Why appropriate | Multi-step reasoning task (tests RQ4); item pool far exceeds the per-cell N required by `POWER_ANALYSIS.md`; exact-match scoring avoids a correlated-grader confound. |

## Dataset 2 — SQuAD 2.0 dev set (reading-comprehension / extractive QA, objective span ground truth) — ACQUIRED, VERIFIED

**This replaces FEVER, which was the original selection in the prior version of this document but could not be downloaded in this environment — see §3 for why, reported honestly rather than silently swapped.**

| Field | Value |
|---|---|
| Exact name | SQuAD 2.0 (Stanford Question Answering Dataset, version 2.0), dev split |
| Citation | Rajpurkar, P., Jia, R., Liang, P. "Know What You Don't Know: Unanswerable Questions for SQuAD." Proceedings of ACL 2018. arXiv:1806.03822. (Builds on the original SQuAD: Rajpurkar, P., Zhang, J., Lopyrev, K., Liang, P. "SQuAD: 100,000+ Questions for Machine Comprehension of Text." EMNLP 2016.) |
| Source (actually used) | `https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v2.0.json` — downloaded directly in this session |
| License | CC BY-SA 4.0 (verified via search of the dataset's official pages) |
| Size | **11,873 questions across 35 Wikipedia articles, of which 5,945 are deliberately unanswerable — counted directly from the downloaded file** (`datasets/squad2/dev-v2.0.json`), matching the well-known published statistics for this exact split, an independent cross-check that the correct file was obtained |
| File location in repo | `datasets/squad2/dev-v2.0.json` (real data, committed) |
| Scoring procedure | Standard SQuAD exact-match / token-F1 against the gold answer span(s) (for answerable questions) or correct abstention (for the 5,945 `is_impossible` questions) — the dataset's own established scoring convention, not invented here. Objective; no LLM-judge required. |
| Why appropriate | A second, genuinely different objective-ground-truth domain (extractive reading comprehension vs. GSM8K's multi-step arithmetic reasoning) satisfying Phase 9's two-domain minimum; includes a built-in "know what you don't know" abstention dimension, which is a relevant, realistic error mode for agent quorums (false consensus on a *confident wrong extraction* vs. on a *failure to recognize unanswerability* are arguably different semantic-fault subtypes — noted as a possible future stratification, not used as a factor in the current pre-registered design). |

## 3. What actually happened with FEVER — reported, not hidden

FEVER (Thorne et al., 2018) was the originally selected Dataset 2 for comparability with H-CSC's claim-verification framing. On attempting to actually acquire it in this session:

- `fever.ai` (the dataset's only real download host) returned a network-policy block (`CONNECT tunnel failed, response 403`), the same organizational policy that blocks `arxiv.org` and `huggingface.co`.
- A GitHub mirror of the FEVER *code* (`awslabs/fever`) is reachable, but its own README directs data download to `fever.ai` — the actual claim/evidence files are not hosted on GitHub directly, so this did not provide a usable substitute.
- Several other candidate datasets were probed for GitHub-hosted reachability before settling on SQuAD 2.0: `google-research-datasets/boolean-questions` (BoolQ) returned HTTP 200 on the repo but was not further pursued once SQuAD 2.0's download succeeded and its objective span/abstention scoring was judged preferable to BoolQ's binary yes/no format for testing the reasoning-vs-extraction domain contrast.

**Consequence for comparability to H-CSC:** the explicit goal of matching H-CSC's claim-verification task *style* is only partially met by SQuAD 2.0 (extractive QA, not 3-way claim classification). This is a real reduction in comparability to the closest prior systems paper, caused by an environment constraint, not a scientific judgment that SQuAD 2.0 is preferable — stated plainly so it is not mistaken for the latter. If a future session has unblocked access to `fever.ai`, re-running Dataset 2 as FEVER rather than SQuAD 2.0 is a direct, low-effort substitution (the loader interface in `src/agents/base.py`'s `TaskItem` is dataset-agnostic) and is recommended before final submission.

## Datasets considered and rejected

- **TruthfulQA**: rejected — open-ended answers typically need human or LLM-judge scoring, reintroducing a correlated-grader confound.
- **A synthetic/custom-built benchmark**: rejected per the gap-analysis document's stated principle against inventing an idiosyncratic benchmark when comparable, established public ones are reachable.
- **BoolQ**: reachable but not pursued once SQuAD 2.0 was successfully acquired (see §3).

## What is not yet finalized

- The exact stratified sample size drawn from each pool (GSM8K's 1,319 items; SQuAD 2.0's 11,873 questions) for each of the 24 design cells is set by `POWER_ANALYSIS.md` (N=350/cell) and `configs/experiment_design.yaml`, not re-decided here.
- Whether agents are given a retrieval/context tool for SQuAD 2.0 (versus relying on parametric knowledge only) is a configured experimental factor, not a fixed dataset property — note SQuAD 2.0 tasks include the source passage by the dataset's own design, so "retrieval" here more precisely means whether agents share vs. have independently-provided copies of that passage, which is exactly the structural/evidence-root manipulation this experiment needs (see `src/structural/fault_basis.py`).
