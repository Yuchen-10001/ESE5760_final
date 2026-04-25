# TSV Audit Note

## Scope

This note is a first-pass reverse-engineering and audit checklist for the TSV model in the current DESTINY-derived codebase.

It focuses on three questions:

1. How is TSV cost modeled today?
2. Which assumptions come from DESTINY / CACTI-3DD semantics?
3. Which parts of the current implementation look inconsistent with DESTINY's documented model or are at least worth auditing first?

This note is intentionally practical. It is meant to support the next step of checking the code against the DESTINY paper / technical report, not to propose a fully new model yet.

## Sources Used

### Local code and docs

- `README`
- `TSV.cpp`, `TSV.h`
- `Technology.cpp`, `Technology.h`
- `Mat.cpp`
- `BankWithHtree.cpp`
- `BankWithoutHtree.cpp`
- `Result.cpp`
- `Doc/Midterm_Progress_Report_ESE5760.tex`

### Primary references

- DESTINY DATE 2015 paper:
  `https://pasalabs.org/papers/2015/2015_DATE_Destiny.pdf`
- DESTINY extended paper / documentation-style description:
  `https://www.mdpi.com/2079-9268/7/3/23`
- CACTI-3DD reference named by DESTINY:
  `https://ieeexplore.ieee.org/document/6176428`

## Current TSV Model: Reverse-Engineered View

The TSV model is split across three layers of abstraction.

### 1. Technology-level TSV primitive parameters

`Technology.cpp` defines TSV geometry-dependent primitive parameters:

- pitch
- diameter
- length
- dielectric thickness
- contact resistance
- depletion width
- liner dielectric constant

These are stored per projection choice and per TSV class in `Technology`.

Key locations:

- `Technology.h:60-82`
- `Technology.cpp:1921-2015`
- `Technology.cpp:2017-2037`

Important observations:

- TSV resistance is modeled as conductor resistance plus contact resistance.
- TSV capacitance is modeled as self-capacitance plus lateral and diagonal coupling terms.
- TSV occupied area is modeled as `pitch^2`.
- Layer count rescales TSV length through `SetLayerCount(...)`, which then recomputes TSV parasitics.

### 2. TSV primitive circuit model

`TSV.cpp` models the latency / dynamic energy / leakage of one TSV plus optional driver chain.

Key locations:

- `TSV.cpp:30-80` initialization
- `TSV.cpp:83-121` area
- `TSV.cpp:124-136` read/write interface
- `TSV.cpp:139-221` latency and energy

Important observations:

- `TSV::Initialize(TSV_type, bool buffered = false)` supports both buffered and unbuffered TSVs.
- In normal execution paths, bank and mat code call `Initialize(tsv_type)` without the second argument, so the default behavior is currently unbuffered.
- Read and write are modeled by calling the same internal function with different input ramps.
- Reset and set are simply aliased to write.

Audit-sensitive heuristics in this file:

- `buffer_area_height = 50 * tech->featureSize` in `TSV.cpp:90`
- duplicated leakage calculation path in `TSV.cpp:103-108`
- the comment `TODO -- Understand this better` around the final area composition in `TSV.cpp:115-119`

### 3. Architectural TSV counting and aggregation

The number of TSVs and how they contribute to bank area / latency / energy are not decided in `TSV.cpp`. That logic is implemented in `Mat.cpp`, `BankWithHtree.cpp`, `BankWithoutHtree.cpp`, and partially re-derived in `Result.cpp`.

This is the most important audit target.

## Coarse-Grained TSV Counting in Banks

For bank-level 3D stacking, both H-tree and non-H-tree code use nearly identical formulas.

Key locations:

- `BankWithHtree.cpp:561-580`
- `BankWithHtree.cpp:701-735`
- `BankWithoutHtree.cpp:271-289`
- `BankWithoutHtree.cpp:504-538`

The current coarse-grained count is:

- `numControlBits = stackedDieCount`
- `numAddressBits = log2(capacity / blockSize / associativity / stackedDieCount)`
- `numDataBits = blockSize * 2`

and then:

- `numTotalBits = (control + address + data) * redundancy`
- `numAccessBits = (control + address + blockSize) * redundancy`
- `numReadBits = (control + address) * redundancy`
- `numDataBits = blockSize * redundancy`

Latency / energy aggregation then assumes:

- worst-case traversal to the furthest die
- hop count = `stackedDieCount - 1`
- read latency = control/address write path plus data read path
- write latency = write path only

This logic is duplicated in both bank implementations.

## Fine-Grained TSV Counting in Mats

For fine-grained partitioning, the bank-level code zeroes out address bits and relies on `Mat.cpp` to model the TSVs used by predecoder outputs.

Key locations:

- `Mat.cpp:119-163`
- `Mat.cpp:169-173`
- `Mat.cpp:203-214`
- `Mat.cpp:287-302`
- `Mat.cpp:369-377`

The current fine-grained interpretation is:

