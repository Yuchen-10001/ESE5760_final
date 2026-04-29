#!/usr/bin/env python3
"""
plot_advanced.py  —  v3
Advanced visualizations for experiments/data/results.csv.

Valid technologies (experiment 1, data complete):
  2D_SRAM, 3D_SRAM, 2D_eDRAM, 3D_eDRAM,
  2D_RRAM, 3D_RRAM, 2D_STTRAM
Skipped (all NaN / timeout):
  2D_PCRAM, 3D_STTRAM

Output (experiments/plots/advanced_viz/):
  heatmap_all_metrics.png + heatmap_<metric>.png ×6
  radar_22nm.png  radar_45nm.png  radar_90nm.png
  ppa_scatter.png   (2-panel: Volatile | Non-volatile)

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
    "3D_SRAM":   "s",
    "2D_eDRAM":  "^",
    "3D_eDRAM":  "D",
    "2D_RRAM":   "P",
    "3D_RRAM":   "X",
    "2D_STTRAM": "v",
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

# PPA grouping
VOLATILE    = ["2D_SRAM", "3D_SRAM", "2D_eDRAM", "3D_eDRAM"]
NONVOLATILE = ["2D_RRAM", "3D_RRAM", "2D_STTRAM"]


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
                # Grey hatching for missing cells
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

    # White cell-border grid via minor ticks
    ax.set_xticks(np.arange(-0.5, len(TECH_ORDER), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(NODE_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)


def plot_heatmap_combined():
    # 7 columns → wider figure
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
# 2.  RADAR CHARTS  (custom-drawn grid, 7 technologies)
# ─────────────────────────────────────────────────────────────────────────────
def plot_radar(node_nm):
    N      = len(METRIC_KEYS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)

    node_data = exp1[exp1["node_nm"] == node_nm]
    tech_vals = {}
    for tech in TECH_ORDER:
        row = node_data[node_data["technology"] == tech]
        if not row.empty:
            vals = np.array([row[m].values[0] for m in METRIC_KEYS],
                            dtype=float)
            if not np.all(np.isnan(vals)):
                tech_vals[tech] = vals
    if not tech_vals:
        return

    mins = np.array([
        min((v[i] for v in tech_vals.values() if not np.isnan(v[i])),
            default=np.nan)
        for i in range(N)
    ])
    maxs = np.array([
        max((v[i] for v in tech_vals.values() if not np.isnan(v[i])),
            default=np.nan)
        for i in range(N)
    ])

    def to_radius(vals):
        r = np.where(
            (maxs == mins) | np.isnan(vals),
            1.0,
            0.15 + 0.85 * (1.0 - (vals - mins) / (maxs - mins + 1e-12)),
        )
        return np.append(r, r[0])

    angles_closed = np.append(angles, angles[0])
    full_circle   = np.linspace(0, 2 * np.pi, 300)

    fig = plt.figure(figsize=(8.5, 8.5), facecolor="white")
    ax  = fig.add_subplot(111, polar=True)
    ax.set_facecolor("#F6F6F6")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.set_yticks([])
    ax.spines["polar"].set_visible(False)

    RING_VALS  = [0.25, 0.5, 0.75, 1.0]
    RING_COLOR = "#C8C8C8"

    ax.fill(full_circle, [1.0] * 300, color="#EFEFEF", zorder=0, alpha=0.6)

    for rv in RING_VALS:
        ax.plot(full_circle, [rv] * 300,
                color=RING_COLOR,
                linewidth=0.8 if rv < 1.0 else 1.4,
                linestyle="--" if rv < 1.0 else "-",
                alpha=0.9, zorder=1)

    for a in angles:
        ax.plot([a, a], [0, 1.0],
                color=RING_COLOR, linewidth=0.9, alpha=0.8, zorder=1)

    label_a = angles[0]
    for rv, lbl in zip([0.25, 0.5, 0.75], ["25%", "50%", "75%"]):
        ax.text(label_a + 0.22, rv, lbl,
                ha="left", va="center",
                fontsize=8, color="#AAAAAA", zorder=5)

    # Use alternating alpha so overlapping polygons stay readable
    for idx, tech in enumerate(TECH_ORDER):
        if tech not in tech_vals:
            continue
        r   = to_radius(tech_vals[tech])
        col = TECH_COLOR[tech]

        ax.fill(angles_closed, r, alpha=0.14, color=col, zorder=2)
        ax.plot(angles_closed, r,
                linewidth=2.5, color=col,
                linestyle=TECH_LS[tech],
                label=TECH_LABEL[tech], zorder=3,
                solid_capstyle="round", dash_capstyle="round")
        ax.scatter(angles, r[:-1], s=50, c=col,
                   edgecolors="white", linewidths=1.6, zorder=4)

    ax.set_xticks(angles)
    ax.set_xticklabels(RADAR_LABELS, fontsize=11,
                       fontweight="bold", color="#333333")
    ax.tick_params(axis="x", pad=16)   # push spoke labels clearly outside the ring
    ax.set_ylim(0, 1.10)               # outer boundary tight; labels sit beyond via pad

    ax.set_title(f"PPA Radar  —  {node_nm} nm",
                 fontsize=14, fontweight="bold", color="#222222", pad=18)

    leg = ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.20),
        ncol=4, fontsize=9.5, frameon=True,
        framealpha=0.95, edgecolor="#CCCCCC",
        title="Technology", title_fontsize=10,
    )
    leg.get_title().set_fontfamily("Times New Roman")
    for txt in leg.get_texts():
        txt.set_fontfamily("Times New Roman")

    fig.subplots_adjust(bottom=0.17, top=0.91)
    save(fig, f"radar_{node_nm}nm.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3.  PPA SCATTER  —  2-panel: Volatile | Non-volatile
# ─────────────────────────────────────────────────────────────────────────────
LABEL_NODES = {22, 180}

def _ppa_panel(ax, techs, panel_title):
    """Draw one PPA panel for the given list of technologies."""
    ax.set_facecolor("#FAFAFA")

    for tech in techs:
        sub = exp1[exp1["technology"] == tech].dropna(
            subset=["read_latency_ns", "total_area_mm2"]
        ).sort_values("node_nm", ascending=False)
        if sub.empty:
            continue

        col  = TECH_COLOR[tech]
        mks  = (sub["node_nm"] / max(NODE_ORDER) * 220 + 30).values

        ax.plot(
            sub["read_latency_ns"], sub["total_area_mm2"],
            color=col, linewidth=2.6, linestyle=TECH_LS[tech],
            label=TECH_LABEL[tech], zorder=3, alpha=0.90,
            solid_capstyle="round", dash_capstyle="round",
        )
        ax.scatter(
            sub["read_latency_ns"], sub["total_area_mm2"],
            s=mks, c=col, marker=TECH_MARKER[tech],
            edgecolors="white", linewidths=1.4,
            zorder=4, alpha=0.95,
        )

        is_2d = tech.startswith("2D")
        for _, row in sub[sub["node_nm"].isin(LABEL_NODES)].iterrows():
            n  = int(row["node_nm"])
            dy = 12 if is_2d else -14
            dx = -30 if n == 22 else 6
            ax.annotate(
                f"{n} nm",
                (row["read_latency_ns"], row["total_area_mm2"]),
                textcoords="offset points", xytext=(dx, dy),
                fontsize=8, color=col, fontweight="bold",
                ha="right" if n == 22 else "left",
            )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Read Latency (ns)", fontsize=12, labelpad=6)
    ax.set_ylabel("Total Area (mm²)", fontsize=12, labelpad=6)
    ax.set_title(panel_title, fontsize=13, fontweight="bold", pad=10)
    ax.legend(fontsize=9.5, framealpha=0.95,
              edgecolor="#CCCCCC", loc="upper left")
    ax.grid(True, which="major", linestyle="--",
            linewidth=0.7, color="#CCCCCC", alpha=0.8)
    ax.grid(False, which="minor")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#CCCCCC")
        ax.spines[spine].set_linewidth(0.8)


def plot_ppa_scatter():
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.5))
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "PPA Trade-off Space  —  Area vs. Read Latency  (log–log)\n"
        "marker size proportional to process node  ·  solid = 2D  ·  dashed = 3D  "
        "·  curves run 180 nm → 22 nm",
        fontsize=13, fontweight="bold", y=1.02,
    )

    _ppa_panel(axes[0], VOLATILE,
               "Volatile Memories  —  SRAM & eDRAM")
    _ppa_panel(axes[1], NONVOLATILE,
               "Non-volatile Memories  —  RRAM & STTRAM")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, "ppa_scatter.png")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}\n")

    print("[1/3] Heatmaps...")
    plot_heatmap_combined()
    plot_heatmap_individual()

    print("[2/3] Radar charts (22 nm, 45 nm, 90 nm)...")
    for node in [22, 45, 90]:
        plot_radar(node)

    print("[3/3] PPA scatter (Volatile | Non-volatile)...")
    plot_ppa_scatter()

    print(f"\nDone.  All figures saved to:\n  {OUT_DIR}")
