#!/usr/bin/env python3
"""
Plot EDP and normalized 3D improvement figures for report use.
"""

import sys
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    print("Missing dependencies. Run: pip install matplotlib pandas")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "experiments" / "data"
PLOT_DIR = ROOT / "experiments" / "plots" / "edp_normalized"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

edp_csv = DATA_DIR / "results_with_edp.csv"
norm_csv = DATA_DIR / "normalized_to_2d_baseline.csv"

if not edp_csv.exists() or not norm_csv.exists():
    print("Run derive_edp_metrics.py first.")
    sys.exit(1)

edp = pd.read_csv(edp_csv)
norm = pd.read_csv(norm_csv)
edp = edp[(edp["experiment"] == 1) & (edp["notes"].isna())].copy()
edp["node_nm"] = edp["node_nm"].astype(int)

nodes = sorted(edp["node_nm"].unique(), reverse=True)
x_positions = {node: index + 1 for index, node in enumerate(nodes)}

tech_style = {
    "2D_SRAM": {"color": "#1f77b4", "marker": "o", "label": "2D SRAM"},
    "3D_SRAM": {"color": "#ff7f0e", "marker": "s", "label": "3D SRAM"},
    "2D_eDRAM": {"color": "#2ca02c", "marker": "^", "label": "2D eDRAM"},
    "3D_eDRAM": {"color": "#d62728", "marker": "D", "label": "3D eDRAM"},
    "2D_STTRAM": {"color": "#9467bd", "marker": "v", "label": "2D STT-RAM"},
    "2D_RRAM": {"color": "#bcbd22", "marker": "<", "label": "2D RRAM"},
    "3D_RRAM": {"color": "#17becf", "marker": ">", "label": "3D RRAM"},
}


def save(fig, name):
    path = PLOT_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    fig.savefig(path.with_suffix(".jpg"), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"saved: {path}")


for metric, ylabel, filename in [
    ("read_edp_nJ_ns", "Read EDP (nJ*ns)", "fig16_read_edp_vs_node.png"),
    ("write_edp_nJ_ns", "Write EDP (nJ*ns)", "fig17_write_edp_vs_node.png"),
]:
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for tech, style in tech_style.items():
        subset = edp[edp["technology"] == tech].copy()
        if subset.empty or subset[metric].isna().all():
            continue
        subset["x"] = subset["node_nm"].map(x_positions)
        subset = subset.sort_values("node_nm", ascending=False)
        ax.plot(subset["x"], subset[metric], color=style["color"], marker=style["marker"], label=style["label"])

    ax.set_xticks(range(1, len(nodes) + 1))
    ax.set_xticklabels([f"{node}nm" for node in nodes])
    ax.set_xlabel("Process Node")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} vs. Process Node")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    save(fig, filename)

norm = norm[(norm["organization"] == "3D") & (norm["memory"].isin(["SRAM", "eDRAM", "RRAM"]))].copy()
norm["node_nm"] = norm["node_nm"].astype(int)

for metric, ylabel, filename in [
    ("improvement_read_edp_nJ_ns", "3D Read EDP Improvement vs 2D", "fig18_3d_read_edp_improvement.png"),
    ("improvement_write_edp_nJ_ns", "3D Write EDP Improvement vs 2D", "fig19_3d_write_edp_improvement.png"),
]:
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for memory, color, marker in [("SRAM", "#ff7f0e", "s"), ("eDRAM", "#d62728", "D"), ("RRAM", "#17becf", ">")]:
        subset = norm[norm["memory"] == memory].copy()
        if subset.empty or subset[metric].isna().all():
            continue
        subset["x"] = subset["node_nm"].map(x_positions)
        subset = subset.sort_values("node_nm", ascending=False)
        ax.plot(subset["x"], subset[metric], color=color, marker=marker, label=memory)

    ax.axhline(1.0, color="#555555", linestyle=":", linewidth=1)
    ax.set_xticks(range(1, len(nodes) + 1))
    ax.set_xticklabels([f"{node}nm" for node in nodes])
    ax.set_xlabel("Process Node")
    ax.set_ylabel("2D metric / 3D metric")
    ax.set_title(ylabel)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best")
    save(fig, filename)

print(f"EDP figures saved to {PLOT_DIR}")
