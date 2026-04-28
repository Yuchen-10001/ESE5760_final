#!/usr/bin/env python3
"""
generate_layer_sweep.py

Creates a layer-count sweep for SRAM and eDRAM using the same normalized
baseline as the existing experiments. This sweep studies how increasing
StackedDieCount changes cache metrics.

Sweep:
    technology: SRAM, eDRAM
    process node: 65, 45, 32, 22 nm
    layers: 1, 2, 4, 8, 16

Output:
    experiments/exploratory_sweeps/layer_sweep/configs/*.cfg
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "experiments" / "exploratory_sweeps" / "layer_sweep" / "configs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CELL_SRAM = "config/sample_SRAM.cell"
CELL_EDRAM_2D = "config/sample_2D_eDRAM.cell"
CELL_EDRAM_3D = "config/sample_3D_eDRAM.cell"

NODES = [65, 45, 32, 22]
LAYERS = [1, 2, 4, 8, 16]

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


def stacked_block(layers: int) -> str:
    # Follow the existing experiments and keep partition granularity fixed,
    # so the sweep isolates layer count as the primary variable.
    return "\n".join(
        [
            f"-StackedDieCount: {layers}",
            "-PartitionGranularity: 0",
            "-LocalTSVProjection: 0",
            "-GlobalTSVProjection: 0",
            "-TSVRedundancy: 1.0",
        ]
    )


def write_cfg(path: Path, description: str, process_node: int, cell_file: str, layers: int, is_edram: bool) -> None:
    lines = [
        f"// {description}",
        "// ESE5760 Layer Sweep",
        "// 2MB | 256bit | Assoc=1 | LOP | 350K | WriteEDP",
        "",
        COMMON_BLOCK,
        f"-ProcessNode: {process_node}",
        f"-MemoryCellInputFile: {cell_file}",
        stacked_block(layers),
    ]
    if is_edram:
        lines.append("-RetentionTime (us): 40")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    count = 0
    for node in NODES:
        for layers in LAYERS:
            sram_name = f"SRAM_L{layers}_{node}nm.cfg"
            write_cfg(
                OUT_DIR / sram_name,
                f"SRAM layer sweep at {node}nm ({layers} layer)",
                node,
                CELL_SRAM,
                layers,
                is_edram=False,
            )
            count += 1

            edram_cell = CELL_EDRAM_2D if layers == 1 else CELL_EDRAM_3D
            edram_name = f"eDRAM_L{layers}_{node}nm.cfg"
            write_cfg(
                OUT_DIR / edram_name,
                f"eDRAM layer sweep at {node}nm ({layers} layer)",
                node,
                edram_cell,
                layers,
                is_edram=True,
            )
            count += 1

    print(f"Wrote {count} configs to {OUT_DIR}")


if __name__ == "__main__":
    main()
