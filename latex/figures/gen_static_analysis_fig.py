#!/usr/bin/env python3
"""Generates fig3_dataset_static_analysis.png from REAL, downloaded GSM8K
and SQuAD 2.0 data (datasets/). This is a genuine descriptive/static
analysis of the two datasets actually used in this project -- not
synthetic and not a claim about model behavior."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("latex/figures/static_analysis_data.npz")

fig, axes = plt.subplots(2, 3, figsize=(13, 7))

axes[0, 0].hist(d["gsm_qlen"], bins=30, color="#4C72B0", edgecolor="white")
axes[0, 0].set_title("GSM8K: question length (words)")
axes[0, 0].set_xlabel("words"); axes[0, 0].set_ylabel("count")

axes[0, 1].hist(d["gsm_steps"], bins=range(1, 14), color="#4C72B0", edgecolor="white")
axes[0, 1].set_title("GSM8K: reasoning steps per solution")
axes[0, 1].set_xlabel("steps (lines in reference solution)")

log_final = np.sign(d["gsm_final"]) * np.log10(np.abs(d["gsm_final"]) + 1)
axes[0, 2].hist(log_final, bins=30, color="#4C72B0", edgecolor="white")
axes[0, 2].set_title("GSM8K: final-answer magnitude")
axes[0, 2].set_xlabel(r"$\mathrm{sign}(x)\cdot\log_{10}(|x|+1)$")

axes[1, 0].hist(d["sq_ctxlen"], bins=30, color="#DD8452", edgecolor="white")
axes[1, 0].set_title("SQuAD 2.0: context length (words)")
axes[1, 0].set_xlabel("words"); axes[1, 0].set_ylabel("count")

axes[1, 1].hist(d["sq_qlen"], bins=25, color="#DD8452", edgecolor="white")
axes[1, 1].set_title("SQuAD 2.0: question length (words)")
axes[1, 1].set_xlabel("words")

axes[1, 2].hist(d["sq_anslen"], bins=25, color="#DD8452", edgecolor="white")
axes[1, 2].set_title("SQuAD 2.0: answer length (words,\nanswerable questions)")
axes[1, 2].set_xlabel("words")

fig.suptitle("Descriptive (static) analysis of the two real, downloaded task pools used in this study",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("latex/figures/fig3_dataset_static_analysis.png", dpi=150)
print("Wrote latex/figures/fig3_dataset_static_analysis.png")
