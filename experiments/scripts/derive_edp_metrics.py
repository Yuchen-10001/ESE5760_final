#!/usr/bin/env python3
"""
Derive EDP and normalized metrics from experiments/data/results.csv.

Outputs:
    experiments/data/results_with_edp.csv
    experiments/data/normalized_to_2d_baseline.csv
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "experiments" / "data"
IN_CSV = DATA_DIR / "results.csv"
EDP_CSV = DATA_DIR / "results_with_edp.csv"
NORM_CSV = DATA_DIR / "normalized_to_2d_baseline.csv"

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

for row in rows:
    read_latency = as_float(row.get("read_latency_ns"))
    write_latency = as_float(row.get("write_latency_ns"))
    read_energy = as_float(row.get("read_energy_nJ"))
    write_energy = as_float(row.get("write_energy_nJ"))
    row["read_edp_nJ_ns"] = fmt(read_latency * read_energy) if read_latency is not None and read_energy is not None else ""
    row["write_edp_nJ_ns"] = fmt(write_latency * write_energy) if write_latency is not None and write_energy is not None else ""

edp_fields = list(rows[0].keys()) if rows else []
for field in ("read_edp_nJ_ns", "write_edp_nJ_ns"):
    if field not in edp_fields:
        edp_fields.append(field)

with EDP_CSV.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=edp_fields)
    writer.writeheader()
    writer.writerows(rows)

baseline = {}
for row in rows:
    tech = row.get("technology", "")
    if not tech.startswith("2D_") or row.get("notes"):
        continue
    base_key = (tech.removeprefix("2D_"), row.get("node_nm"))
    baseline[base_key] = row

norm_rows = []
for row in rows:
    tech = row.get("technology", "")
    if row.get("experiment") != "1" or row.get("notes"):
        continue
    if tech.startswith("2D_"):
        memory = tech.removeprefix("2D_")
        organization = "2D"
    elif tech.startswith("3D_"):
        memory = tech.removeprefix("3D_")
        organization = "3D"
    else:
        continue

    base = baseline.get((memory, row.get("node_nm")))
    if not base:
        continue

    out = {
        "filename": row.get("filename", ""),
        "memory": memory,
        "organization": organization,
        "technology": tech,
        "node_nm": row.get("node_nm", ""),
    }
    for metric in METRICS:
        value = as_float(row.get(metric))
        base_value = as_float(base.get(metric))
        out[f"normalized_{metric}"] = fmt(value / base_value) if value is not None and base_value not in (None, 0) else ""
        out[f"improvement_{metric}"] = fmt(base_value / value) if value not in (None, 0) and base_value is not None else ""
    norm_rows.append(out)

norm_fields = ["filename", "memory", "organization", "technology", "node_nm"]
for metric in METRICS:
    norm_fields.extend([f"normalized_{metric}", f"improvement_{metric}"])

with NORM_CSV.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=norm_fields)
    writer.writeheader()
    writer.writerows(norm_rows)

print(f"Wrote {len(rows)} rows to {EDP_CSV}")
print(f"Wrote {len(norm_rows)} rows to {NORM_CSV}")
