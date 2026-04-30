#!/usr/bin/env python3
"""
plot_advanced.py  —  v4
Advanced visualizations for experiments/data/results.csv.

Valid technologies (experiment 1, data complete):
  2D_SRAM, 3D_SRAM, 2D_eDRAM, 3D_eDRAM,
  2D_RRAM, 3D_RRAM, 2D_STTRAM
Skipped (all NaN / timeout):
  2D_PCRAM, 3D_STTRAM

Output (experiments/plots/advanced_viz/):
  heatmap_all_metrics.png + heatmap_<metric>.png ×6
  radar_22nm.png  radar_45nm.png  radar_90nm.png
    → each is a 2×2 grid: SRAM | eDRAM / RRAM | STTRAM

Requires: matplotlib >= 3.5, pandas, numpy
"""

import sys
import numpy as np
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
except ImportError:
    print("Missing deps.  Run:  pip install matplotlib pandas numpy")
    sys.exit(1)

# Load Times New Roman from Windows fonts (available via WSL)
for _ttf in ["times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"]:
    _p = Path(f"/mnt/c/Windows/Fonts/{_ttf}")
    if _p.exists():
        fm.fontManager.addfont(str(_p))

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent.parent
DATA_CSV = ROOT / "experiments" / "data" / "results.csv"
OUT_DIR  = ROOT / "experiments" / "plots" / "advanced_viz"
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_CSV.exists():
    print(f"results.csv not found at {DATA_CSV}")
    sys.exit(1)

df   = pd.read_csv(DATA_CSV)
exp1 = df[df["experiment"] == 1].copy()
exp1["node_nm"] = exp1["node_nm"].astype(int)

# ── Global style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "Times New Roman",
    "font.size":      12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
})

# Only technologies with actual data
TECH_ORDER = [
    "2D_SRAM", "3D_SRAM",
    "2D_eDRAM", "3D_eDRAM",
    "2D_RRAM",  "3D_RRAM",
    "2D_STTRAM",
]

TECH_LABEL = {
    "2D_SRAM":   "2D SRAM",
    "3D_SRAM":   "3D SRAM",
    "2D_eDRAM":  "2D eDRAM",
    "3D_eDRAM":  "3D eDRAM",
    "2D_RRAM":   "2D RRAM",
    "3D_RRAM":   "3D RRAM",
    "2D_STTRAM": "2D STTRAM",
}

# Colour palette — visually distinct for 7 lines
TECH_COLOR = {
    "2D_SRAM":   "#4C72B0",   # blue
    "3D_SRAM":   "#DD8452",   # orange
    "2D_eDRAM":  "#55A868",   # green
    "3D_eDRAM":  "#C44E52",   # red
    "2D_RRAM":   "#8172B2",   # purple
    "3D_RRAM":   "#937860",   # brown
    "2D_STTRAM": "#DA8EC0",   # pink
}

TECH_MARKER = {
    "2D_SRAM":   "o",
    "3D_SRAM":   "o",
    "2D_eDRAM":  "o",
    "3D_eDRAM":  "o",
    "2D_RRAM":   "o",
    "3D_RRAM":   "o",
    "2D_STTRAM": "o",
}

# Solid = 2D, dashed = 3D (consistent convention)
TECH_LS = {t: "--" if t.startswith("3D") else "-" for t in TECH_ORDER}

NODE_ORDER = [180, 130, 90, 65, 45, 32, 22]

METRICS = [
    ("total_area_mm2",   "Area (mm²)",        "heatmap_total_area.png"),
    ("read_latency_ns",  "Read Latency (ns)",  "heatmap_read_latency.png"),
    ("write_latency_ns", "Write Latency (ns)", "heatmap_write_latency.png"),
    ("read_energy_nJ",   "Read Energy (nJ)",   "heatmap_read_energy.png"),
    ("write_energy_nJ",  "Write Energy (nJ)",  "heatmap_write_energy.png"),
    ("leakage_power_mW", "Leakage (mW)",       "heatmap_leakage_power.png"),
]
METRIC_KEYS   = [m[0] for m in METRICS]
METRIC_LABELS = [m[1] for m in METRICS]

RADAR_LABELS = [
    "Area\n(mm²)",
    "Read\nLatency",
    "Write\nLatency",
    "Read\nEnergy",
    "Write\nEnergy",
    "Leakage\nPower",
]

# Technology families for the 2×2 radar grid
RADAR_FAMILIES = [
    ("SRAM",   ["2D_SRAM",  "3D_SRAM"]),
    ("eDRAM",  ["2D_eDRAM", "3D_eDRAM"]),
    ("RRAM",   ["2D_RRAM",  "3D_RRAM"]),
    ("STTRAM", ["2D_STTRAM"]),
]

FAMILY_BG = {
    "SRAM":   "#FFF5EC",
    "eDRAM":  "#EFF8EF",
    "RRAM":   "#F2EFFA",
    "STTRAM": "#FBF0F6",
}


