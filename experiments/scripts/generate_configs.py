#!/usr/bin/env python3
"""
generate_configs.py
Generates all DESTINY config files for the ESE5760 Final Project.

Experiment 1 — Node scaling sweep:
    4 technologies (2D_SRAM, 3D_SRAM, 2D_eDRAM, 3D_eDRAM)
    × 4 process nodes (65 / 45 / 32 / 22 nm)
    = 16 configs

Experiment 2 — TSV sensitivity sweep (3D SRAM @ 32nm):
    Vary LocalTSVProjection  : 0 (baseline), 1, 2
    Vary GlobalTSVProjection : 0 (baseline), 1, 2
    Vary TSVRedundancy       : 1.0 (baseline), 1.2, 1.5
    = 6 new configs  (baseline reuses 3D_SRAM_32nm.cfg from Exp 1)

Run this script once before running experiments.
Output: experiments/configs/*.cfg
Cell files are resolved relative to the destiny.exe working directory (final/).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent   # final/
CONFIGS_OUT = ROOT / "experiments" / "configs"
CONFIGS_OUT.mkdir(parents=True, exist_ok=True)

# Paths are relative to final/ (where destiny.exe is called from)
CELL_SRAM      = "config/sample_SRAM.cell"
CELL_EDRAM_2D  = "config/sample_2D_eDRAM.cell"
CELL_EDRAM_3D  = "config/sample_3D_eDRAM.cell"

NODES = [65, 45, 32, 22]

# ---------------------------------------------------------------------------
# Shared baseline block — same for all 25 configs
# ---------------------------------------------------------------------------
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


def tsv_block(local=0, global_tsv=0, redundancy=1.0):
    return (
        f"-StackedDieCount: 2\n"
        f"-PartitionGranularity: 0\n"
        f"-LocalTSVProjection: {local}\n"
        f"-GlobalTSVProjection: {global_tsv}\n"
        f"-TSVRedundancy: {redundancy}"
    )


def write_cfg(filename, description, process_node, cell_file, extra_block=""):
    lines = [
        f"// {description}",
        f"// ESE5760 Final Project — Normalized baseline",
        f"// 2MB | 256bit | Assoc=1 | LOP | 350K | WriteEDP",
        "",
        COMMON_BLOCK,
        f"-ProcessNode: {process_node}",
        f"-MemoryCellInputFile: {cell_file}",
    ]
    if extra_block:
        lines.append(extra_block)

    content = "\n".join(lines) + "\n"
    path = CONFIGS_OUT / filename
    path.write_text(content)
    print(f"  {filename}")


# ---------------------------------------------------------------------------
# Experiment 1: node scaling sweep
# ---------------------------------------------------------------------------
print("Experiment 1 — node scaling sweep:")

for node in NODES:

    write_cfg(
        filename    = f"2D_SRAM_{node}nm.cfg",
        description = f"2D SRAM at {node}nm",
        process_node = node,
        cell_file   = CELL_SRAM,
        extra_block = "-StackedDieCount: 1",
    )

    write_cfg(
        filename    = f"3D_SRAM_{node}nm.cfg",
        description = f"3D SRAM at {node}nm  [TSV baseline: Local=0 Global=0 Redundancy=1.0]",
        process_node = node,
        cell_file   = CELL_SRAM,
        extra_block = tsv_block(local=0, global_tsv=0, redundancy=1.0),
    )

    write_cfg(
        filename    = f"2D_eDRAM_{node}nm.cfg",
        description = f"2D eDRAM at {node}nm",
        process_node = node,
        cell_file   = CELL_EDRAM_2D,
        extra_block = "-StackedDieCount: 1\n-RetentionTime (us): 40",
    )

    write_cfg(
        filename    = f"3D_eDRAM_{node}nm.cfg",
        description = f"3D eDRAM at {node}nm  [TSV baseline: Local=0 Global=0 Redundancy=1.0]",
        process_node = node,
        cell_file   = CELL_EDRAM_3D,
        extra_block = tsv_block(local=0, global_tsv=0, redundancy=1.0) + "\n-RetentionTime (us): 40",
    )

# ---------------------------------------------------------------------------
# Experiment 2: TSV sensitivity (3D SRAM @ 32nm)
# Baseline is already 3D_SRAM_32nm.cfg  (Local=0, Global=0, Redundancy=1.0)
# ---------------------------------------------------------------------------
print("\nExperiment 2 — TSV sensitivity on 3D SRAM @ 32nm:")
print("  (baseline = 3D_SRAM_32nm.cfg, reused from Exp 1)")

# LocalTSVProjection sweep  (Global=0, Redundancy=1.0 fixed)
for local in [1, 2]:
    write_cfg(
        filename    = f"TSV_3D_SRAM_32nm_LocalTSV{local}.cfg",
        description = f"TSV sensitivity — LocalTSVProjection={local}  (Global=0, Redundancy=1.0)",
        process_node = 32,
        cell_file   = CELL_SRAM,
        extra_block = tsv_block(local=local, global_tsv=0, redundancy=1.0),
    )

# GlobalTSVProjection sweep  (Local=0, Redundancy=1.0 fixed)
for glob in [1, 2]:
    write_cfg(
        filename    = f"TSV_3D_SRAM_32nm_GlobalTSV{glob}.cfg",
        description = f"TSV sensitivity — GlobalTSVProjection={glob}  (Local=0, Redundancy=1.0)",
        process_node = 32,
        cell_file   = CELL_SRAM,
        extra_block = tsv_block(local=0, global_tsv=glob, redundancy=1.0),
    )

# TSVRedundancy sweep  (Local=0, Global=0 fixed)
for redund, label in [(1.2, "1p2"), (1.5, "1p5")]:
    write_cfg(
        filename    = f"TSV_3D_SRAM_32nm_Redundancy{label}.cfg",
        description = f"TSV sensitivity — TSVRedundancy={redund}  (Local=0, Global=0)",
        process_node = 32,
        cell_file   = CELL_SRAM,
        extra_block = tsv_block(local=0, global_tsv=0, redundancy=redund),
    )

print(f"\nDone. {len(list(CONFIGS_OUT.glob('*.cfg')))} configs written to:")
print(f"  {CONFIGS_OUT}")
