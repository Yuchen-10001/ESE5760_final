#!/usr/bin/env python3
"""
Plot focused 1/2/4-layer comparisons for SRAM/eDRAM/RRAM.
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
DATA_CSV = ROOT / "experiments" / "exploratory_sweeps" / "layer_sweep" / "data" / "layer_sweep_focus_1_2_4.csv"
PLOT_DIR = ROOT / "experiments" / "plots" / "layer_focus"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_CSV.exists():
    print("Run derive_layer_focus.py first.")
    sys.exit(1)

df = pd.read_csv(DATA_CSV)

style = {
    ("SRAM", 32): ("#1f77b4", "o", "SRAM 32nm"),
    ("SRAM", 45): ("#ff7f0e", "s", "SRAM 45nm"),
    ("eDRAM", 32): ("#2ca02c", "^", "eDRAM 32nm"),
    ("eDRAM", 45): ("#d62728", "D", "eDRAM 45nm"),
    ("RRAM", 45): ("#17becf", ">", "RRAM 45nm"),
}


def save(fig, name):
    path = PLOT_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    fig.savefig(path.with_suffix(".jpg"), bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"saved: {path}")


for metric, ylabel, filename in [
    ("improvement_total_area_mm2", "Area Improvement vs 1-layer", "fig20_layer_area_improvement.png"),
    ("improvement_read_edp_nJ_ns", "Read EDP Improvement vs 1-layer", "fig21_layer_read_edp_improvement.png"),
    ("improvement_write_edp_nJ_ns", "Write EDP Improvement vs 1-layer", "fig22_layer_write_edp_improvement.png"),
]:
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for key, (color, marker, label) in style.items():
        technology, node = key
        subset = df[(df["technology"] == technology) & (df["node_nm"] == node)].copy()
        if subset.empty or subset[metric].isna().all():
            continue
        subset = subset.sort_values("layers")
        ax.plot(subset["layers"], subset[metric], color=color, marker=marker, label=label)

    ax.axhline(1.0, color="#555555", linestyle=":", linewidth=1)
    ax.set_xticks([1, 2, 4])
    ax.set_xlabel("Stacked Die Count")
    ax.set_ylabel("1-layer metric / N-layer metric")
    ax.set_title(ylabel)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    save(fig, filename)

print(f"Layer focus figures saved to {PLOT_DIR}")
