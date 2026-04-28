#!/usr/bin/env python3
"""
generate_tsv_physical_45nm.py

Create a small 45nm TSV physical-parameter sweep for 3D SRAM.

The sweep uses direct physical scaling factors rather than projection labels.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "experiments" / "exploratory_sweeps" / "tsv_physical_45nm" / "configs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CELL_SRAM = "config/sample_SRAM.cell"

COMMON_BLOCK = """\
-DesignTarget: cache
-CacheAccessMode: Normal
-Associativity (for cache only): 1
-Capacity (MB): 2
-WordWidth (bit): 256
-DeviceRoadmap: LOP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: H-tree
-InternalSensing: true
-Temperature (K): 350
-OptimizationTarget: WriteEDP
-EnablePruning: Yes
-BufferDesignOptimization: latency"""

CASES = [
    ("baseline",      1.00, 1.00, 1.00, 1.00),
    ("dense_pitch",   0.70, 1.00, 1.00, 1.00),
    ("sparse_pitch",  1.30, 1.00, 1.00, 1.00),
    ("thin_via",      1.00, 0.70, 1.00, 1.00),
    ("thick_via",     1.00, 1.30, 1.00, 1.00),
    ("short_tsv",     1.00, 1.00, 0.70, 1.00),
    ("long_tsv",      1.00, 1.00, 1.30, 1.00),
    ("high_contact",  1.00, 1.00, 1.00, 1.50),
    ("low_contact",   1.00, 1.00, 1.00, 0.70),
    ("best_case",     0.70, 1.30, 0.70, 0.70),
    ("worst_case",    1.30, 0.70, 1.30, 1.50),
]


def write_cfg(name: str, pitch: float, diameter: float, length: float, contact: float) -> None:
    path = OUT_DIR / f"TSVPhys_3D_SRAM_45nm_{name}.cfg"
    content = "\n".join([
        f"// TSV physical sweep — 3D SRAM @ 45nm ({name})",
        f"// pitch_scale={pitch} diameter_scale={diameter} length_scale={length} contact_scale={contact}",
        "",
        COMMON_BLOCK,
        "-ProcessNode: 45",
        f"-MemoryCellInputFile: {CELL_SRAM}",
        "-StackedDieCount: 2",
        "-PartitionGranularity: 0",
        "-LocalTSVProjection: 0",
        "-GlobalTSVProjection: 0",
        "-TSVRedundancy: 1.0",
        f"-TSVPitchScale: {pitch}",
        f"-TSVDiameterScale: {diameter}",
        f"-TSVLengthScale: {length}",
        f"-TSVContactResistanceScale: {contact}",
        "",
    ])
    path.write_text(content)


def main() -> None:
    for case in CASES:
        write_cfg(*case)
    print(f"Wrote {len(CASES)} configs to {OUT_DIR}")


if __name__ == "__main__":
    main()
