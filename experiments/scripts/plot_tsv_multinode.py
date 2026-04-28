#!/usr/bin/env python3
"""
plot_tsv_multinode.py

Visualize the full-factorial TSV sweep for 3D SRAM at 32nm and 45nm.

Input:
    experiments/tsv_multinode/data/tsv_multinode_results.csv

Output:
    experiments/plots/fig11_tsv_multinode_area.jpg
    experiments/plots/fig12_tsv_multinode_write_energy.jpg
    experiments/plots/fig13_tsv_multinode_read_latency.jpg
"""

from pathlib import Path
import csv

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent.parent
CSV_PATH = ROOT / "experiments" / "tsv_multinode" / "data" / "tsv_multinode_results.csv"
PLOTS_DIR = ROOT / "experiments" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

NODES = [32, 45]
LOCAL_LEVELS = [0, 1, 2]
GLOBAL_LEVELS = [0, 1, 2]
REDUNDANCY_LEVELS = [1.0, 1.2, 1.5]
REDUNDANCY_LABELS = ["1.0", "1.2", "1.5"]
NODE_STYLE = {
    32: {"color": (0.122, 0.467, 0.706), "marker": "o", "label": "32 nm"},
    45: {"color": (0.839, 0.153, 0.157), "marker": "s", "label": "45 nm"},
}


def load_rows():
    rows = []
    with CSV_PATH.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row["node_nm"] = int(row["node_nm"])
            row["local_tsv_projection"] = int(row["local_tsv_projection"])
            row["global_tsv_projection"] = int(row["global_tsv_projection"])
            row["tsv_redundancy"] = float(row["tsv_redundancy"])
            for key in [
                "total_area_mm2",
                "read_latency_ns",
                "write_latency_ns",
                "write_energy_nJ",
                "leakage_power_mW",
            ]:
                row[key] = float(row[key])
            rows.append(row)
    return rows


def average_metric(rows, node, metric, local=None, global_tsv=None, redundancy=None):
    subset = [r for r in rows if r["node_nm"] == node]
    if local is not None:
        subset = [r for r in subset if r["local_tsv_projection"] == local]
    if global_tsv is not None:
        subset = [r for r in subset if r["global_tsv_projection"] == global_tsv]
    if redundancy is not None:
        subset = [r for r in subset if abs(r["tsv_redundancy"] - redundancy) < 1e-9]
    return sum(r[metric] for r in subset) / len(subset)


def save(fig, filename):
    path = PLOTS_DIR / filename
    fig.savefig(path, format="jpg", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(path)


def plot_three_panel(rows, metric, ylabel, title, filename, legend_loc="best"):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))

    for node in NODES:
        style = NODE_STYLE[node]

        local_values = [
            average_metric(rows, node, metric, local=level)
            for level in LOCAL_LEVELS
        ]
        axes[0].plot(
            LOCAL_LEVELS,
            local_values,
            f"-{style['marker']}",
            color=style["color"],
            linewidth=2,
            markersize=7,
            label=style["label"],
        )

        global_values = [
            average_metric(rows, node, metric, global_tsv=level)
            for level in GLOBAL_LEVELS
        ]
        axes[1].plot(
            GLOBAL_LEVELS,
            global_values,
            f"-{style['marker']}",
            color=style["color"],
            linewidth=2,
            markersize=7,
            label=style["label"],
        )

        redundancy_values = [
            average_metric(rows, node, metric, redundancy=level)
            for level in REDUNDANCY_LEVELS
        ]
        axes[2].plot(
            REDUNDANCY_LEVELS,
            redundancy_values,
            f"-{style['marker']}",
            color=style["color"],
            linewidth=2,
            markersize=7,
            label=style["label"],
        )

    axes[0].set_title("LocalTSVProjection Sweep", fontweight="bold")
    axes[0].set_xlabel("LocalTSVProjection")
    axes[0].set_ylabel(ylabel)
    axes[0].set_xticks(LOCAL_LEVELS)

    axes[1].set_title("GlobalTSVProjection Sweep", fontweight="bold")
    axes[1].set_xlabel("GlobalTSVProjection")
    axes[1].set_ylabel(ylabel)
    axes[1].set_xticks(GLOBAL_LEVELS)

    axes[2].set_title("TSVRedundancy Sweep", fontweight="bold")
    axes[2].set_xlabel("TSV Redundancy")
    axes[2].set_ylabel(ylabel)
    axes[2].set_xticks(REDUNDANCY_LEVELS)
    axes[2].set_xticklabels(REDUNDANCY_LABELS)

    for ax in axes:
        ax.grid(True)
        ax.boxplot if False else None
        ax.legend(loc=legend_loc, fontsize=10)
        ax.tick_params(labelsize=10)
        for spine in ax.spines.values():
            spine.set_visible(True)

    fig.suptitle(title, fontsize=13, fontweight="bold")
    save(fig, filename)


def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing input CSV: {CSV_PATH}")

    rows = load_rows()
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 11,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
    })

    plot_three_panel(
        rows,
        "total_area_mm2",
        "Total Area (mm^2)",
        "TSV Multinode Sweep — Total Area (3D SRAM @ 32 nm / 45 nm)",
        "fig11_tsv_multinode_area.jpg",
        legend_loc="best",
    )

    plot_three_panel(
        rows,
        "write_energy_nJ",
        "Write Dynamic Energy (nJ/access)",
        "TSV Multinode Sweep — Write Dynamic Energy (3D SRAM @ 32 nm / 45 nm)",
        "fig12_tsv_multinode_write_energy.jpg",
        legend_loc="best",
    )

    plot_three_panel(
        rows,
        "read_latency_ns",
        "Read Latency (ns)",
        "TSV Multinode Sweep — Read Latency (3D SRAM @ 32 nm / 45 nm)",
        "fig13_tsv_multinode_read_latency.jpg",
        legend_loc="best",
    )


if __name__ == "__main__":
    main()
