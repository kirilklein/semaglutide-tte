#!/usr/bin/env python3
"""
Make a forest-style plot of IPW results with 95% CI.
Usage:
    python plot_ipw_forest.py path/to/causal_results.csv
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_ipw_forest(csv_path, out_path="figures/ipw_forestplot.png"):
    # Load results
    df = pd.read_csv(csv_path)

    # Outcomes order & labels
    order = [
        "all_cause_death",
        "death_mi_stroke",
        "hospitalization_with_heart_failure",
        "nonfatal_MI",
        "nonfatal_stroke",
    ]
    pretty = {
        "all_cause_death": "All-cause death",
        "death_mi_stroke": "Death/MI/Stroke",
        "hospitalization_with_heart_failure": "HF hospitalization",
        "nonfatal_MI": "Nonfatal MI",
        "nonfatal_stroke": "Nonfatal stroke",
    }

    # Reference results (Table 2)
    # Calculated manually from N=1648 (Semaglutide) vs N=1649 (Placebo)
    # RD = p1 - p2
    # SE = sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)
    # CI = RD +/- 1.96 * SE
    ref_data = {
        "all_cause_death": {
            "rd": 0.00123, "ci_lower": -0.01166, "ci_upper": 0.01412
        },
        "death_mi_stroke": {
            "rd": -0.02179, "ci_lower": -0.0408, "ci_upper": -0.0028
        },
        "hospitalization_with_heart_failure": {
            "rd": 0.00305, "ci_lower": -0.00938, "ci_upper": 0.01548
        },
        "nonfatal_MI": {
            "rd": -0.01029, "ci_lower": -0.0226, "ci_upper": 0.0020
        },
        "nonfatal_stroke": {
            "rd": -0.01030, "ci_lower": -0.0202, "ci_upper": -0.0004
        },
    }

    # Prepare IPW data
    ipw = (
        df.query("method == 'IPW' and outcome in @order")
          .assign(outcome=lambda d: pd.Categorical(d["outcome"], categories=order, ordered=True))
          .sort_values("outcome")
          .copy()
    )
    ipw["label"] = ipw["outcome"].map(pretty)

    # Prepare plotting arrays
    y = np.arange(len(ipw))[::-1]  # top-to-bottom
    
    # IPW values
    x_ipw = ipw["effect"].to_numpy()
    xerr_ipw = np.vstack([
        x_ipw - ipw["CI95_lower"].to_numpy(),
        ipw["CI95_upper"].to_numpy() - x_ipw
    ])

    # Reference values
    x_ref = []
    xerr_ref_lower = []
    xerr_ref_upper = []
    for outcome in ipw["outcome"]:
        d = ref_data[outcome]
        x_ref.append(d["rd"])
        xerr_ref_lower.append(d["rd"] - d["ci_lower"])
        xerr_ref_upper.append(d["ci_upper"] - d["rd"])
    
    x_ref = np.array(x_ref)
    xerr_ref = np.vstack([xerr_ref_lower, xerr_ref_upper])

    # Plot
    fig, ax = plt.subplots(figsize=(8, 3))

    # Alternating background colors
    for i in range(len(ipw)):
        if i % 2 == 0:  # even rows
            ax.axhspan(i - 0.5, i + 0.5, color="mistyrose", alpha=0.4, zorder=0)

    # Offsets for grouped display
    offset = 0.15
    
    # Plot IPW
    ax.errorbar(
        x_ipw, y + offset, xerr=xerr_ipw,
        fmt="o", markersize=4, capsize=3, linewidth=1.5,
        color="black", label="Ours (IPW)", zorder=3
    )
    
    # Plot Reference
    ax.errorbar(
        x_ref, y - offset, xerr=xerr_ref,
        fmt="o", markersize=4, capsize=3, linewidth=1.5,
        color="gray", mfc="white", label="RCT (Table 2)", zorder=3
    )

    # Reference line at 0
    ax.axvline(0, linestyle="--", linewidth=0.5, color="black", alpha=0.5)

    # Y labels
    ax.set_yticks(y)
    ax.set_yticklabels(ipw["label"])

    # Labels & grid
    ax.set_xlabel("Risk difference")
    ax.grid(axis="x", linestyle=":", alpha=0.7, zorder=1)
    ax.legend(loc="lower right", frameon=True, fontsize="small")
    
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Margins
    all_mins = np.concatenate([ipw["CI95_lower"], [d["ci_lower"] for d in ref_data.values()]])
    all_maxs = np.concatenate([ipw["CI95_upper"], [d["ci_upper"] for d in ref_data.values()]])
    xmin = min(all_mins.min(), x_ipw.min(), x_ref.min())
    xmax = max(all_maxs.max(), x_ipw.max(), x_ref.max())
    pad = 0.06 * (xmax - xmin if xmax > xmin else 1.0)
    ax.set_xlim(xmin - pad, xmax + pad)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Plot saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_ipw_forest.py path/to/causal_results.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    plot_ipw_forest(csv_path)
