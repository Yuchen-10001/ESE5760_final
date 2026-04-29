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

Derived EDP and normalized-to-2D data live in:

- `data/results_with_edp.csv`
- `data/normalized_to_2d_baseline.csv`
- Figures: `plots/edp_normalized/`

These files are derived from `data/results.csv`; no extra DESTINY runs are
needed for EDP.

The regular node-sweep config generator now emits 2D/3D configs for SRAM,
eDRAM, STT-RAM, PCRAM, and RRAM across 180, 130, 90, 65, 45, 32, and 22 nm.
Some NVM runs can be very slow under the shared 2 MB, H-tree, WriteEDP
optimization setup. In `data/results.csv`, incomplete or timed-out runs are
kept with a `notes` entry instead of being treated as valid metric rows.

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

The layer-count sweep includes SRAM/eDRAM across 22, 32, 45, and 65 nm. A
focused RRAM 45 nm layer-count sweep is also included for 1, 2, and 4 stacked
dies. A compact report-ready subset lives in:

- `exploratory_sweeps/layer_sweep/data/layer_sweep_focus_1_2_4.csv`
- Figures: `plots/layer_focus/`
