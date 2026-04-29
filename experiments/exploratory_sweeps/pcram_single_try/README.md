# PCRAM Single Feasibility Run

This folder records one PCRAM run using DESTINY's bundled PCRAM sample
configuration directly:

- Config: `config/sample_PCRAM.cfg`
- Cell file: `config/sample_PCRAM.cell`
- Process node: 32nm
- Capacity: 32 MB
- Associativity: 16
- Device roadmap: HP
- Routing: H-tree
- Optimization target: WriteEDP
- Stacked die count: 1

This run completed successfully in about 214 seconds. It is useful as evidence
that the bundled PCRAM model can produce a valid DESTINY result when used with
its own sample configuration.

Important caveat:

This point is not directly comparable with the main 2 MB, 1-way, LOP node sweep.
The main PCRAM cache-style configs still fail with `No valid solutions` and
subarray read-current/precharge constraints.
