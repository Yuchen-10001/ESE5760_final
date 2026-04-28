# Experiment Layout

The experiment assets are grouped by purpose.

## Regular Node Sweep

Six primary process-node metrics live in:

- MATLAB scripts: `matlab/regular_node_sweep/`
- Figures: `plots/regular_node_sweep/`
- Source CSV: `data/results.csv`

Figure order:

| Figure | Metric |
|---|---|
| `fig01_total_area_vs_node` | Total area |
| `fig02_read_latency_vs_node` | Read latency |
| `fig03_write_latency_vs_node` | Write latency |
| `fig04_read_energy_vs_node` | Read dynamic energy |
| `fig05_write_energy_vs_node` | Write dynamic energy |
| `fig06_leakage_power_vs_node` | Leakage power |

The node-sweep MATLAB scripts use equal-spaced x positions with real process-node labels.

## TSV Sensitivity

The focused 3D SRAM TSV sensitivity figures live in:

- MATLAB scripts: `matlab/tsv_sensitivity/`
- Figures: `plots/tsv_sensitivity/`

Figure order:

| Figure | Metric |
|---|---|
| `fig07_tsv_sensitivity_area` | TSV sensitivity, total area |
| `fig08_tsv_sensitivity_read_latency` | TSV sensitivity, read latency |

## Exploratory Sweeps

Large auxiliary sweeps are isolated under:

- Raw sweep assets: `exploratory_sweeps/`
- MATLAB scripts: `matlab/exploratory_sweeps/`
- Figures: `plots/exploratory_sweeps/`

This includes layer-count sweeps, TSV multinode sweeps, and TSV physical-parameter sweeps.