def save(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=250)
    fig.savefig(path.with_suffix(".jpg"), bbox_inches="tight", dpi=250)
    plt.close(fig)
    print(f"    saved → {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# 1.  HEATMAPS
# ─────────────────────────────────────────────────────────────────────────────
def _build_matrix(metric):
    """(nodes × techs) raw values and [0,1]-normalised values."""
    mat = np.full((len(NODE_ORDER), len(TECH_ORDER)), np.nan)
    for r, node in enumerate(NODE_ORDER):
        for c, tech in enumerate(TECH_ORDER):
            row = exp1[(exp1["node_nm"] == node) & (exp1["technology"] == tech)]
            if not row.empty and not pd.isna(row[metric].values[0]):
                mat[r, c] = row[metric].values[0]
    valid = mat[~np.isnan(mat)]
    if valid.size == 0:
        return mat, mat
    mn, mx = valid.min(), valid.max()
    norm = (mat - mn) / (mx - mn + 1e-12)
    return mat, norm


def _draw_single_heatmap(ax, metric, label, ann_fs=10):
    raw, norm = _build_matrix(metric)
    ax.imshow(norm, cmap=plt.cm.RdYlGn_r, vmin=0, vmax=1, aspect="auto")

    for r in range(len(NODE_ORDER)):
        for c in range(len(TECH_ORDER)):
            v = raw[r, c]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle(
                    (c - 0.5, r - 0.5), 1, 1,
                    fill=True, color="#DDDDDD", zorder=2,
                ))
                ax.text(c, r, "N/A", ha="center", va="center",
                        fontsize=8, color="#999999", zorder=3)
                continue
            n = norm[r, c]
            fc = "white" if (n < 0.18 or n > 0.72) else "#1a1a1a"
            ax.text(c, r, f"{v:.2f}", ha="center", va="center",
                    fontsize=ann_fs, color=fc, fontweight="bold")

    ax.set_xticks(range(len(TECH_ORDER)))
    ax.set_xticklabels([TECH_LABEL[t] for t in TECH_ORDER],
                       fontsize=9, rotation=30, ha="right")
    ax.set_yticks(range(len(NODE_ORDER)))
    ax.set_yticklabels([f"{n}nm" for n in NODE_ORDER], fontsize=10)
    ax.set_title(label, fontsize=12, fontweight="bold", pad=8)

    ax.set_xticks(np.arange(-0.5, len(TECH_ORDER), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(NODE_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)


def plot_heatmap_combined():
    fig, axes = plt.subplots(2, 3, figsize=(26, 13))
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "Memory Technology — Full Performance Heatmap\n"
        "green = best  ·  red = worst  ·  grey = no data  ·  values normalized globally per metric",
        fontsize=15, fontweight="bold", y=1.01,
    )

    for ax, (metric, label, _) in zip(axes.flat, METRICS):
        _draw_single_heatmap(ax, metric, label, ann_fs=10)

    fig.subplots_adjust(left=0.05, right=0.87, top=0.92, bottom=0.06,
                        hspace=0.5, wspace=0.25)

    cbar_ax = fig.add_axes([0.90, 0.12, 0.016, 0.72])
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label("")
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])
    cbar.set_ticklabels(["Best", "", "Mid", "", "Worst"], fontsize=10)

    save(fig, "heatmap_all_metrics.png")


def plot_heatmap_individual():
    for metric, label, fname in METRICS:
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor("white")
        _draw_single_heatmap(ax, metric, label, ann_fs=11)
        ax.set_xlabel("Technology", labelpad=8, fontsize=12)
        ax.set_ylabel("Process Node", labelpad=8, fontsize=12)

        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, norm=plt.Normalize(0, 1))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, shrink=0.88, pad=0.03)
        cbar.set_label("")
        cbar.set_ticks([0, 0.5, 1])
        cbar.set_ticklabels(["Best", "Mid", "Worst"], fontsize=10)

        fig.tight_layout()
        save(fig, fname)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  RADAR CHARTS  —  2×2 grid (SRAM | eDRAM / RRAM | STTRAM)
