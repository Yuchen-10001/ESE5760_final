# Midterm Code Changes Detail

## 1. Strict Process-Node Validation

### Original code location

File: `main.cpp`

Current baseline behavior:

```cpp
Technology techHigh;
double alpha = 0;
if (inputParameter->processNode > 200){
    // TO-DO: technology node > 200 nm
} else if (inputParameter->processNode > 120) { // 120 nm < technology node <= 200 nm
    techHigh.Initialize(200, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 120.0) / 60;
} else if (inputParameter->processNode > 90) { // 90 nm < technology node <= 120 nm
    techHigh.Initialize(120, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 90.0) / 30;
} else if (inputParameter->processNode > 65) { // 65 nm < technology node <= 90 nm
    techHigh.Initialize(90, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 65.0) / 25;
} else if (inputParameter->processNode > 45) { // 45 nm < technology node <= 65 nm
    techHigh.Initialize(65, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 45.0) / 20;
} else if (inputParameter->processNode >= 32) { // 32 nm < technology node <= 45 nm
    techHigh.Initialize(45, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 32.0) / 13;
} else if (inputParameter->processNode >= 22) { // 22 nm < technology node <= 32 nm
    techHigh.Initialize(32, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 22.0) / 10;
} else {
    //TO-DO: technology node < 22 nm
}
```

### Midterm repair version

```cpp
Technology techHigh;
double alpha = 0;

if (inputParameter->processNode < 22 || inputParameter->processNode > 200) {
    cout << "[ERROR] Process node " << inputParameter->processNode
         << "nm is outside the supported DESTINY range of 22nm to 200nm." << endl;
    exit(-1);
}

if (inputParameter->processNode > 120) {
    techHigh.Initialize(200, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 120.0) / 60;
} else if (inputParameter->processNode > 90) {
    techHigh.Initialize(120, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 90.0) / 30;
} else if (inputParameter->processNode > 65) {
    techHigh.Initialize(90, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 65.0) / 25;
} else if (inputParameter->processNode > 45) {
    techHigh.Initialize(65, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 45.0) / 20;
} else if (inputParameter->processNode >= 32) {
    techHigh.Initialize(45, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 32.0) / 13;
} else {
    techHigh.Initialize(32, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 22.0) / 10;
}
```



The original code silently fell into incomplete branches for unsupported nodes below 22 nm or above 200 nm. The midterm fix turns that into an explicit fail-fast error.

## 2. Fail-Fast for Non-Power-of-Two Associativity

### Original code location

File: `main.cpp`

```cpp
if (!isPow2(inputParameter->associativity)) {
    cout << "[ERROR] The associativity value has to be a power of 2 in this version" << endl;
    //exit(-1);
}
```

### Midterm repair version

```cpp
if (!isPow2(inputParameter->associativity)) {
    cout << "[ERROR] The associativity value has to be a power of 2 in this version" << endl;
    exit(-1);
}
```



Without the terminating `exit(-1)`, the simulator prints an error but continues execution with invalid geometry assumptions.

## 3. Re-enable the Dedicated eDRAM Technology Path

### Original code location

File: `main.cpp`

```cpp
devtech = tech;

if (cell->memCellType == eDRAM && false) {
    devtech = new Technology();
    devtech->Initialize(inputParameter->processNode, EDRAM, inputParameter);
}

...

if (cell->memCellType == eDRAM && false) {
    delete devtech;
}
```

### Midterm repair version

```cpp
devtech = tech;

if (cell->memCellType == eDRAM) {
    devtech = new Technology();
    devtech->Initialize(inputParameter->processNode, EDRAM, inputParameter);
}

...

if (cell->memCellType == eDRAM) {
    delete devtech;
}
```



The hardcoded `&& false` disables the dedicated eDRAM path unconditionally, forcing eDRAM to use the generic device-technology flow instead.

## 4. Add Explicit `ReadEnergy` Support

### Original code location

File: `MemCell.h`

```cpp
double readVoltage;     /* Read voltage */
double readCurrent;     /* Read current */
double minSenseVoltage; /* Minimum sense voltage */
double wordlineBoostRatio;
double readPower;       /* Read power per bitline (uW)*/
```

File: `MemCell.cpp`

```cpp
if (!strncmp("-ReadPower", line, strlen("-ReadPower"))) {
    sscanf(line, "-ReadPower (uW): %lf", &readPower);
    readPower /= 1e6;
    continue;
}
```

