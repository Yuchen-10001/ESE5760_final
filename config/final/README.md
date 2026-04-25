# Final Project Configs (ESE 5760)

This folder contains **project-specific** DESTINY configuration templates and generated `.cfg` files for the final project experiments:

- Baseline scaling vs. process node (65/45/32/22nm)
- TSV sensitivity sweeps (projection, redundancy, hop model)

Why this exists:
- The bundled `config/sample_*.cfg` files are **not** normalized (capacity/wordwidth/assoc/temperature/roadmap differ across technologies),
  so they are not ideal for fair cross-technology comparisons.
- These configs make the assumptions explicit and keep comparisons consistent.

## Layout

- `templates/`:
  - Hand-authored baseline templates (do not run directly).
- `generated/`:
  - Auto-generated configs created by `scripts/final_generate_configs.ps1`.

## Run

From repo root:

```powershell
pwsh -File scripts/final_generate_configs.ps1
pwsh -File scripts/final_run.ps1
pwsh -File scripts/final_parse.ps1
```

Notes:
- DESTINY expects cell files to be found relative to the **current working directory**.
  Our runner executes from `config/` so `sample_*.cell` resolves correctly.