#     Convention: smaller metric value = better = larger radius (center = worst)
#     Normalization is global across all 7 technologies so subplots are comparable
# ─────────────────────────────────────────────────────────────────────────────
def _draw_radar_panel(ax, family_techs, family_name, tech_vals, mins, maxs,
                      angles, angles_closed, full_circle):
    """Draw one family's radar panel onto a polar Axes."""
    N = len(METRIC_KEYS)
    RING_COLOR = "#C0C0C0"

    ax.set_facecolor(FAMILY_BG[family_name])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.set_yticks([])
    ax.spines["polar"].set_visible(False)

    # Concentric rings at 25 / 50 / 75 / 100 %
    for rv in [0.25, 0.5, 0.75, 1.0]:
        ax.plot(full_circle, [rv] * len(full_circle),
                color=RING_COLOR,
                linewidth=1.0 if rv < 1.0 else 1.8,
                linestyle="--" if rv < 1.0 else "-",
                alpha=0.85, zorder=1)

    # Spoke lines
    for a in angles:
        ax.plot([a, a], [0, 1.0],
                color=RING_COLOR, linewidth=0.8, alpha=0.7, zorder=1)

    # Percentage labels on the first spoke (Area, top)
    for rv, lbl in zip([0.0, 0.25, 0.5, 0.75, 1.0],
                       ["0%", "25%", "50%", "75%", "100%"]):
        ax.text(angles[0] + 0.18, rv, lbl,
                ha="left", va="center",
                fontsize=9, color="#999999", zorder=5)

    def to_radius(vals):
        # Inverted: smaller value (better) → larger radius.
        # Floor at 0.15 so no technology collapses to the center.
        norm = np.where(
            (maxs == mins) | np.isnan(vals),
            0.85,   # tie / missing → show at 85% (near outer ring)
            np.clip(1.0 - (vals - mins) / (maxs - mins + 1e-12), 0.0, 1.0),
        )
        r = 0.15 + 0.85 * norm
        return np.append(r, r[0])

    for tech in family_techs:
        if tech not in tech_vals:
            continue
        r   = to_radius(tech_vals[tech])
        col = TECH_COLOR[tech]

        ax.fill(angles_closed, r, alpha=0.22, color=col, zorder=2)
        ax.plot(angles_closed, r,
                linewidth=2.2, color=col,
                linestyle=TECH_LS[tech],
                label=TECH_LABEL[tech], zorder=3,
                solid_capstyle="round", dash_capstyle="round")
        ax.scatter(angles, r[:-1], s=45, c=col,
                   edgecolors="white", linewidths=1.5, zorder=4)

    ax.set_xticks(angles)
    ax.set_xticklabels(RADAR_LABELS, fontsize=13, fontweight="bold",
                       color="#333333")
    ax.tick_params(axis="x", pad=5)
    ax.set_ylim(0, 1.05)

    ax.set_title(family_name, fontsize=15, fontweight="bold",
                 color="#222222", pad=6)

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Place legend inside the circle at lower-right to avoid overlapping
        # with spoke labels outside the axes boundary.
        ax.legend(
            handles, labels,
            loc="lower right", bbox_to_anchor=(1.18, -0.02),
            ncol=1, fontsize=10, frameon=True,
            framealpha=0.95, edgecolor="#CCCCCC",
        )


def plot_radar(node_nm):
    N             = len(METRIC_KEYS)
    angles        = np.linspace(0, 2 * np.pi, N, endpoint=False)
    angles_closed = np.append(angles, angles[0])
    full_circle   = np.linspace(0, 2 * np.pi, 300)

    node_data = exp1[exp1["node_nm"] == node_nm]

    # Gather all tech values for global normalization
    tech_vals = {}
    for tech in TECH_ORDER:
        row = node_data[node_data["technology"] == tech]
        if not row.empty:
            vals = np.array([row[m].values[0] for m in METRIC_KEYS], dtype=float)
            if not np.all(np.isnan(vals)):
                tech_vals[tech] = vals

    if not tech_vals:
        return

    # Global min/max across all technologies (makes panels comparable)
    mins = np.array([
        min((v[i] for v in tech_vals.values() if not np.isnan(v[i])), default=0.0)
        for i in range(N)
    ])
    maxs = np.array([
        max((v[i] for v in tech_vals.values() if not np.isnan(v[i])), default=1.0)
        for i in range(N)
    ])

    fig = plt.figure(figsize=(14, 12), facecolor="white")
    # Manual title — avoids suptitle fighting with set_position axes
    fig.text(0.5, 0.97, f"PPA Radar  —  {node_nm} nm",
             ha="center", va="top",
             fontsize=20, fontweight="bold", color="#111111")

    # [left, bottom, width, height] in figure fraction.
    # Columns 0.02 apart so circles nearly touch horizontally.
    # Row gap 0.08 — no per-subplot external legend, so no conflict.
    pos = [
        [0.02, 0.55, 0.47, 0.35],   # top-left  (SRAM)
        [0.51, 0.55, 0.47, 0.35],   # top-right (eDRAM)
        [0.02, 0.08, 0.47, 0.35],   # bot-left  (RRAM)
        [0.51, 0.08, 0.47, 0.35],   # bot-right (STTRAM)
    ]

    for idx, (family_name, family_techs) in enumerate(RADAR_FAMILIES):
        ax = fig.add_axes(pos[idx], projection="polar")
        _draw_radar_panel(ax, family_techs, family_name, tech_vals,
                          mins, maxs, angles, angles_closed, full_circle)

    save(fig, f"radar_{node_nm}nm.png")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}\n")

    print("[1/2] Heatmaps...")
    plot_heatmap_combined()
    plot_heatmap_individual()

    print("[2/2] Radar charts (22 nm, 45 nm, 90 nm)...")
    for node in [22, 45, 90]:
        plot_radar(node)

    print(f"\nDone.  All figures saved to:\n  {OUT_DIR}")