There is no parser branch for:

```text
-ReadEnergy (pJ): ...
```

### Midterm repair version

File: `MemCell.h`

```cpp
double readVoltage;     /* Read voltage */
double readCurrent;     /* Read current */
double minSenseVoltage; /* Minimum sense voltage */
double wordlineBoostRatio;
double readPower;       /* Read power per bitline (W) */
double readEnergy;      /* Explicit read energy per cell (J) */
```

File: `MemCell.cpp`

```cpp
readPower = 0;
readEnergy = 0;
```

```cpp
if (!strncmp("-ReadPower", line, strlen("-ReadPower"))) {
    sscanf(line, "-ReadPower (uW): %lf", &readPower);
    readPower /= 1e6;
    continue;
}

if (!strncmp("-ReadEnergy", line, strlen("-ReadEnergy"))) {
    sscanf(line, "-ReadEnergy (pJ): %lf", &readEnergy);
    readEnergy /= 1e12;
    continue;
}
```


The bundled `sample_RRAM.cell` includes `-ReadEnergy (pJ): 0.1`, but the original parser ignores it completely.

### Ignoring `ReadEnergy` can produce a negative result

This point is especially important for the ReRAM example discussed in the midterm report.

In `config/sample_RRAM.cell`, the user explicitly provides:

```text
-ReadMode: current
-ReadVoltage (V): 0.3
-ReadEnergy (pJ): 0.1
-VoltageDropAccessDevice (V): 1.8
```

The intended behavior is straightforward:

- if explicit `ReadEnergy` is present, the simulator should use that positive user-specified energy value directly;
- it should not fall back to estimating read energy indirectly from a derived read-power formula.

However, in the original code, `ReadEnergy` is not parsed at all. As a result:

1. the explicit positive energy input (`0.1 pJ`) is silently discarded;
2. the simulator falls back to the `readPower == 0` path in `SubArray.cpp`;
3. that fallback calls `CalculateReadPower()` in `MemCell.cpp`;
4. the current-sensing branch then computes read current from:

```text
(readVoltage - voltageDropAccessDevice) / resistanceOn
```

For this bundled ReRAM case:

```text
readVoltage - voltageDropAccessDevice = 0.3 - 1.8 = -1.5 V
```

So the derived current becomes negative. Since the original code then computes read power as:

```text
readPower = Vdd * current
```

the derived read power also becomes negative. Finally, `SubArray.cpp` converts that negative power into read energy by multiplying by a positive sensing latency:

```text
cellReadEnergy = 2 * CalculateReadPower() * senseAmp.readLatency
```

Because the latency and scaling factors are positive, the negative sign is preserved all the way to the final reported quantity:

```text
Bitline & Cell Read Energy = -0.035 pJ
```

In short, the negative energy artifact appears because two issues interact:

- the simulator ignores the explicit positive `ReadEnergy` value provided by the user, and
- the fallback derived read-power formula allows a negative effective read voltage.

That is why the `ReadEnergy` repair is not just a parser convenience. It is part of the causal chain behind the negative result reported in the midterm.

## 5. Correct Read-Energy Selection Logic in the Subarray Path

### Original code location

File: `SubArray.cpp`

```cpp
if (cell->readPower == 0) 
    cellReadEnergy = 2 * cell->CalculateReadPower() * senseAmp.readLatency; /* x2 is because of the reference cell */
else
    cellReadEnergy = 2 * cell->readPower * senseAmp.readLatency;
cellReadEnergy *= numColumn / muxSenseAmp / muxOutputLev1 / muxOutputLev2;
```

### Midterm repair version

```cpp
if (cell->readEnergy > 0) {
    cellReadEnergy = 2 * cell->readEnergy;
} else if (cell->readPower > 0) {
    cellReadEnergy = 2 * cell->readPower * senseAmp.readLatency;
} else {
    cellReadEnergy = 2 * cell->CalculateReadPower() * senseAmp.readLatency;
}

cellReadEnergy *= numColumn / muxSenseAmp / muxOutputLev1 / muxOutputLev2;
```



The original logic only chooses between explicit `readPower` and derived `CalculateReadPower()`. It has no path for user-specified `readEnergy`.

## 6. Prevent Negative Derived Read Power

### Original code location

File: `MemCell.cpp`

