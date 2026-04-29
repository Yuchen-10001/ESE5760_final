# NVM Feasibility Sweep at 45nm

This exploratory sweep checks whether PCRAM and RRAM can run under the same
general cache-style assumptions used by the SRAM/eDRAM node sweep.

Fixed settings:

- Process node: 45nm
- Organization: 2D
- Word width: 256 bit
- Associativity: 1
- Device roadmap: LOP
- Temperature: 350 K

Swept settings:

- Memory cell: PCRAM, RRAM
- Capacity: 1 MB, 2 MB
- Routing: H-tree, Non-H-tree
- Optimization target: Area, ReadLatency, WriteEDP

Summary:

- RRAM completed for all tested 45nm feasibility configurations.
- PCRAM returned `No valid solutions` for all tested configurations.
- PCRAM failures repeatedly report:
  `Error[Subarray]: Read current too large or too small that no reasonable precharge voltage existing`

Interpretation:

For 45nm, the RRAM issue is mostly runtime/search-cost related; it can complete
when run individually with a longer timeout. The PCRAM issue is different: it is
a model-validity problem under this cache/subarray setup, not simply an H-tree
or WriteEDP runtime problem.
