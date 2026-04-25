# Detailed Response to Midterm Follow-up Questions

This note directly addresses the two follow-up questions:

1. Were we using the original version of DESTINY?
2. What are concrete example configurations that yielded the negative results?

## 1. Confirmation of Progress and Baseline

Yes. In our midterm report, the "before repair" results refer to the original DESTINY baseline before our local fixes.

More precisely:

- The modeling framework we started from is the public C++ DESTINY codebase referenced in the report.
- Our workflow at the midterm stage was:
  - run the original baseline behavior,
  - identify incorrect or physically inconsistent outputs,
  - implement targeted fixes locally,
  - compare the repaired behavior against the original baseline.
- Therefore, when the report says "original code" and presents "Before Repair" versus "After Repair", the negative result belongs to the original DESTINY behavior prior to our modifications.

This is already reflected in the midterm report:

- `Doc/Midterm_Progress_Report_ESE5760.tex`
  - lines 137-145 describe the original read-current expression and explain why it can become negative,
  - lines 237-258 present the "Before Repair" and "After Repair" comparison for the ReRAM case.

## 2. Example Configuration Yielding the Negative Result

The clearest example is the bundled 3D ReRAM sample:

- Configuration file: `config/sample_3DReRAM.cfg`
- Memory-cell file referenced by that configuration: `config/sample_RRAM.cell`

### 2.1 Command Used

The configuration is run from the `config` directory:

```bash
..\destiny.exe sample_3DReRAM.cfg
```

This is also the command documented in the midterm report.

### 2.2 Relevant Configuration Parameters

From `config/sample_3DReRAM.cfg`:

- `-DesignTarget: RAM`
- `-ProcessNode: 180`
- `-MemoryCellInputFile: sample_RRAM.cell`
- `-OptimizationTarget: WriteEDP`
- `-StackedDieCount: 1`
- `-MonolithicStackCount: 2`

From `config/sample_RRAM.cell`:

- `-MemCellType: memristor`
- `-ReadMode: current`
- `-ReadVoltage (V): 0.3`
- `-ReadEnergy (pJ): 0.1`
- `-AccessType: diode`
- `-VoltageDropAccessDevice (V): 1.8`
- `-ResistanceOnAtReadVoltage (ohm): 1000000`

### 2.3 Why This Configuration Produces a Negative Result in the Original Code

The midterm report identifies the original read-current path as:

```text
(readVoltage - voltageDropAccessDevice) / resistanceOn
```

For this bundled ReRAM case:

- `readVoltage = 0.3 V`
- `voltageDropAccessDevice = 1.8 V`

So the effective voltage term becomes:

```text
0.3 - 1.8 = -1.5 V
```

That makes the derived current negative, which then propagates into negative read power and finally a negative read-energy contribution.

## 3. Observed Negative Output

For the bundled ReRAM sample above, the midterm report records the following "Before Repair" result:

- `Read Dynamic Energy = 150.509 pJ`
- `Bitline & Cell Read Energy = -0.035 pJ`

This is the negative numeric result we were referring to in the report.

In other words, the problematic output is not just "poor performance" or a failed run. It is a physically impossible negative energy term in the read-energy breakdown.

## 4. Interpretation of "Negative Results"

To avoid ambiguity, our use of "negative results" in this context means:

- a reported energy component becoming numerically negative,
- specifically the read-side `Bitline & Cell Read Energy` term,
- not merely a test that failed or an invalid-input error message.

This distinction matters because the project goal is correctness and physical consistency of the model. A negative energy contribution is a modeling defect, not just an inconvenient output.

## 5. Additional Clarification About Other Validation Cases

The midterm report also includes:

- an invalid process-node stress test, and
- an invalid associativity stress test.

Those are useful validation cases, but they are not the same as the "negative results" issue above:

- `test_invalid_node.cfg` is intended to trigger a fail-fast error for unsupported process nodes,
- `test_invalid_assoc.cfg` is intended to trigger a fail-fast error for illegal associativity,
- neither of those is the source of the negative energy artifact.

The negative numeric artifact is specifically demonstrated by the bundled ReRAM configuration:

- `sample_3DReRAM.cfg` plus `sample_RRAM.cell`

## 6. Direct Answer Version

If a concise reply is needed, the answer can be stated as follows:

> Yes. The negative result reported in our midterm came from the original DESTINY behavior before our local fixes. A concrete example is the bundled configuration `sample_3DReRAM.cfg`, which uses `sample_RRAM.cell`. In that cell file, `ReadVoltage = 0.3 V` and `VoltageDropAccessDevice = 1.8 V`, so the original read-current path produced a negative effective voltage and therefore a negative read-energy term. The reported negative output was `Bitline & Cell Read Energy = -0.035 pJ`.

## 7. Suggested Short Email Reply

Dear [Instructor Name],

Yes, the negative result discussed in our midterm report was observed from the original DESTINY behavior before our local fixes.

A concrete example is the bundled configuration `sample_3DReRAM.cfg`, which uses `sample_RRAM.cell`. In that case, the relevant parameters are `ReadMode = current`, `ReadVoltage = 0.3 V`, and `VoltageDropAccessDevice = 1.8 V`. Under the original read-current path, this produces a negative effective read voltage, which leads to a negative read-energy artifact. The specific negative output reported in our midterm was:

- `Read Dynamic Energy = 150.509 pJ`
- `Bitline & Cell Read Energy = -0.035 pJ`

We are happy to provide the full configuration excerpts and logs if helpful.

Best regards,
[Your Names]
