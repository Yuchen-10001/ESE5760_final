#!/usr/bin/env python3
"""
generate_tsv_multinode_grid.py

Build a full-factorial TSV sweep for 3D SRAM at two representative nodes.

Sweep dimensions:
    nodes: 32, 45 nm
    LocalTSVProjection:  0, 1, 2
    GlobalTSVProjection: 0, 1, 2
    TSVRedundancy:       1.0, 1.2, 1.5

Total:
    2 nodes x 3 x 3 x 3 = 54 configs

Output:
    experiments/tsv_multinode/configs/*.cfg
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "experiments" / "tsv_multinode" / "configs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CELL_SRAM = "config/sample_SRAM.cell"
NODES = [32, 45]
LOCAL_LEVELS = [0, 1, 2]
GLOBAL_LEVELS = [0, 1, 2]
REDUNDANCY_LEVELS = [1.0, 1.2, 1.5]

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


def label_redundancy(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value).replace(".", "p")


def write_cfg(path: Path, node: int, local: int, global_tsv: int, redundancy: float) -> None:
    content = "\n".join([
        f"// TSV multinode sweep — 3D SRAM @ {node}nm",
        f"// LocalTSVProjection={local}  GlobalTSVProjection={global_tsv}  TSVRedundancy={redundancy}",
        "// ESE5760 Final Project — Fixed 3D SRAM baseline",
        "",
        COMMON_BLOCK,
        f"-ProcessNode: {node}",
        f"-MemoryCellInputFile: {CELL_SRAM}",
        "-StackedDieCount: 2",
        "-PartitionGranularity: 0",
        f"-LocalTSVProjection: {local}",
        f"-GlobalTSVProjection: {global_tsv}",
        f"-TSVRedundancy: {redundancy}",
        "",
    ])
    path.write_text(content)


def main() -> None:
    count = 0
    for node in NODES:
        for local in LOCAL_LEVELS:
            for global_tsv in GLOBAL_LEVELS:
                for redundancy in REDUNDANCY_LEVELS:
                    name = (
                        f"TSVGrid_3D_SRAM_{node}nm_"
                        f"L{local}_G{global_tsv}_R{label_redundancy(redundancy)}.cfg"
                    )
                    write_cfg(OUT_DIR / name, node, local, global_tsv, redundancy)
                    count += 1

    print(f"Wrote {count} configs to {OUT_DIR}")


if __name__ == "__main__":
    main()
