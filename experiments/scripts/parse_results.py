#!/usr/bin/env python3
"""
parse_results.py
Reads every DESTINY output file in experiments/results/ and extracts
the key metrics into a single CSV: experiments/data/results.csv

Metrics extracted (from CACHE DESIGN -- SUMMARY):
    total_area_mm2          Total Area (mm^2)
    read_latency_ns         Cache Hit Latency (ns)
    write_latency_ns        Cache Write Latency (ns)
    read_energy_nJ          Cache Hit Dynamic Energy (nJ/access)
    write_energy_nJ         Cache Write Dynamic Energy (nJ/access)
    leakage_power_mW        Cache Total Leakage Power (mW)

File naming convention (set by generate_configs.py):
    <technology>_<node>nm_output.txt            -> Experiment 1
    TSV_3D_SRAM_32nm_<param><value>_output.txt  -> Experiment 2

Run this script from any directory after run_all_experiments.ps1 completes.
"""

import csv
import re
import sys
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent.parent   # final/
RESULTS_DIR = ROOT / "experiments" / "results"
DATA_DIR    = ROOT / "experiments" / "data"
OUTPUT_CSV  = DATA_DIR / "results.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Regex patterns for DESTINY output
# The output is UTF-16 LE; after decoding the text is normal ASCII.
# ---------------------------------------------------------------------------
PATTERNS = {
    "total_area_mm2":    re.compile(r"Total Area\s*=\s*([\d.]+)\s*mm\^2"),
    "read_latency_ns":   re.compile(r"Cache Hit Latency\s*=\s*([\d.]+)\s*ns"),
    "write_latency_ns":  re.compile(r"Cache Write Latency\s*=\s*([\d.]+)\s*ns"),
    "read_energy_nJ":    re.compile(r"Cache Hit Dynamic Energy\s*=\s*([\d.]+)\s*nJ"),
    "write_energy_nJ":   re.compile(r"Cache Write Dynamic Energy\s*=\s*([\d.]+)\s*nJ"),
    "leakage_power_mW":  re.compile(r"Cache Total Leakage Power\s*=\s*([\d.]+)\s*mW"),
}

FIELDNAMES = [
    "filename", "experiment", "technology", "node_nm",
    "tsv_param", "tsv_value",
    "total_area_mm2", "read_latency_ns", "write_latency_ns",
    "read_energy_nJ", "write_energy_nJ", "leakage_power_mW",
    "notes",
]


def decode_destiny_output(path: Path) -> str:
    """DESTINY writes UTF-16 LE output on Windows. Try that first, fall back to UTF-8."""
    for enc in ("utf-16", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_bytes().decode("latin-1")


def extract_metrics(text: str) -> dict:
    metrics = {}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        metrics[key] = float(match.group(1)) if match else None
    return metrics


def parse_filename(stem: str) -> dict:
    """
    Examples:
        2D_SRAM_65nm            -> experiment=1, tech=2D_SRAM,  node=65,  tsv_param='', tsv_value=''
        3D_eDRAM_22nm           -> experiment=1, tech=3D_eDRAM, node=22,  tsv_param='', tsv_value=''
        TSV_3D_SRAM_32nm_LocalTSV1   -> experiment=2, tech=3D_SRAM, node=32, tsv_param=LocalTSVProjection, tsv_value=1
        TSV_3D_SRAM_32nm_GlobalTSV2  -> experiment=2, tsv_param=GlobalTSVProjection, tsv_value=2
        TSV_3D_SRAM_32nm_Redundancy1p2 -> experiment=2, tsv_param=TSVRedundancy, tsv_value=1.2
    """
    stem = stem.replace("_output", "")

    if stem.startswith("TSV_"):
        # Experiment 2
        info = {"experiment": 2, "technology": "3D_SRAM", "node_nm": 32}
        suffix = stem[len("TSV_3D_SRAM_32nm_"):]

        m = re.match(r"LocalTSV(\d+)", suffix)
        if m:
            info["tsv_param"]  = "LocalTSVProjection"
            info["tsv_value"]  = int(m.group(1))
            return info

        m = re.match(r"GlobalTSV(\d+)", suffix)
        if m:
            info["tsv_param"]  = "GlobalTSVProjection"
            info["tsv_value"]  = int(m.group(1))
            return info

        m = re.match(r"Redundancy(\d+p\d+)", suffix)
        if m:
            info["tsv_param"]  = "TSVRedundancy"
            info["tsv_value"]  = float(m.group(1).replace("p", "."))
            return info

        info["tsv_param"] = "unknown"
        info["tsv_value"] = suffix
        return info

    else:
        # Experiment 1  — format: <tech>_<node>nm
        m = re.match(r"^(2D_SRAM|3D_SRAM|2D_eDRAM|3D_eDRAM)_(\d+)nm$", stem)
        if m:
            return {
                "experiment":  1,
                "technology":  m.group(1),
                "node_nm":     int(m.group(2)),
                "tsv_param":   "",
                "tsv_value":   "",
            }

    return {"experiment": "?", "technology": stem, "node_nm": "", "tsv_param": "", "tsv_value": ""}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
output_files = sorted(RESULTS_DIR.glob("*_output.txt"))
if not output_files:
    print(f"No output files found in {RESULTS_DIR}")
    print("Run run_all_experiments.ps1 first.")
    sys.exit(1)

rows = []
missing_metrics_count = 0

for path in output_files:
    text    = decode_destiny_output(path)
    metrics = extract_metrics(text)
    meta    = parse_filename(path.stem)

    notes = ""
    if any(v is None for v in metrics.values()):
        missing = [k for k, v in metrics.items() if v is None]
        notes = f"missing: {', '.join(missing)}"
        missing_metrics_count += 1

    row = {
        "filename":      path.name,
        "experiment":    meta.get("experiment", ""),
        "technology":    meta.get("technology", ""),
        "node_nm":       meta.get("node_nm", ""),
        "tsv_param":     meta.get("tsv_param", ""),
        "tsv_value":     meta.get("tsv_value", ""),
        "notes":         notes,
        **metrics,
    }
    rows.append(row)
    status = "OK" if not notes else f"WARN ({notes})"
    print(f"  {path.name:55s}  {status}")

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n{len(rows)} rows written to {OUTPUT_CSV}")
if missing_metrics_count:
    print(f"WARNING: {missing_metrics_count} files had missing metrics — check 'notes' column.")
