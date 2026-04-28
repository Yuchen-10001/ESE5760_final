#!/usr/bin/env python3
"""
plot_trends.py
Reads experiments/data/results.csv and generates publication-ready figures
for the ESE5760 Final Project poster and writeup.

Figures produced:
    experiments/plots/regular_node_sweep/fig01_total_area_vs_node.png
    experiments/plots/regular_node_sweep/fig02_read_latency_vs_node.png
    experiments/plots/regular_node_sweep/fig03_write_latency_vs_node.png
    experiments/plots/regular_node_sweep/fig04_read_energy_vs_node.png
    experiments/plots/regular_node_sweep/fig05_write_energy_vs_node.png
    experiments/plots/regular_node_sweep/fig06_leakage_power_vs_node.png
    experiments/plots/tsv_sensitivity/fig07_tsv_sensitivity_area.png
    experiments/plots/tsv_sensitivity/fig08_tsv_sensitivity_read_latency.png

Requires: matplotlib, pandas  (pip install matplotlib pandas)
"""

import sys
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("Missing dependencies. Run:  pip install matplotlib pandas")
    sys.exit(1)

ROOT      = Path(__file__).resolve().parent.parent.parent
DATA_CSV = ROOT / "experiments" / "data" / "results.csv"
PLOTS_ROOT = ROOT / "experiments" / "plots"
REGULAR_PLOTS_DIR = PLOTS_ROOT / "regular_node_sweep"
TSV_PLOTS_DIR = PLOTS_ROOT / "tsv_sensitivity"
REGULAR_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
TSV_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_CSV.exists():
    print(f"results.csv not found at {DATA_CSV}")
    print("Run parse_results.py first.")
    sys.exit(1)

df = pd.read_csv(DATA_CSV)

# ---------------------------------------------------------------------------
# Plot style
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi":       150,
    "font.size":        11,
    "axes.titlesize":   12,
    "axes.labelsize":   11,
    "legend.fontsize":  10,
    "lines.linewidth":  1.8,
    "lines.markersize": 7,
})

TECH_STYLE = {
    "2D_SRAM":  {"color": "#1f77b4", "marker": "o",  "label": "2D SRAM"},
    "3D_SRAM":  {"color": "#ff7f0e", "marker": "s",  "label": "3D SRAM (2-die)"},
    "2D_eDRAM": {"color": "#2ca02c", "marker": "^",  "label": "2D eDRAM"},
    "3D_eDRAM": {"color": "#d62728", "marker": "D",  "label": "3D eDRAM (2-die)"},
}

TSV_PARAM_LABEL = {
    "LocalTSVProjection":  "LocalTSVProjection",
    "GlobalTSVProjection": "GlobalTSVProjection",
    "TSVRedundancy":       "TSVRedundancy",
}

TSV_PARAM_COLOR = {
    "LocalTSVProjection":  "#1f77b4",
    "GlobalTSVProjection": "#ff7f0e",
    "TSVRedundancy":       "#2ca02c",
}


def save(fig, directory, name):
    path = directory / name
    fig.savefig(path, bbox_inches="tight")
    if path.suffix.lower() == ".png":
        fig.savefig(path.with_suffix(".jpg"), bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {name}")


# ---------------------------------------------------------------------------
# Experiment 1 — node scaling sweep
# ---------------------------------------------------------------------------
exp1 = df[df["experiment"] == 1].copy()
exp1 = exp1[exp1["node_nm"].notna()]
exp1["node_nm"] = exp1["node_nm"].astype(int)
exp1 = exp1.sort_values("node_nm", ascending=False)

METRICS_EXP1 = [
    ("total_area_mm2",    "Total Area (mm²)",              "fig01_total_area_vs_node.png"),
    ("read_latency_ns",   "Read Latency (ns)",             "fig02_read_latency_vs_node.png"),
    ("write_latency_ns",  "Write Latency (ns)",            "fig03_write_latency_vs_node.png"),
    ("read_energy_nJ",    "Read Dynamic Energy (nJ)",      "fig04_read_energy_vs_node.png"),
    ("write_energy_nJ",   "Write Dynamic Energy (nJ)",     "fig05_write_energy_vs_node.png"),
    ("leakage_power_mW",  "Total Leakage Power (mW)",      "fig06_leakage_power_vs_node.png"),
]

for metric, ylabel, figname in METRICS_EXP1:
    fig, ax = plt.subplots(figsize=(6, 4))

    nodes = sorted(exp1["node_nm"].unique(), reverse=True)
    x_positions = {node: index + 1 for index, node in enumerate(nodes)}

    for tech, style in TECH_STYLE.items():
        subset = exp1[exp1["technology"] == tech].copy()
        if subset.empty or subset[metric].isna().all():
            continue
        subset = subset.sort_values("node_nm", ascending=False)
        subset["x"] = subset["node_nm"].map(x_positions)
        ax.plot(
            subset["x"], subset[metric],
            color=style["color"], marker=style["marker"], label=style["label"],
        )

    ax.set_xticks(range(1, len(nodes) + 1))
    ax.set_xticklabels([f"{n}nm" for n in nodes])
    ax.set_xlim(0.5, len(nodes) + 0.5)
    ax.set_xlabel("Process Node")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} vs. Process Node")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)

    save(fig, REGULAR_PLOTS_DIR, figname)

# ---------------------------------------------------------------------------
# Experiment 2 — TSV sensitivity
# ---------------------------------------------------------------------------
exp2 = df[df["experiment"] == 2].copy()

# Attach the baseline row (3D_SRAM_32nm from Exp 1) as LocalTSV=0, GlobalTSV=0, Redundancy=1.0
baseline_row = df[(df["experiment"] == 1) & (df["technology"] == "3D_SRAM") & (df["node_nm"] == 32)]

def build_tsv_sweep(param_name):
    """Collect baseline + all rows for one TSV parameter sweep."""
    sweep = exp2[exp2["tsv_param"] == param_name].copy()
    if baseline_row.empty:
        return sweep

    base = baseline_row.copy()
    base["tsv_param"] = param_name
    # assign baseline value
    baseline_vals = {"LocalTSVProjection": 0, "GlobalTSVProjection": 0, "TSVRedundancy": 1.0}
    base["tsv_value"] = baseline_vals[param_name]
    combined = pd.concat([base, sweep], ignore_index=True)
    combined["tsv_value"] = pd.to_numeric(combined["tsv_value"], errors="coerce")
    return combined.sort_values("tsv_value")


TSV_METRICS = [
    ("total_area_mm2",   "Total Area (mm²)",       "fig07_tsv_sensitivity_area.png"),
    ("read_latency_ns",  "Read Latency (ns)",      "fig08_tsv_sensitivity_read_latency.png"),
]

for metric, ylabel, figname in TSV_METRICS:
    fig, ax = plt.subplots(figsize=(6, 4))

    for param, color in TSV_PARAM_COLOR.items():
        sweep = build_tsv_sweep(param)
        if sweep.empty or sweep[metric].isna().all():
            continue
        ax.plot(
            sweep["tsv_value"], sweep[metric],
            color=color, marker="o", label=TSV_PARAM_LABEL[param],
        )

    ax.set_xlabel("TSV Parameter Value")
    ax.set_ylabel(ylabel)
    ax.set_title(f"TSV Sensitivity — {ylabel}\n(3D SRAM @ 32nm)")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)

    save(fig, TSV_PLOTS_DIR, figname)

print(f"\nRegular figures saved to {REGULAR_PLOTS_DIR}")
print(f"TSV figures saved to {TSV_PLOTS_DIR}")
