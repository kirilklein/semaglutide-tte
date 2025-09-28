import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import textwrap
import numpy as np

def plot_weighted_vs_unweighted(df_unweighted: pd.DataFrame, df_weighted: pd.DataFrame, sort_by="Control"):
    """
    Scatter plot comparing weighted vs unweighted percentages for Control and Exposed groups.
    - Y-axis: criteria
    - X-axis: percentage
    - Groups: Control, Exposed
    """
    # Copy and add weighting labels
    df_unweighted = df_unweighted.copy()
    df_weighted = df_weighted.copy()
    df_unweighted["weighting"] = "Unweighted"
    df_weighted["weighting"] = "Weighted"
    
    df = pd.concat([df_unweighted, df_weighted], ignore_index=True)

    # Clean percentage column
    df["percentage"] = (
        df["percentage"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )
    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce")

    # Keep only Control and Exposed
    df = df[df["group"].isin(["Control", "Exposed"])]

    # Sort criteria (optional)
    if sort_by in ["Control", "Exposed"]:
        order = (
            df[df["group"] == sort_by]
            .groupby("criterion")["percentage"]
            .mean()
            .sort_values(ascending=False)
            .index
        )
    else:
        order = sorted(df["criterion"].unique(), ascending=False)
    
    # Define colors
    palette = {
        ("Control", "Unweighted"): "#a6cee3",  # light blue
        ("Control", "Weighted"): "#1f78b4",    # dark blue
        ("Exposed", "Unweighted"): "#fca5a5",  # light red
        ("Exposed", "Weighted"): "#e31a1c",    # dark red
    }
    
    # Wrap long criterion names
    df["criterion_wrapped"] = df["criterion"].apply(lambda x: "\n".join(textwrap.wrap(str(x), 50)))
    
    fig_height = max(6, 0.25 * len(order))  # scale height
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    # --- alternating background colors ---
    n_rows = len(order)
    for i in range(n_rows):
        if i % 2 == 1:  # every other row
            ax.axhspan(i-0.5, i+0.5, color="lightgrey", alpha=0.2, zorder=0)
    
    # Plot points
    for (grp, wgt), subdf in df.groupby(["group", "weighting"]):
        ax.scatter(
            subdf["percentage"],
            subdf["criterion_wrapped"],
            label=f"{grp} - {wgt}",
            color=palette[(grp, wgt)],
            s=60,
            alpha=0.9,
            edgecolor="black",
            linewidth=0.3,
            zorder=2
        )
    
    # Styling
    ax.set_xlabel("Percentage (%)", fontsize=12)
    ax.set_ylabel("Criterion", fontsize=12)
    ax.legend(title="Group", bbox_to_anchor=(0.5, 0.999), loc="upper left", fontsize=10, ncols=2)
    
    # Move x-axis up a little
    ax.spines['bottom'].set_position(("outward", 1))
    
    # Add vertical dashed lines at 20%, 40%, 60%...
    max_val = 80
    for x in np.arange(20, max_val+20, 20):
        ax.axvline(x=x, color="gray", linestyle="--", linewidth=0.6, alpha=0.5, zorder=1)
    
    ax.set_xlim(0, 101)
    ax.set_ylim(-1, n_rows - 0.5)
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0f}%")
    
    sns.despine(trim=True)
    fig.tight_layout()
    
    return fig