```cpp
double MemCell::CalculateReadPower() { /* TO-DO consider charge pumped read voltage */
    if (readPower == 0) {
        if (cell->readMode) {   /* voltage-sensing */
            if (readVoltage == 0) { /* Current-in voltage sensing */
                return tech->vdd * readCurrent;
            }
            if (readCurrent == 0) { /*Voltage-divider sensing */
                double resInSerialForSenseAmp, maxBitlineCurrent;
                resInSerialForSenseAmp = sqrt(resistanceOn * resistanceOff);
                maxBitlineCurrent = (readVoltage - voltageDropAccessDevice) / (resistanceOn + resInSerialForSenseAmp);
                return tech->vdd * maxBitlineCurrent;
            }
        } else { /* current-sensing */
            double maxBitlineCurrent = (readVoltage - voltageDropAccessDevice) / resistanceOn;
            return tech->vdd * maxBitlineCurrent;
        }
    } else {
        return -1.0; /* should not call the function if read energy exists */
    }
    return -1.0;
}
```

### Midterm repair version

```cpp
double MemCell::CalculateReadPower() {
    if (readPower > 0) {
        return readPower;
    }

    if (readMode) { /* voltage-sensing */
        if (readVoltage == 0) {
            return tech->vdd * readCurrent;
        }

        if (readCurrent == 0) {
            double resInSerialForSenseAmp = sqrt(resistanceOn * resistanceOff);
            double effectiveReadVoltage = readVoltage - voltageDropAccessDevice;
            if (effectiveReadVoltage < 0) {
                effectiveReadVoltage = 0;
            }
            double maxBitlineCurrent = effectiveReadVoltage / (resistanceOn + resInSerialForSenseAmp);
            return tech->vdd * maxBitlineCurrent;
        }
    } else { /* current-sensing */
        double effectiveReadVoltage = readVoltage - voltageDropAccessDevice;
        if (effectiveReadVoltage < 0) {
            effectiveReadVoltage = 0;
        }
        double maxBitlineCurrent = effectiveReadVoltage / resistanceOn;
        return tech->vdd * maxBitlineCurrent;
    }

    return 0;
}
```



For `sample_RRAM.cell`, the original current-sensing path computes:

```text
(0.3 - 1.8) / resistanceOn
```

which is negative. That negative current becomes negative read power, and then negative read energy.

This repair also replaces `cell->readMode` with the object field `readMode`, which is cleaner and avoids dependence on a global pointer.

## 7. Fix the `SetVoltage` Parser Copy/Paste Bug

### Original code location

File: `MemCell.cpp`

```cpp
if (!strncmp("-SetVoltage", line, strlen("-SetVoltage"))) {
    sscanf(line, "-ResetVoltage (V): %s", tmp);
    if (!strcmp(tmp, "vdd"))
        resetVoltage = tech->vdd;
    else
        sscanf(line, "-SetVoltage (V): %lf", &setVoltage);
    continue;
}
```

### Midterm repair version

```cpp
if (!strncmp("-SetVoltage", line, strlen("-SetVoltage"))) {
    sscanf(line, "-SetVoltage (V): %s", tmp);
    if (!strcmp(tmp, "vdd"))
        setVoltage = tech->vdd;
    else
        sscanf(line, "-SetVoltage (V): %lf", &setVoltage);
    continue;
}
```



The original code reuses the `-ResetVoltage` format string and even writes to `resetVoltage` when parsing `SetVoltage = vdd`.

## 8. Accept Both `AllowDifferentTagTech` and `AllowDifferenceTagTech`

### Original code location

The README uses:

```text
-AllowDifferenceTagTech
```

but the parser only accepts:

```cpp
if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech"))) {
    sscanf(line, "-AllowDifferentTagTech: %s", tmp);
    if (!strcmp(tmp, "true"))
        allowDifferentTagTech = true;
    else
        allowDifferentTagTech = false;
    continue;
}
```

### Midterm repair version

File: `InputParameter.cpp`

```cpp
if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech")) ||
    !strncmp("-AllowDifferenceTagTech", line, strlen("-AllowDifferenceTagTech"))) {
    if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech")))
        sscanf(line, "-AllowDifferentTagTech: %s", tmp);
    else
        sscanf(line, "-AllowDifferenceTagTech: %s", tmp);

    if (!strcmp(tmp, "true"))
        allowDifferentTagTech = true;
    else
        allowDifferentTagTech = false;
    continue;
}
```



This is a documentation-versus-implementation mismatch. Users following the README can otherwise provide a valid-looking parameter name that the parser simply ignores.
