from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def create_plots(df, summary, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sig = -np.log10(0.05)
    directions = df["Direction"].tolist()
    labels = df["Term_clean"].tolist()
    x = df["neglog10p"].to_numpy()
    counts = df["Count"].fillna(0).to_numpy()
    fdr = df["Benjamini"].fillna(1).to_numpy()

    # Bar chart
    fig, ax = plt.subplots(figsize=(13, max(6, len(df) * 0.42)))
    colors = ["#2980B9" if d == "Downregulated" else "#C0392B" for d in directions]
    bars = ax.barh(range(len(df)), x, color=colors, edgecolor="white",
                   linewidth=0.6, height=0.65)

    ax.axvline(sig, color="#7F8C8D", linestyle="--", linewidth=1.3, alpha=.8)
    for i, (bar, row) in enumerate(zip(bars, df.itertuples())):
        ax.text(bar.get_width()+0.08, i, f"n={row.Count}",
                va="center", fontsize=9, color="#2C3E50")
        if row.Benjamini < .05:
            ax.text(.08, i, f"FDR={row.Benjamini:.2e}",
                    va="center", fontsize=7.5, color="white", fontweight="bold")

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("−log₁₀ (P-value)", fontsize=12)
    ax.set_title("KEGG Pathway Enrichment Analysis", fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(x.max() * 1.35, sig * 1.5))
    ax.xaxis.grid(True, linestyle=":", alpha=.4)
    ax.set_axisbelow(True)
    ax.legend(handles=[
        mpatches.Patch(color="#C0392B", label="Upregulated"),
        mpatches.Patch(color="#2980B9", label="Downregulated")
    ], loc="lower right")
    plt.tight_layout()
    fig.savefig(output_dir / "KEGG_Bar_Chart.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Bubble plot
    fig, ax = plt.subplots(figsize=(13, max(6, len(df) * .42)))
    max_count = max(counts.max(), 1)
    sizes = (counts / max_count) * 700 + 100
    for i, row in enumerate(df.itertuples()):
        color = "#E74C3C" if row.Direction == "Upregulated" else "#3498DB"
        alpha = .90 if row.Benjamini < .05 else .55
        ax.scatter(row.neglog10p, i, s=sizes[i], c=color, alpha=alpha,
                   edgecolors="white", linewidths=1.3, zorder=3)
        ax.text(row.neglog10p+.15, i, f"n={row.Count}",
                va="center", fontsize=8.8, color="#2C3E50")

    ax.axvline(sig, color="#7F8C8D", linestyle="--", linewidth=1.3)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("−log₁₀ (P-value)", fontsize=12)
    ax.set_title("KEGG Pathway Enrichment Bubble Plot", fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(x.max()*1.45, sig*1.5))
    ax.xaxis.grid(True, linestyle=":", alpha=.4)
    ax.set_axisbelow(True)
    ax.legend(handles=[
        mpatches.Patch(color="#E74C3C", label="Upregulated"),
        mpatches.Patch(color="#3498DB", label="Downregulated")
    ], loc="lower right")
    plt.tight_layout()
    fig.savefig(output_dir / "KEGG_Bubble_Plot.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Combined figure
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(22, max(7, len(df)*.45)),
        gridspec_kw={"width_ratios": [1, 1]}
    )
    fig.suptitle("KEGG Pathway Enrichment Analysis", fontsize=14,
                 fontweight="bold", y=1.01)

    ax1.barh(range(len(df)), x, color=colors, edgecolor="white",
             linewidth=.5, height=.65)
    ax1.axvline(sig, color="#7F8C8D", linestyle="--", linewidth=1.2)
    ax1.set_yticks(range(len(df)))
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel("−log₁₀ (P-value)")
    ax1.set_title("A", loc="left", fontweight="bold")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.xaxis.grid(True, linestyle=":", alpha=.4)
    ax1.set_axisbelow(True)

    for i, row in enumerate(df.itertuples()):
        color = "#E74C3C" if row.Direction == "Upregulated" else "#3498DB"
        alpha = .90 if row.Benjamini < .05 else .55
        ax2.scatter(row.neglog10p, i, s=sizes[i], c=color, alpha=alpha,
                    edgecolors="white", linewidths=1.2)
        ax2.text(row.neglog10p+.12, i, f"n={row.Count}",
                 va="center", fontsize=8.5)

    ax2.axvline(sig, color="#7F8C8D", linestyle="--", linewidth=1.2)
    ax2.set_yticks(range(len(df)))
    ax2.set_yticklabels(labels, fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlabel("−log₁₀ (P-value)")
    ax2.set_title("B", loc="left", fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.xaxis.grid(True, linestyle=":", alpha=.4)
    ax2.set_axisbelow(True)

    fig.legend(handles=[
        mpatches.Patch(color="#C0392B", label="Upregulated"),
        mpatches.Patch(color="#2980B9", label="Downregulated")
    ], loc="lower center", ncol=2, bbox_to_anchor=(.5, -.02))
    plt.tight_layout()
    fig.savefig(output_dir / "KEGG_Combined_Figure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # CSV
    export = df[
        ["Term_clean", "Direction", "Count", "P-Value",
         "Benjamini", "Fold Enrichment", "neglog10p", "User Ids"]
    ].copy()
    export.columns = [
        "Pathway", "Direction", "Gene_Count", "P_Value",
        "Benjamini_FDR", "Fold_Enrichment", "negLog10_Pval", "Genes"
    ]
    export.to_csv(output_dir / "KEGG_All_Pathways_Summary.csv", index=False)