- all predecoder outputs are counted into `totalPredecoderOutputBits`
- local TSVs are instantiated at mat level
- `tsvArray.numTotalBits = totalPredecoderOutputBits * redundancy`
- `tsvArray.numAccessBits = numTotalBits`
- predecoder latency gets an added TSV write-latency term
- mat power adds TSV energy proportional to `totalPredecoderOutputBits`

So in this implementation:

- bank-level global TSVs represent broadcast control/data-class traffic
- mat-level local TSVs represent decoded predecoder-output traffic

That is directionally close to DESTINY's fine-grained description, but several details still need auditing.

## Result Reporting Uses a Second TSV Formula Layer

`Result.cpp` does not simply print the already-aggregated TSV contribution from bank totals. It recomputes several TSV breakdown terms from primitive fields.

Key locations:

- `Result.cpp:340-349` area printing
- `Result.cpp:357-364` read TSV latency printing
- `Result.cpp:482-489` read TSV energy printing
- `Result.cpp:646-649` leakage printing

This means TSV accounting exists in two places:

1. in bank / mat aggregation logic
2. in reporting-time decomposition logic

This duplication is an audit risk because the printed TSV breakdown can drift from the real modeled contribution.

## What DESTINY Says the TSV Model Should Mean

From the DESTINY README:

- coarse granularity:
  address, control, and data signals are broadcast to all stacked dies and decoded on the destination die
- fine granularity:
  address signals are pre-decoded on a separate logic layer and the undecoded address signals are broadcast to all stacked dies
  control and data are still shared

From the DESTINY DATE 2015 paper:

- DESTINY uses coarse- and fine-grained TSV models from CACTI-3DD
- the TSV model may act as buffered or unbuffered
- coarse-grained model broadcasts undecoded row and column select signals to all layers
- fine-grained model broadcasts decoded row and column signals to all layers
- fine-grained assumes a dedicated logic layer for predecoder units
- both coarse and fine assume a simplistic equal bank folding scheme across layers

These statements give the main semantic contract for the audit.

## Differences and High-Priority Audit Targets

This section lists the places where the current implementation appears to differ from DESTINY's documented semantics, or where the mapping is ambiguous enough that it should be checked first.

### A. Buffered vs unbuffered TSV support exists in code, but runtime paths appear unbuffered-only

Evidence:

- `TSV.h:24` default `buffered = false`
- `Mat.cpp:171-172`
- `BankWithHtree.cpp:461-462`
- `BankWithoutHtree.cpp:219-220`

Why it matters:

The DESTINY paper explicitly says the TSV model may act as buffered or unbuffered. In the current runtime flow, all normal initialization sites call `Initialize(tsv_type)` without enabling buffering. That means the implementation may no longer expose the buffered/unbuffered modeling choice during actual exploration.

Audit question:

- Was unbuffered-only an intentional project simplification?
- If yes, is it documented?
- If not, where should the buffered choice enter the search space or config?

### B. Coarse-grained control-bit count is a hand-written simplification and even leaves the older formula commented out

Evidence:

- `BankWithHtree.cpp:565-567`
- `BankWithoutHtree.cpp:274-276`

Current code:

- old commented formula: `log2(stackedDieCount + 0.1)`
- active formula: `numControlBits = stackedDieCount`

Why it matters:

This is a classic audit hotspot. The code itself preserves evidence that the formula changed. The DESTINY documentation describes broadcast semantics, but does not directly justify this exact count. This should be checked against the original paper / technical report / CACTI-3DD source.

Audit question:

- Should control TSV count scale with stack depth linearly, logarithmically, or by selected control classes?

### C. Coarse-grained address/data counting collapses signal classes too aggressively

Evidence:

- `BankWithHtree.cpp:567-568`
- `BankWithoutHtree.cpp:276-277`

Current code:

- one address-bit formula from cache geometry
- `numDataBits = blockSize * 2`

Why it matters:

The DESTINY paper describes coarse-grained TSVs in terms of undecoded row / column select broadcasting and shared TSV buses. The current implementation reduces this to one geometry-derived address count plus `blockSize * 2`. That may still be a valid approximation, but it is much coarser than the wording in the paper.

Audit question:

- Is the current formula a faithful abstraction of the published model, or a later shortcut?
- Should row and column classes be separated?
- Should control / address / data use distinct read/write accounting classes?

### D. Fine-grained modeling in README and in the paper are not phrased the same way, and the code only partially reflects both

Evidence:

- README says undecoded address signals are broadcast to all stacked dies and pre-decoded on a logic layer
- DATE paper says decoded row and column signals are broadcast to all layers
- current code:
  - zeroes bank-level address count in fine-grained mode
  - adds `totalPredecoderOutputBits` TSVs at mat level

Relevant code:

- `BankWithHtree.cpp:570-577`
- `BankWithoutHtree.cpp:279-286`
- `Mat.cpp:119-163`
- `Mat.cpp:203-214`

Why it matters:

