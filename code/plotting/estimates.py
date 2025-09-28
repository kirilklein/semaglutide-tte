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

    ipw = (
        df.query("method == 'IPW' and outcome in @order")
          .assign(outcome=lambda d: pd.Categorical(d["outcome"], categories=order, ordered=True))
          .sort_values("outcome")
          .copy()
    )
    ipw["label"] = ipw["outcome"].map(pretty)

    # Prepare data
    y = np.arange(len(ipw))[::-1]  # top-to-bottom
    x = ipw["effect"].to_numpy()
    xerr = np.vstack([
        x - ipw["CI95_lower"].to_numpy(),
        ipw["CI95_upper"].to_numpy() - x
    ])

    # Plot
    fig, ax = plt.subplots(figsize=(8, 2.1))

    # Alternating background colors
    for i in range(len(ipw)):
        if i % 2 == 0:  # even rows
            ax.axhspan(i - 0.5, i + 0.5, color="mistyrose", alpha=0.4, zorder=0)

    # Errorbar scatter
    ax.errorbar(
        x, y, xerr=xerr,
        fmt="s", markersize=3, capsize=4, linewidth=1.5,
        color="black", zorder=3
    )

    # Reference line at 0
    ax.axvline(0, linestyle="--", linewidth=0.5, color="black", alpha=0.5)

    # Y labels
    ax.set_yticks(y)
    ax.set_yticklabels(ipw["label"])

    # Labels & grid
    ax.set_xlabel("Risk difference (IPW)")
    ax.grid(axis="x", linestyle=":", alpha=0.7, zorder=1)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Margins
    xmin = min(ipw["CI95_lower"].min(), x.min())
    xmax = max(ipw["CI95_upper"].max(), x.max())
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
