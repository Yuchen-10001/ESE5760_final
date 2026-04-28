#!/usr/bin/env python3
"""
parse_tsv_physical_45nm.py

Parse a direct physical TSV sweep at 45nm into CSV.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "experiments" / "exploratory_sweeps" / "tsv_physical_45nm" / "results"
DATA_DIR = ROOT / "experiments" / "exploratory_sweeps" / "tsv_physical_45nm" / "data"
OUT_CSV = DATA_DIR / "tsv_physical_45nm_results.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

PATTERNS = {
    "total_area_mm2": re.compile(r"Total Area\s*=\s*([\d.]+)\s*mm\^2"),
    "read_latency_ns": re.compile(r"Cache Hit Latency\s*=\s*([\d.]+)\s*ns"),
    "write_latency_ns": re.compile(r"Cache Write Latency\s*=\s*([\d.]+)\s*ns"),
    "write_energy_nJ": re.compile(r"Cache Write Dynamic Energy\s*=\s*([\d.]+)\s*nJ"),
    "leakage_power_mW": re.compile(r"Cache Total Leakage Power\s*=\s*([\d.]+)\s*mW"),
}


def decode_text(path: Path) -> str:
    for enc in ("utf-16", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeError:
            continue
    return path.read_bytes().decode("latin-1", errors="ignore")


def parse_case_name(stem: str) -> str:
    stem = stem.replace("_output", "")
    prefix = "TSVPhys_3D_SRAM_45nm_"
    if not stem.startswith(prefix):
        raise ValueError(f"Unrecognized filename: {stem}")
    return stem[len(prefix):]


def extract_metrics(text: str) -> dict:
    out = {}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        out[key] = float(match.group(1)) if match else None
    return out


def main() -> None:
    rows = []
    for path in sorted(RESULTS_DIR.glob("*_output.txt")):
        rows.append({
            "filename": path.name,
            "case": parse_case_name(path.stem),
            "technology": "3D_SRAM",
            "node_nm": 45,
            **extract_metrics(decode_text(path)),
        })

    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "filename",
                "case",
                "technology",
                "node_nm",
                "total_area_mm2",
                "read_latency_ns",
                "write_latency_ns",
                "write_energy_nJ",
                "leakage_power_mW",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