The code is trying to move address-like TSV traffic from bank-level undecoded signals to mat-level predecoder outputs. That is a plausible implementation of the paper's fine-grained semantics, but the README and paper use different wording. This is precisely the kind of place where an audit note should distinguish "semantic translation" from "formula mismatch".

Audit question:

- Is `totalPredecoderOutputBits` the right proxy for the published fine-grained model?
- Should bank-level fine-grained still include some undecoded address traffic?
- Are row and column decode outputs both represented correctly?

### E. Hop cost is modeled as worst-case only

Evidence:

- `BankWithHtree.cpp:721-735`
- `BankWithoutHtree.cpp:523-538`

Current code:

- always uses `(stackedDieCount - 1)` for read/write/reset/set/refresh aggregation

Why it matters:

The midterm report already calls TSV formulas out as a next-phase repair target. Worst-case-only routing cost is a modeling choice that can materially bias stack-depth comparisons. Even if it matches an original simplification, it should be made explicit during audit.

Audit question:

- Did original DESTINY intend worst-case only, or was average / expected communication ever discussed?
- Should the next repair stage add an optional average-hop mode rather than replacing worst-case outright?

### F. TSV reporting may be inconsistent with TSV accounting used in optimization

Evidence:

- bank area accumulation multiplies by `numTotalBits`
- coarse TSV area printing in `Result.cpp` prints `bank->tsvArray.area` directly

Relevant code:

- `BankWithHtree.cpp:576-580`
- `BankWithoutHtree.cpp:285-289`
- `Result.cpp:340-349`

Why it matters:

This suggests a possible unit-vs-total ambiguity. Even if total bank area is correct, the printed TSV area breakdown may not represent the same quantity.

Audit question:

- Does `tsvArray.area` represent one TSV or the total TSV bundle?
- If it is one TSV, should `Result.cpp` multiply by `numTotalBits` when printing coarse TSV area?

### G. Fine-grained read-energy reporting is explicitly marked as unfinished

Evidence:

- `Result.cpp:485-488`

Why it matters:

The code comment says `TODO: revisit this`. This should be treated as first-class audit evidence. If the reported TSV energy is later used in experiments or paper plots, this path must be reconciled with bank-level aggregation logic.

### H. Primitive TSV area model contains open TODOs and fixed heuristics

Evidence:

- `TSV.cpp:90`
- `TSV.cpp:104-115`

Why it matters:

These are weaker than the bank-level counting issues, but they matter if the audit reaches primitive calibration. They are better treated as second-stage model refinement after the counting semantics are validated.

## Recommended Audit Order

Do not start from "new TSV papers". Start from consistency checks.

### Stage 1. Freeze the semantic contract

Write down, side by side:

- README definition of coarse/fine
- DATE 2015 definition of coarse/fine
- current code interpretation

Goal:

- identify where the code is implementing a translation
- identify where the code is implementing a shortcut

### Stage 2. Audit the high-risk formulas

Check these first:

1. `numControlBits = stackedDieCount`
2. `numAddressBits = log2(capacity / blockSize / associativity / stackedDieCount)`
3. `numDataBits = blockSize * 2`
4. fine-grained `numAddressBits = 0`
5. `totalPredecoderOutputBits` as fine-grained local TSV count
6. `(stackedDieCount - 1)` as mandatory hop distance

For each item, record:

- code location
- current formula
- intended signal meaning
- DESTINY / CACTI-3DD source wording
- provisional judgment: consistent / ambiguous / inconsistent

### Stage 3. Check reporting consistency

Audit whether `Result.cpp` prints:

- the same quantity used in optimization
- a primitive TSV metric
- or a recomputed approximation

This matters because paper figures often rely on printed TSV breakdowns.

### Stage 4. Only then consider model upgrades

If Stage 1-3 confirm that the formulas are merely coarse but internally consistent, then the next step can be an upgrade such as:

- signal-class-aware TSV counting
- average-hop versus worst-hop option
- explicit separation of control / address / data classes
- calibrated buffered / unbuffered mode exposure

## Minimal Deliverables for the Next Pass

The next pass should ideally produce:

1. a table of TSV formulas and their intended meanings
2. a table of DESTINY-documented semantics versus current implementation
3. one small code patch that fixes the clearest inconsistency
4. one experiment sweep over 2 / 4 / 8 / 16 layers showing the before/after impact

## Bottom-Line Assessment

The current codebase does have a functioning TSV model, but it is not a single clean model. It is a combination of:

- technology-level TSV parasitic formulas
- primitive TSV delay/energy logic
- bank/mat-level counting heuristics
- result-time decomposition formulas

That is exactly why TSV repair should start with audit rather than immediate redesign.

The highest-priority audit targets are:

- signal counting semantics
- buffered vs unbuffered exposure
- worst-case hop assumption
- reporting consistency

Once those are checked, it will be much easier to justify any follow-up optimization as a real modeling improvement instead of an ad hoc rewrite.
