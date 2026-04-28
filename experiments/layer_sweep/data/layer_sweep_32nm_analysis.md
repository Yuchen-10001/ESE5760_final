# 32nm Layer Sweep Summary

## Setup

- Fixed baseline: `2 MB`, `256-bit`, `Assoc=1`, `LOP`, `350 K`, `WriteEDP`
- Sweep variable: `StackedDieCount = 1 / 2 / 4 / 8 / 16`
- Fixed TSV style: `PartitionGranularity = 0`, `LocalTSVProjection = 0`, `GlobalTSVProjection = 0`, `TSVRedundancy = 1.0`
- SRAM uses `config/sample_SRAM.cell`
- eDRAM uses `config/sample_2D_eDRAM.cell` at `L1` and `config/sample_3D_eDRAM.cell` for `L2+`

## Results

| Technology | Layers | Area (mm^2) | Read (ns) | Write (ns) | Write Energy (nJ) | Leakage (mW) | Write EDP |
|---|---:|---:|---:|---:|---:|---:|---:|
| SRAM  | 1  | 4.262 | 1.061 | 0.605 | 0.123 | 234.632 | 0.0744 |
| SRAM  | 2  | 2.132 | 0.633 | 0.423 | 0.089 | 234.632 | 0.0376 |
| SRAM  | 4  | 1.542 | 0.488 | 0.242 | 0.126 | 285.915 | 0.0305 |
| SRAM  | 8  | 1.014 | 0.338 | 0.172 | 0.338 | 386.048 | 0.0581 |
| SRAM  | 16 | 0.620 | 0.244 | 0.126 | 1.369 | 471.264 | 0.1725 |
| eDRAM | 1  | 1.440 | 0.757 | 0.607 | 0.066 | 29.992  | 0.0401 |
| eDRAM | 2  | 1.068 | 0.472 | 0.340 | 0.061 | 50.137  | 0.0207 |
| eDRAM | 4  | 0.927 | 0.316 | 0.199 | 0.108 | 132.416 | 0.0215 |
| eDRAM | 8  | 1.199 | 0.337 | 0.141 | 0.339 | 352.322 | 0.0478 |
| eDRAM | 16 | 0.618 | 0.248 | 0.105 | 1.370 | 348.162 | 0.1439 |

## Main Takeaways

1. Increasing layer count consistently improves area density and latency for SRAM through `L16`, but the energy-leakage trade-off turns sharply after `L4`.
2. SRAM write EDP improves from `L1 -> L4` (`0.0744 -> 0.0305`) and then degrades at `L8` and especially `L16` because dynamic write energy rises much faster than latency falls.
3. eDRAM shows the same "sweet spot then penalty" pattern, but the turning point arrives earlier: `L2` is best on write EDP (`0.0207`), `L4` is nearly tied, and `L8/L16` become much more expensive in write energy and leakage.
4. eDRAM leakage is extremely sensitive to higher layer counts in this setup: `29.992 mW` at `L1`, `50.137 mW` at `L2`, `132.416 mW` at `L4`, then above `348 mW` at `L8/L16`.
5. The results are strongly non-monotonic in some metrics, which suggests the trend is not a pure geometric stacking benefit. DESTINY is re-optimizing organization under a `WriteEDP` objective, so changes in bank/mat/subarray structure are part of the observed response.

## Interpretation

- For SRAM, `L4` is the best compromise in this 32nm sweep: it retains most of the area and latency gains from stacking while avoiding the severe write-energy and leakage blow-up seen at `L8/L16`.
- For eDRAM, `L2` remains the cleanest operating point and `L4` is still defensible if the design prioritizes latency and footprint over standby power.
- `L8` and `L16` should not be presented as universally better 3D points. They reduce area and latency, but they do so by paying a very large dynamic-energy and leakage cost.
- These layer-count sweeps therefore reinforce a more cautious conclusion than "more layers is always better": at 32nm, moderate stacking helps, but aggressive stacking pushes the optimizer into much less attractive operating points.
