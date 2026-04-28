#!/usr/bin/env python3
"""
parse_layer_sweep.py

Parses experiments/exploratory_sweeps/layer_sweep/results/*.txt into a CSV summary.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "experiments" / "exploratory_sweeps" / "layer_sweep" / "results"
DATA_DIR = ROOT / "experiments" / "exploratory_sweeps" / "layer_sweep" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = DATA_DIR / "layer_sweep_results.csv"

PATTERNS = {
    "total_area_mm2": re.compile(r"Total Area\s*=\s*([\d.]+)\s*mm\^2"),
    "read_latency_ns": re.compile(r"Cache Hit Latency\s*=\s*([\d.]+)\s*ns"),
    "write_latency_ns": re.compile(r"Cache Write Latency\s*=\s*([\d.]+)\s*ns"),
    "write_energy_nJ": re.compile(r"Cache Write Dynamic Energy\s*=\s*([\d.]+)\s*nJ"),
    "leakage_power_mW": re.compile(r"Cache Total Leakage Power\s*=\s*([\d.]+)\s*mW"),
    "refresh_latency_us": re.compile(r"Cache Refresh Latency\s*=\s*([\d.]+)\s*us"),
}

FIELDS = [
    "filename",
    "technology",
    "layers",
    "node_nm",
    "total_area_mm2",
    "read_latency_ns",
    "write_latency_ns",
    "write_energy_nJ",
    "leakage_power_mW",
    "refresh_latency_us",
]


def decode_text(path: Path) -> str:
    for enc in ("utf-16", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return path.read_bytes().decode("latin-1")


def parse_name(stem: str) -> tuple[str, int, int]:
    m = re.match(r"^(SRAM|eDRAM)_L(\d+)_(\d+)nm_output$", stem)
    if not m:
        raise ValueError(f"Unexpected filename: {stem}")
    return m.group(1), int(m.group(2)), int(m.group(3))


def main() -> None:
    rows = []
    for path in sorted(RESULTS_DIR.glob("*_output.txt")):
        text = decode_text(path)
        technology, layers, node_nm = parse_name(path.stem)
        row = {
            "filename": path.name,
            "technology": technology,
            "layers": layers,
            "node_nm": node_nm,
        }
        for key, pattern in PATTERNS.items():
            match = pattern.search(text)
            row[key] = float(match.group(1)) if match else ""
        rows.append(row)

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
