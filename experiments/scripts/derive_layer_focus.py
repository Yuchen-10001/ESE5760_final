#!/usr/bin/env python3
"""
Create a compact 1/2/4-layer CSV from the layer sweep.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "experiments" / "exploratory_sweeps" / "layer_sweep" / "data"
IN_CSV = DATA_DIR / "layer_sweep_results.csv"
OUT_CSV = DATA_DIR / "layer_sweep_focus_1_2_4.csv"

FOCUS_ROWS = {
    ("SRAM", 32),
    ("SRAM", 45),
    ("eDRAM", 32),
    ("eDRAM", 45),
    ("RRAM", 45),
}

METRICS = [
    "total_area_mm2",
    "read_latency_ns",
    "write_latency_ns",
    "read_energy_nJ",
    "write_energy_nJ",
    "leakage_power_mW",
    "read_edp_nJ_ns",
    "write_edp_nJ_ns",
]


def as_float(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt(value):
    if value is None:
        return ""
    return f"{value:.6g}"


with IN_CSV.open(newline="") as f:
    rows = list(csv.DictReader(f))

base = {}
for row in rows:
    if int(row["layers"]) == 1:
        base[(row["technology"], int(row["node_nm"]))] = row

out_rows = []
for row in rows:
    key = (row["technology"], int(row["node_nm"]))
    if key not in FOCUS_ROWS or int(row["layers"]) not in (1, 2, 4):
        continue
    out = dict(row)
    baseline = base.get(key)
    for metric in METRICS:
        value = as_float(row.get(metric))
        base_value = as_float(baseline.get(metric)) if baseline else None
        out[f"normalized_{metric}"] = fmt(value / base_value) if value is not None and base_value not in (None, 0) else ""
        out[f"improvement_{metric}"] = fmt(base_value / value) if value not in (None, 0) and base_value is not None else ""
    out_rows.append(out)

fieldnames = list(rows[0].keys()) if rows else []
for metric in METRICS:
    fieldnames.extend([f"normalized_{metric}", f"improvement_{metric}"])

with OUT_CSV.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)

print(f"Wrote {len(out_rows)} rows to {OUT_CSV}")
